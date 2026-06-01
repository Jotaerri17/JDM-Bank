import requests
from database.database import obter_conexao
from datetime import datetime
from visualizacoes.visualizacoes import exibir_carteira_investimentos

def obter_cotacao_moeda(moeda):
    """
    Busca a cotação atual de uma moeda em relação ao Real usando a AwesomeAPI.
    Exemplo de 'moeda': 'BTC-BRL' (Bitcoin).
    """
    try:
        url = f"https://economia.awesomeapi.com.br/last/{moeda}"
        response = requests.get(url, timeout=5)
        dados = response.json()
        
        chave = moeda.replace("-", "")
        cotacao_atual = float(dados[chave]["bid"])
        return cotacao_atual
    except Exception as e:
        print(f"⚠️ Erro ao buscar cotação do Bitcoin: {e}")
        return None

def obter_taxa_selic():
    """
    Busca a Taxa Selic Meta atualizada diretamente da API oficial do Banco Central (SGS - Série 432).
    """
    try:
        url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados/ultimos/1?formato=json"
        response = requests.get(url, timeout=5)
        dados = response.json()
        # A API retorna uma lista com o dicionário contendo a data e o valor (ex: "10.50")
        return float(dados[0]["valor"])
    except Exception as e:
        print(f"⚠️ Erro ao buscar Taxa Selic na API do Banco Central: {e}")
        # Valor padrão de segurança caso a API do Banco Central esteja fora do ar temporariamente
        return 10.50 

def investir(usuario_id, investimento_id, valor_reais):
    """
    Realiza a aplicação do saldo do usuário em um investimento específico,
    salvando as taxas/cotações reais do momento da compra.
    """
    if valor_reais <= 0:
        print("❌ O valor do investimento deve ser maior que zero.")
        return False

    conexao = obter_conexao()
    if not conexao:
        return False

    cursor = conexao.cursor()

    try:
        # 1. Verifica saldo do usuário
        cursor.execute("SELECT saldo FROM usuarios WHERE id = %s", (usuario_id,))
        resultado = cursor.fetchone()
        
        if not resultado:
            print("❌ Erro: Usuário não encontrado.")
            return False
            
        saldo_atual = float(resultado[0])
        if saldo_atual < valor_reais:
            print(f"❌ Erro: Saldo insuficiente. Seu saldo é R$ {saldo_atual:.2f}")
            return False

        # 2. Verifica qual é o investimento selecionado
        cursor.execute("SELECT nome FROM tipos_investimento WHERE id = %s", (investimento_id,))
        tipo_inv = cursor.fetchone()
        
        if not tipo_inv:
            print("❌ Erro: Tipo de investimento inválido ou não cadastrado.")
            return False
            
        nome_investimento = tipo_inv[0].upper()
        
        # Valor padrão para investimentos sem variação cambial direta
        cotacao_compra = 1.00 

        # 3. Regras Específicas por Ativo
        if 'BITCOIN' in nome_investimento or 'BTC' in nome_investimento:
            print("🌐 Conectando à AwesomeAPI... Buscando cotação do Bitcoin...")
            cotacao_compra = obter_cotacao_moeda('BTC-BRL')
            if not cotacao_compra:
                print("❌ Operação cancelada: Não foi possível cotar o Bitcoin.")
                return False
            
            fracao_comprada = valor_reais / cotacao_compra
            print(f"🪙 Cotação Atual BTC: R$ {cotacao_compra:,.2f}")
            print(f"📊 Com R$ {valor_reais:.2f} você está adquirindo: {fracao_comprada:.7f} BTC")

        elif 'CDB' in nome_investimento:
            print("🌐 Conectando ao Banco Central... Buscando Taxa Selic Meta...")
            cotacao_compra = obter_taxa_selic()
            print(f"📈 Taxa Selic capturada: {cotacao_compra}% ao ano.")
            print(f"🔒 Seu rendimento foi travado nesta taxa a partir de hoje!")

        elif 'FUNDO' in nome_investimento or 'FII' in nome_investimento:
            # Mantendo suporte para FII com uma taxa fictícia de dividendo fixo simulado
            cotacao_compra = 9.50 
            print(f"🏢 Investindo em Fundos Imobiliários (Rendimento estimado: {cotacao_compra}% a.a.)")

        # 4. Deduz o valor do saldo do usuário
        cursor.execute("UPDATE usuarios SET saldo = saldo - %s WHERE id = %s", (valor_reais, usuario_id))

        # 5. Registra o investimento na carteira do usuário (salvando a taxa em cotacao_compra)
        cursor.execute("""
            INSERT INTO investimentos_usuarios (usuario_id, investimento_id, valor_investido, cotacao_compra)
            VALUES (%s, %s, %s, %s)
        """, (usuario_id, investimento_id, valor_reais, cotacao_compra))

        # 6. Registra no extrato (Movimentações)
        cursor.execute("""
            INSERT INTO movimentacoes (usuario_id, tipo, valor)
            VALUES (%s, %s, %s)
        """, (usuario_id, f"INVESTIMENTO_{nome_investimento.replace(' ', '_')}", valor_reais))

        # Confirma a transação no banco de forma segura
        conexao.commit()
        print(f"✅ Sucesso! Você investiu R$ {valor_reais:.2f} em {nome_investimento}.")
        return True

    except Exception as e:
        conexao.rollback()
        print(f"❌ Erro ao processar investimento: {e}")
        return False
    finally:
        cursor.close()
        conexao.close()

