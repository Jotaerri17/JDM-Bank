
import requests
from database import obter_conexao

def obter_cotacao_moeda(moeda):
    """
    Busca a cotação atual de uma moeda em relação ao Real usando a AwesomeAPI.
    Exemplo de 'moeda': 'USD-BRL' (Dólar) ou 'BTC-BRL' (Bitcoin).
    """
    try:
        url = f"https://economia.awesomeapi.com.br/last/{moeda}"
        response = requests.get(url)
        dados = response.json()
        
      
        chave = moeda.replace("-", "")
        cotacao_atual = float(dados[chave]["bid"])
        return cotacao_atual
    except Exception as e:
        print(f"Erro ao buscar cotação: {e}")
        return None

def investir(usuario_id, investimento_id, valor_reais):
    """
    Realiza a aplicação do saldo do usuário em um investimento específico.
    """
    if valor_reais <= 0:
        print("O valor do investimento deve ser maior que zero.")
        return False

    conexao = obter_conexao()
    if not conexao:
        return False

    cursor = conexao.cursor()

    try:
        #  Verifica saldo do usuário
        cursor.execute("SELECT saldo FROM usuarios WHERE id = %s", (usuario_id,))
        resultado = cursor.fetchone()
        
        if not resultado or resultado[0] < valor_reais:
            print("Erro: Saldo insuficiente para este investimento.")
            return False

        # Verifica qual é o investimento (CDB, FII, BTC)
        cursor.execute("SELECT nome FROM tipos_investimento WHERE id = %s", (investimento_id,))
        tipo_inv = cursor.fetchone()
        
        if not tipo_inv:
            print("Erro: Tipo de investimento não encontrado.")
            return False
            
        nome_investimento = tipo_inv[0].upper()
        cotacao_compra = 1.00

        # Se for Bitcoin, precisamos pegar a cotação
        if nome_investimento == 'BITCOIN' or nome_investimento == 'BTC':
            print("Buscando cotação atual do Bitcoin...")
            cotacao_compra = obter_cotacao_moeda('BTC-BRL')
            if not cotacao_compra:
                print("Operação cancelada: Falha ao obter cotação.")
                return False
            print(f"Cotação do BTC hoje: R$ {cotacao_compra:,.2f}")

        # Deduz o valor do saldo do usuário
        cursor.execute("UPDATE usuarios SET saldo = saldo - %s WHERE id = %s", (valor_reais, usuario_id))

        #  Registra o investimento na carteira do usuário
        cursor.execute("""
            INSERT INTO investimentos_usuarios (usuario_id, investimento_id, valor_investido, cotacao_compra)
            VALUES (%s, %s, %s, %s)
        """, (usuario_id, investimento_id, valor_reais, cotacao_compra))

        #  Registra no extrato (Movimentações)
        cursor.execute("""
            INSERT INTO movimentacoes (usuario_id, tipo, valor)
            VALUES (%s, %s, %s)
        """, (usuario_id, f"INVESTIMENTO_{nome_investimento}", valor_reais))

        # Confirma a transação no banco
        conexao.commit()
        print(f"Sucesso! Você investiu R$ {valor_reais:.2f} em {nome_investimento}.")
        return True

    except Exception as e:
        conexao.rollback()
        print(f"Erro ao processar investimento: {e}")
        return False
    finally:
        cursor.close()
        conexao.close()