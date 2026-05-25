import sys
from service import criar_usuario, realizar_transferencia, autenticar_usuario, realizar_deposito
from investimentos import investir

def menu_logado(usuario):
    """Menu que aparece apenas quando o usuário entra na conta."""
    while True:
        print("\n" + "="*40)
        print(f" Olá, {usuario['nome']}! | Saldo: R$ {usuario['saldo']:.2f} ")
        print("="*40)
        print("1. Fazer Depósito")
        print("2. Fazer Transferência (PIX)")
        print("3. Área de Investimentos")
        print("4. Atualizar Saldo")
        print("5. Sair da Conta (Logout)")
        print("="*40)
        
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            valor = float(input("Digite o valor para depositar: R$ "))
            if realizar_deposito(usuario['id'], valor):
                usuario['saldo'] += valor # Atualiza o saldo na tela

        elif opcao == '2':
            email_destino = input("E-mail de quem vai receber: ")
            valor = float(input("Valor da transferência: R$ "))
            # Passamos o ID direto da sessão, sem perguntar!
            if realizar_transferencia(usuario['id'], email_destino, valor):
                usuario['saldo'] -= valor # Atualiza o saldo na tela

        elif opcao == '3':
            print("\n--- INVESTIMENTOS ---")
            print("1 - CDB | 2 - FII | 3 - BITCOIN")
            id_inv = int(input("Número do investimento: "))
            valor = float(input("Valor: R$ "))
            if investir(usuario['id'], id_inv, valor):
                usuario['saldo'] -= valor

        elif opcao == '4':
            print("Atualizando dados...")
            # Para atualizar, poderíamos fazer um SELECT no banco, mas por ora re-autenticamos
            print("Saia e entre novamente para ver o extrato completo (Em breve!).")

        elif opcao == '5':
            print("Fazendo logout...")
            break # Quebra este loop e volta para o menu deslogado

        else:
            print("Opção inválida.")

def app():
    """Menu Inicial (Deslogado)"""
    while True:
        print("\n" + "="*40)
        print("🏦 JDM BANK - ACESSO 🏦")
        print("="*40)
        print("1. Entrar na Conta (Login)")
        print("2. Abrir Nova Conta")
        print("3. Encerrar")
        print("="*40)
        
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            print("\n--- LOGIN ---")
            email = input("E-mail: ")
            cpf = input("CPF: ")
            
            print("Autenticando...")
            usuario_logado = autenticar_usuario(email, cpf)
            
            if usuario_logado:
                print(f"\nLogin efetuado com sucesso!")
                # Chama o menu interno passando os dados do usuário
                menu_logado(usuario_logado) 
            else:
                print("\n❌ Acesso negado: E-mail ou CPF incorretos.")

        elif opcao == '2':
            print("\n--- ABERTURA DE CONTA ---")
            nome = input("Seu Nome: ")
            email = input("Seu E-mail: ")
            cpf = input("Seu CPF (apenas números): ")
            telefone = input("Seu Telefone: ")
            idade = int(input("Sua Idade: "))
            
            criar_usuario(nome, email, cpf, telefone, idade)

        elif opcao == '3':
            print("Encerrando o sistema...")
            sys.exit()

if __name__ == "__main__":
    app()