def resgatar_investimento(usuario_id):
    """
    Lista a carteira do usuário automaticamente e processa o resgate pelo ID escolhido.
    """
    # MELHORIA: Mostra a carteira do usuário logo de cara para ele ver os IDs disponíveis
    print("\n--- SUA CARTEIRA DE INVESTIMENTOS ATIVA ---")
    exibir_carteira_investimentos(usuario_id)
    
    try:
        investimento_usuario_id = int(input("\nDigite o ID do investimento que deseja resgatar/vender: "))
    except ValueError:
        print("❌ Erro: O ID deve ser um número inteiro.")
        return False

    conexao = obter_conexao()
    if not conexao:
        return False

    cursor = conexao.cursor()

    try:
        # QUERY CORRIGIDA: trazendo 'investimento_id' para fazer o JOIN perfeito com o Neon
        query = """
            SELECT iu.valor_investido, iu.cotacao_compra, iu.data_aplicacao, ti.nome
            FROM investimentos_usuarios iu
            JOIN tipos_investimento ti ON iu.investimento_id = ti.id
            WHERE iu.id = %s AND iu.usuario_id = %s
        """
        cursor.execute(query, (investimento_usuario_id, usuario_id))
        investimento = cursor.fetchone()

        if not investimento:
            print("❌ Erro: Investimento não encontrado ou não pertence a você.")
            print("💡 Dica: Verifique no topo da tela o número que aparece na coluna 'ID'.")
            return False

        valor_investido = float(investimento[0])
        cotacao_compra = float(investimento[1])
        data_aplicacao = investimento[2]
        nome_produto = investimento[3].upper()

        # Calcula a quantidade de dias passados desde a aplicação
        dias_passados = (datetime.now() - data_aplicacao).days
        if dias_passados < 0: 
            dias_passados = 0

        valor_atualizado = valor_investido
        detalhe_calculo = ""

        # Executa o cálculo matemático baseado no tipo de ativo
        if 'BITCOIN' in nome_produto or 'BTC' in nome_produto:
            print("\n🌐 Conectando à AwesomeAPI para buscar cotação atual do Bitcoin...")
            from investimento.investimento import obter_cotacao_moeda
            cotacao_atual = obter_cotacao_moeda('BTC-BRL')
            if not cotacao_atual:
                print("❌ Operação cancelada: Não foi possível obter a cotação atual do BTC.")
                return False
            
            fracao_btc = valor_investido / cotacao_compra
            valor_atualizado = fracao_btc * cotacao_atual
            
            detalhe_calculo = (
                f"🪙 Cotação de Compra: R$ {cotacao_compra:,.2f}\n"
                f"📈 Cotação Atual:     R$ {cotacao_atual:,.2f}\n"
                f"📊 Fração Detida:     {fracao_btc:.7f} BTC"
            )

        elif 'CDB' in nome_produto or 'FUNDO' in nome_produto or 'FII' in nome_produto:
            taxa_anual = cotacao_compra
            taxa_diaria = (1 + (taxa_anual / 100)) ** (1 / 365) - 1
            valor_atualizado = valor_investido * ((1 + taxa_diaria) ** dias_passados)
            
            detalhe_calculo = (
                f"📈 Taxa Contratada:   {taxa_anual}% ao ano\n"
                f"🗓️ Tempo de Aplicação: {dias_passados} dias decorridos"
            )

        lucro_prejuizo = valor_atualizado - valor_investido
        
        print("\n" + "="*50)
        print("汇 PAINEL DE FECHAMENTO DE INVESTIMENTO 汇")
        print("="*50)
        print(f"Produto:               {nome_produto}")
        print(f"Valor Investido:       R$ {valor_investido:.2f}")
        print(detalhe_calculo)
        print("-"*50)
        print(f"Valor de Resgate:      R$ {valor_atualizado:.2f}")
        
        if lucro_prejuizo > 0:
            print(f"🟢 Resultado Operacional: +R$ {lucro_prejuizo:.2f} (LUCRO)")
        elif lucro_prejuizo < 0:
            print(f"🔴 Resultado Operacional: -R$ {abs(lucro_prejuizo):.2f} (PREJUÍZO)")
        else:
            print("🟡 Resultado Operacional: R$ 0.00 (SEM VARIAÇÃO)")
        print("="*50)

        confirmar = input("Confirmar resgate total do dinheiro para o seu saldo? (S/N): ").upper()
        if confirmar != 'S':
            print("❌ Operação cancelada pelo usuário.")
            return False

        # Transação no Banco de Dados
        cursor.execute("UPDATE usuarios SET saldo = saldo + %s WHERE id = %s", (valor_atualizado, usuario_id))
        cursor.execute("DELETE FROM investimentos_usuarios WHERE id = %s", (investimento_usuario_id,))
        cursor.execute("""
            INSERT INTO movimentacoes (usuario_id, tipo, valor)
            VALUES (%s, %s, %s)
        """, (usuario_id, f"RESGATE_{nome_produto.replace(' ', '_')}", valor_atualizado))

        conexao.commit()
        print("\n✅ Resgate concluído com sucesso! Seu saldo foi atualizado.")
        return True

    except Exception as e:
        conexao.rollback()
        print(f"❌ Erro crítico ao processar resgate: {e}")
        return False
    finally:
        cursor.close()
        conexao.close()