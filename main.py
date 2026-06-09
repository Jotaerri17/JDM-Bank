import sys
import time
import threading
from datetime import datetime
from database.database import obter_conexao
from transferencias.transferencias import realizar_deposito, realizar_transferencia
from investimento.investimento import investir
from visualizacoes.visualizacoes import exibir_saldo, exibir_extrato, exibir_carteira_investimentos


from auth.auth import Autenticador, Validador

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


class JDBMBankApp:
    """Classe que controla toda a interface e fluxo da aplicação no terminal."""
    
    def __init__(self):
        
        self.usuario_logado = None

    def executar(self):
        """Inicia o ciclo principal do sistema."""
        while True:
            print("\n" + "="*40 + "\n🏦 JDM BANK OPERATIONAL TERMINAL\n" + "="*40)
            print("1. Entrar na Conta (Login)\n2. Abrir Nova Conta\n3. Encerrar Sistema")
            print("="*40)

            opcao = input("Escolha uma opção: ")

            if opcao == '1':
                self._fluxo_login()
            elif opcao == '2':
                self._fluxo_registo()
            elif opcao == '3':
                print("Desligando terminais e conexões...")
                sys.exit()

    def _fluxo_login(self):
        print("\n--- AUTENTICAÇÃO ---")
        cpf = input("CPF: ")
        senha = input("Senha: ")
        
        with jdm_loading("Verificando credenciais criptografadas"):
            self.usuario_logado = Autenticador.autenticar(cpf, senha)

        if self.usuario_logado:
            print("✅ Autenticação bem-sucedida.")
            self._menu_logado()
        else:
            print("\n❌ Falha no login: CPF ou Senha incorretos.")

    def _fluxo_registo(self):
        print("\n--- FORMULÁRIO DE CADASTRO ---")
        
        
        while True:
            nome = input("Nome Completo: ")
            if Validador.nome(nome): break
            print("❌ Erro: Insira o seu nome e apelido (apenas letras).")

        while True:
            email = input("E-mail Único: ")
            if Validador.email(email): break
            print("❌ Erro: Formato de e-mail inválido.")

        while True:
            cpf = input("CPF (apenas números): ")
            if Validador.cpf(cpf): break
            print("❌ Erro: CPF inválido. Digite novamente.")

        while True:
            telefone = input("Telefone/Telemóvel: ")
            if Validador.telefone(telefone): break
            print("❌ Erro: Formato inválido.")
        
        while True:
            try:
                idade = int(input("Idade: "))
                if idade >= 18: break
                else: print("❌ Erro: Registo permitido apenas para maiores de 18 anos.")
            except ValueError:
                print("❌ Erro: Idade inválida.")
            
        while True:
            senha = input("Defina a sua Senha: ")
            if Validador.senha(senha): break
            print("❌ Erro: Senha fraca. Exigido: mínimo 8 caracteres, maiúscula, minúscula, número e especial.")

        tipo_conta = 'CORRENTE'
        while True:
            print("\nQual Tipo de Conta deseja abrir?\n1 - Conta Corrente\n2 - Conta Poupança\n3 - Conta Empresarial (PJ)")
            op_tipo = input("Sua escolha: ")
            if op_tipo == '1': tipo_conta = 'CORRENTE'; break
            elif op_tipo == '2': tipo_conta = 'POUPANCA'; break
            elif op_tipo == '3': tipo_conta = 'PJ'; break
            else: print("❌ Opção inválida.")

        with jdm_loading("Gravando novo registo de forma segura no banco"):
            sucesso = Autenticador.criar_usuario(nome, email, cpf, senha, telefone, idade, tipo_conta)

        if sucesso:
            print("\n✅ Vá em frente e faça o Login (Opção 1) com o seu CPF e nova Senha!")

    def _menu_logado(self):
        """Menu interno quando o utilizador já está logado."""
        while self.usuario_logado:
            
            self.usuario_logado.sincronizar_saldo()
            horario_atual = datetime.now().strftime("%H:%M:%S")

            print("\n" + "╔" + "═"*58 + "╗")
            print(f"  {self.usuario_logado.exibir_dados()} | SESSÃO: {horario_atual}")
            print(f"  🔑 ID CONTA: {self.usuario_logado.id:06d}                               ")
            print("╚" + "═"*58 + "╝")
            print(" 1. Fazer Depósito")
            print(" 2. Fazer Transferência")
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
                    realizar_deposito(self.usuario_logado.id, valor)
                except ValueError:
                    print("❌ Entrada inválida.")

            elif opcao == '2':
                email_destino = input("E-mail do destinatário: ")
                try:
                    valor = float(input("Valor da transferência: R$ "))
                    with jdm_loading("Validando chaves e processando transferência"):
                        realizar_transferencia(self.usuario_logado.id, email_destino, valor)
                except ValueError:
                    print("❌ Entrada inválida.")

            elif opcao == '3':
                print("\n--- MERCADO DE INVESTIMENTOS ---\n1 - CDB | 2 - FII | 3 - BITCOIN")
                try:
                    id_inv = int(input("Escolha o ID do ativo: "))
                    valor = float(input("Valor a investir: R$ "))
                    with jdm_loading("Buscando cotações em tempo real nas APIs"):
                        investir(self.usuario_logado.id, id_inv, valor)
                except ValueError:
                    print("❌ Dados incorretos inseridos.")

            elif opcao == '4':
                jdm_loading("Puxando histórico do livro-razão", duracao_fixa=1.0)
                exibir_saldo(self.usuario_logado.id)
                exibir_extrato(self.usuario_logado.id)

            elif opcao == '5':
                jdm_loading("Consolidando ativos da carteira", duracao_fixa=0.8)
                exibir_carteira_investimentos(self.usuario_logado.id)

            elif opcao == '6':
                from investimento.investimento import resgatar_investimento
                resgatar_investimento(self.usuario_logado.id)

            elif opcao == '7':
                jdm_loading("Limpando dados temporários e fechando sessão", duracao_fixa=1.2)
                print("🔒 Sessão encerrada de forma segura.")
                
                self.usuario_logado = None 
            else:
                print("❌ Opção inválida.")

if __name__ == "__main__":
    
    banco_app = JDBMBankApp()
    banco_app.executar()