import sys
import time
import threading
from datetime import datetime
from database.database import obter_conexao
from transferencias.transferencias import realizar_deposito, realizar_transferencia
from auth.auth import criar_usuario, autenticar_usuario, validar_cpf, validar_senha, validar_email, validar_nome, validar_telefone
from investimento.investimento import investir
from visualizacoes.visualizacoes import exibir_saldo, exibir_extrato, exibir_carteira_investimentos



def _animacao_loading(stop_event, texto):

    frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
    idx = 0
    while not stop_event.is_set():
        
        sys.stdout.write(f"\r  {frames[idx]}  {texto}...")
        sys.stdout.flush()
        idx = (idx + 1) % len(frames)
        time.sleep(0.08)
    
    sys.stdout.write("\r" + " " * (len(texto) + 15) + "\r")
    sys.stdout.flush()

def jdm_loading(texto="Processando operação JDM", duracao_fixa=None):
    
    class LoadingContext:
        def __init__(self, texto):
            self.texto = texto
            self.stop_event = threading.Event()
            self.thread = threading.Thread(target=_animacao_loading, args=(self.stop_event, self.texto))

        def __enter__(self):
            self.thread.start()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.stop_event.set()
            self.thread.join()

    if duracao_fixa:
       
        with LoadingContext(texto):
            time.sleep(duracao_fixa)
    else:
        
        return LoadingContext(texto)
    





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
        horario_atual = datetime.now().strftime("%H:%M:%S")

        print("\n" + "╔" + "═"*58 + "╗")
        print(f"  👤 CLIENTE: {usuario['nome'][:30]:<30} | SESSÃO: {horario_atual}")
        print(f"  🔑 ID CONTA: {usuario['id']:06d}                               ")
        print(f"  💵 SALDO DISPONÍVEL: R$ {usuario['saldo']:,.2f}")
        print("╚" + "═"*58 + "╝")
        print(" 1. Fazer Depósito")
        print(" 2. Fazer Transferência por E-mail")
        print(" 3. Executar Investimento")
        print(" 4. Ver Extrato")
        print(" 5. Ver Carteira")
        print(" 6. Resgatar Investimento")
        print(" 7. Sair da Conta (Logout)")
        print("─"*60)
        
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            try:
                valor = float(input("Digite o valor para depositar: R$ "))
                
                jdm_loading("Autenticando depósito nos servidores JDM", duracao_fixa=1.5)
                realizar_deposito(usuario['id'], valor)
            except ValueError:
                print("❌ Entrada inválida. Use apenas números.")

        elif opcao == '2':
            email_destino = input("E-mail do destinatário: ")
            try:
                valor = float(input("Valor da transferência: R$ "))

                with jdm_loading("Validando chaves e processando transferência (ACID)"):
                    realizar_transferencia(usuario['id'], email_destino, valor)
                    
            except ValueError:
                print("❌ Entrada inválida. Use apenas números.")

        elif opcao == '3':
            print("\n--- MERCADO DE INVESTIMENTOS ---\n1 - CDB | 2 - FII | 3 - BITCOIN")
            try:
                id_inv = int(input("Escolha o ID do ativo: "))
                valor = float(input("Valor a investir: R$ "))

                with jdm_loading("Buscando cotações em tempo real nas APIs"):
                    status = investir(usuario['id'], id_inv, valor)
            except ValueError:
                print("❌ Dados incorretos inseridos.")

        elif opcao == '4':
            jdm_loading("Puxando histórico do livro-razão", duracao_fixa=1.0)
            exibir_saldo(usuario['id'])
            exibir_extrato(usuario['id'])

        elif opcao == '5':
            jdm_loading("Consolidando ativos da carteira", duracao_fixa=0.8)
            exibir_carteira_investimentos(usuario['id'])

        elif opcao == '6':
            from investimento.investimento import resgatar_investimento
            resgatar_investimento(usuario['id'])

        elif opcao == '7':
            jdm_loading("Limpando dados temporários e fechando sessão", duracao_fixa=1.2)
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
            
            usuario_logado = None
            with jdm_loading("Verificando credenciais criptografadas"):
                usuario_logado = autenticar_usuario(cpf, senha)

            if usuario_logado:
                print(f"✅ Autenticação bem-sucedida.")
                menu_logado(usuario_logado) 
            else:
                print("\n❌ Falha no login: CPF ou Senha incorretos.")

        elif opcao == '2':
            print("\n--- FORMULÁRIO DE CADASTRO ---")
            
            while True:
                nome = input("Nome Completo: ")
                if validar_nome(nome): break
                print("❌ Erro: Insira seu nome e sobrenome (apenas letras).")

            while True:
                email = input("E-mail Único: ")
                if validar_email(email): break
                print("❌ Erro: Formato de e-mail inválido (exemplo@dominio.com).")

            while True:
                cpf = input("CPF (apenas números): ")
                if validar_cpf(cpf): break
                print("❌ Erro: CPF inválido. Digite novamente.")

            while True:
                telefone = input("Telefone/Celular (com DDD): ")
                if validar_telefone(telefone): break
                print("❌ Erro: Formato inválido. Digite apenas números com DDD (Ex: 79996021345).")
            
            while True:
                try:
                    idade = int(input("Idade: "))
                    if idade >= 18:
                        break
                    else:
                        print("❌ Erro: Cadastro permitido apenas para maiores de 18 anos.")
                except ValueError:
                    print("❌ Erro: Idade inválida. Digite apenas números inteiros.")
                
            while True:
                senha = input("Defina sua Senha: ")
                if validar_senha(senha): break
                print("❌ Erro: Senha fraca. Exigido: mínimo 8 caracteres, contendo letra maiúscula, minúscula, número e caractere especial.")

            usuario_novo = None
            with jdm_loading("Gravando novo registro de forma segura no banco"):
                usuario_novo = criar_usuario(nome, email, cpf, senha, telefone, idade)

            # Redireciona direto para o menu caso o cadastro tenha retornado o dicionário do usuário
            if usuario_novo:
                print("Acessando sua nova conta JDM...")
                menu_logado(usuario_novo)

        elif opcao == '3':
            print("Desligando terminais e conexões...")
            sys.exit()

if __name__ == "__main__":
    app()
