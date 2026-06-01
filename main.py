import sys
from database.database import obter_conexao
from transferencias.transferencias import realizar_deposito, realizar_transferencia
from auth.auth import criar_usuario, autenticar_usuario

# Mapeamento do diretório/arquivo correto para o terminal achar o script
from investimento.investimento import investir



# Centralização das consultas de leitura no módulo de visualizações
from visualizacoes.visualizacoes import exibir_saldo, exibir_extrato, exibir_carteira_investimentos

def sincronizar_saldo_sessao(usuario_id):
    """Consulta o banco e traz o saldo correto atualizado em tempo real."""
    conexao = obter_conexao()
    if not conexao: 
        return 0.0
    cursor = conexao.cursor()
    try:
        cursor.execute("SELECT saldo FROM usuarios WHERE id = %s", (usuario_id,))
        resultado = cursor.fetchone()
        return float(resultado[0]) if resultado else 0.0
    except Exception as e:
        print(f"❌ Erro ao sincronizar saldo: {e}")
        return 0.0
    finally:
        cursor.close()
        conexao.close()

def menu_logado(usuario):
    """Menu interno do usuário autenticado."""
    while True:
        # Força a atualização do saldo a cada renderização do menu
        usuario['saldo'] = sincronizar_saldo_sessao(usuario['id'])
        
        print("\n" + "="*40)
        print(f" 👤 {usuario['nome']} | Saldo Atual: R$ {usuario['saldo']:.2f} ")
        print("="*40)
        print("1. Fazer Depósito")
        print("2. Fazer Transferência por E-mail")
        print("3. Executar Investimento")
        print("4. Ver Extrato de Movimentações")
        print("5. Ver Carteira de Investimentos")
        print("6. Resgatar/Vender Investimento")
        print("7. Sair da Conta (Logout)")
        print("="*40)
        
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            try:
                valor = float(input("Digite o valor para depositar: R$ "))
                realizar_deposito(usuario['id'], valor)
            except ValueError:
                print("❌ Entrada inválida. Use apenas números.")

        elif opcao == '2':
            email_destino = input("E-mail do destinatário: ")
            try:
                valor = float(input("Valor da transferência: R$ "))
                realizar_transferencia(usuario['id'], email_destino, valor)
            except ValueError:
                print("❌ Entrada inválida. Use apenas números.")

        elif opcao == '3':
            print("\n--- MERCADO DE INVESTIMENTOS ---")
            print("1 - CDB (Pós-Fixado) | 2 - FII (Fundos Imobiliários) | 3 - BITCOIN")
            try:
                id_inv = int(input("Escolha o ID do ativo: "))
                valor = float(input("Valor a investir: R$ "))
                investir(usuario['id'], id_inv, valor)
            except ValueError:
                print("❌ Dados incorretos inseridos.")

        elif opcao == '4':
            exibir_saldo(usuario['id'])
            exibir_extrato(usuario['id'])

        elif opcao == '5':
            exibir_carteira_investimentos(usuario['id'])

        # Exemplo de lógica para encaixar no seu menu_logado ou menu de investimentos no main.py:

        elif opcao == '6':
            print("\n--- RESGATE DE INVESTIMENTOS ---")
            from investimento.investimento import resgatar_investimento
            # Agora só passamos o ID do usuário conectado, a função faz o resto!
            resgatar_investimento(usuario['id'])

        elif opcao == '7':
            print("🔒 Sessão encerrada de forma segura.")
            break
        else:
            print("❌ Opção inválida.")

def app():
    """Menu Inicial Deslogado."""
    while True:
        print("\n" + "="*40)
        print("🏦 JDM BANK OPERATIONAL TERMINAL")
        print("="*40)
        print("1. Entrar na Conta (Login)")
        print("2. Abrir Nova Conta")
        print("3. Encerrar Sistema")
        print("="*40)
        
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            print("\n--- AUTENTICAÇÃO ---")
            cpf = input("CPF: ")
            senha = input("Senha: ")
            
            print("Processando credenciais...")
            usuario_logado = autenticar_usuario(cpf, senha)
            
            if usuario_logado:
                print(f"✅ Autenticação bem-sucedida.")
                menu_logado(usuario_logado) 
            else:
                print("\n❌ Falha no login: CPF ou Senha incorretos.")

        elif opcao == '2':
            print("\n--- FORMULÁRIO DE CADASTRO ---")
            nome = input("Nome Completo: ")
            email = input("E-mail Único: ")
            cpf = input("CPF (apenas números): ")
            telefone = input("Telefone/Celular: ")
            try:
                idade = int(input("Idade: "))
                senha = input("Defina sua Senha: ")
                criar_usuario(nome, email, cpf, senha, telefone, idade)
            except ValueError:
                print("❌ Erro: Idade deve conter apenas números inteiros.")

        elif opcao == '3':
            print("Desligando terminais e conexões...")
            sys.exit()

if __name__ == "__main__":
    app()