import sys
from database.database import obter_conexao
from transferencias.transferencias import realizar_deposito, realizar_transferencia
# Importações atualizadas com as novas validações
from auth.auth import criar_usuario, autenticar_usuario, validar_cpf, validar_senha, validar_email, validar_nome
from investimento.investimento import investir
from visualizacoes.visualizacoes import exibir_saldo, exibir_extrato, exibir_carteira_investimentos

def sincronizar_saldo_sessao(usuario_id):
    conexao = obter_conexao()
    if not conexao: return 0.0
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
    while True:
        usuario['saldo'] = sincronizar_saldo_sessao(usuario['id'])
        print("\n" + "="*40)
        print(f" 👤 {usuario['nome']} | Saldo Atual: R$ {usuario['saldo']:.2f} ")
        print("="*40)
        print("1. Fazer Depósito\n2. Fazer Transferência por E-mail\n3. Executar Investimento\n4. Ver Extrato\n5. Ver Carteira\n6. Resgatar Investimento\n7. Sair da Conta (Logout)")
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
            print("\n--- MERCADO DE INVESTIMENTOS ---\n1 - CDB | 2 - FII | 3 - BITCOIN")
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
        elif opcao == '6':
            from investimento.investimento import resgatar_investimento
            resgatar_investimento(usuario['id'])
        elif opcao == '7':
            print("🔒 Sessão encerrada de forma segura.")
            break
        else:
            print("❌ Opção inválida.")

def app():
    while True:
        print("\n" + "="*40 + "\n🏦 JDM BANK OPERATIONAL TERMINAL\n" + "="*40)
        print("1. Entrar na Conta (Login)\n2. Abrir Nova Conta\n3. Encerrar Sistema")
        print("="*40)
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            print("\n--- AUTENTICAÇÃO ---")
            cpf = input("CPF: ")
            senha = input("Senha: ")
            usuario_logado = autenticar_usuario(cpf, senha)
            if usuario_logado:
                print(f"✅ Autenticação bem-sucedida.")
                menu_logado(usuario_logado) 
            else:
                print("\n❌ Falha no login: CPF ou Senha incorretos.")

        elif opcao == '2':
            print("\n--- FORMULÁRIO DE CADASTRO ---")
            
            # Validação imediata do Nome
            while True:
                nome = input("Nome Completo: ")
                if validar_nome(nome): break
                print("❌ Erro: Insira seu nome e sobrenome (apenas letras).")

            # Validação imediata do E-mail
            while True:
                email = input("E-mail Único: ")
                if validar_email(email): break
                print("❌ Erro: Formato de e-mail inválido (exemplo@dominio.com).")
            
            # Validação imediata do CPF
            while True:
                cpf = input("CPF (apenas números): ")
                if validar_cpf(cpf): break
                print("❌ Erro: CPF inválido. Digite novamente.")

            telefone = input("Telefone/Celular: ")
            
            try:
                idade = int(input("Idade: "))
                if idade < 18:
                    print("❌ Erro: Cadastro permitido apenas para maiores de 18 anos.")
                    continue
                
                # Validação imediata da Senha
                while True:
                    senha = input("Defina sua Senha: ")
                    if validar_senha(senha): break
                    print("❌ Erro: Senha fraca. Exigido: mínimo 8 caracteres, contendo letra maiúscula, minúscula, número e caractere especial.")

                # Executa a criação no banco somente após passar pelas validações locais
                criar_usuario(nome, email, cpf, senha, telefone, idade)
                
            except ValueError:
                print("❌ Erro: Idade inválida.")

        elif opcao == '3':
            print("Desligando terminais e conexões...")
            sys.exit()

if __name__ == "__main__":
    app()