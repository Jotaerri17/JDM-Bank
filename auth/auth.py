import bcrypt
import re
from database.database import obter_conexao
from contas import ContaCorrente, ContaPoupanca, ContaPJ

class Validador:
    """Classe utilitária para validação de dados de entrada."""
    
    @staticmethod
    def nome(nome):
        nome = nome.strip()
        regras = r"^[A-Za-zÀ-ÖØ-öø-ÿ]+(\s+[A-Za-zÀ-ÖØ-öø-ÿ]+)+$"
        return bool(re.match(regras, nome)) and len(nome) >= 5

    @staticmethod
    def email(email):
        email = email.strip().lower()
        regra = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(regra, email))

    @staticmethod
    def telefone(telefone):
        nums = ''.join(filter(str.isdigit, telefone))
        regra = r"^[1-9]{2}9[0-9]{8}$"
        return bool(re.match(regra, nums))

    @staticmethod
    def senha(senha):
        if len(senha) < 8: return False
        if not re.search(r"[A-Z]", senha): return False
        if not re.search(r"[a-z]", senha): return False
        if not re.search(r"\d", senha): return False
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=/\\]", senha): return False
        return True

    @staticmethod
    def cpf(cpf):
        cpf = ''.join(filter(str.isdigit, cpf))
        if len(cpf) != 11 or cpf == cpf[0] * 11: return False
        for j in (10, 11):
            soma = sum(int(cpf[i]) * (j - i) for i in range(j - 1))
            resto = (soma * 10) % 11
            if resto == 10: resto = 0
            if resto != int(cpf[j - 1]): return False
        return True


class Autenticador:
    """Classe responsável por gerir o acesso ao sistema (Login e Registo)."""
    
    @staticmethod
    def criar_usuario(nome, email, cpf, senha, telefone, idade, tipo_conta='CORRENTE'):
        conexao = obter_conexao()
        if not conexao: return False
        cursor = conexao.cursor()
        
        cpf_limpo = ''.join(filter(str.isdigit, cpf))
        senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        sql = """
            INSERT INTO usuarios (nome, email, cpf, senha, telefone, idade, tipo_conta)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        try:
            cursor.execute(sql, (nome.strip(), email.strip().lower(), cpf_limpo, senha_hash, telefone, idade, tipo_conta)) 
            conexao.commit()
            print(f"✅ Utilizador {nome.strip()} cadastrado com sucesso como Conta {tipo_conta}!")
            return True
        except Exception as e:
            conexao.rollback()
            print(f"❌ Erro ao salvar no banco. CPF ou E-mail já existentes.")
            return False
        finally:
            cursor.close()
            conexao.close()

    @staticmethod
    def autenticar(cpf, senha):
        conexao = obter_conexao()
        if not conexao: return None

        cursor = conexao.cursor()
        cpf_limpo = ''.join(filter(str.isdigit, cpf))

        try:
            cursor.execute("SELECT id, nome, saldo, tipo_conta, senha FROM usuarios WHERE cpf = %s", (cpf_limpo,))
            usuario = cursor.fetchone()
            
            if usuario:
                id_conta, nome, saldo, tipo, senha_hash_banco = usuario[0], usuario[1], float(usuario[2]), (usuario[3].upper() if usuario[3] else 'CORRENTE'), usuario[4]

                if bcrypt.checkpw(senha.encode('utf-8'), senha_hash_banco.encode('utf-8')):
                    if tipo == 'PJ': return ContaPJ(id_conta, nome, saldo)
                    elif tipo == 'POUPANCA': return ContaPoupanca(id_conta, nome, saldo)
                    else: return ContaCorrente(id_conta, nome, saldo)
            return None
        except Exception as e:
            print(f"❌ Erro ao autenticar: {e}")
            return None
        finally:
            cursor.close()
            conexao.close()