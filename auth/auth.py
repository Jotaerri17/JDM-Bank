import bcrypt
import re
from database.database import obter_conexao

def validar_nome(nome):

    nome = nome.strip()

    regras = r"^[A-Za-zÀ-ÖØ-öø-ÿ]+(\s+[A-Za-zÀ-ÖØ-öø-ÿ]+)+$"

    if not re.match(regras, nome) or len(nome) < 5:
        return False
    return True

def validar_email(email):
    """Valida se o e-mail segue o formato padrão (usuario@dominio.com)."""
    email = email.strip().lower()
    padrao = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(padrao, email))

def validar_senha(senha):
    """Valida se a senha atende aos requisitos mínimos."""
    if len(senha) < 8: return False
    if not re.search(r"[A-Z]", senha): return False
    if not re.search(r"[a-z]", senha): return False
    if not re.search(r"\d", senha): return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=/\\]", senha): return False
    return True

def validar_cpf(cpf):
    """Valida se o CPF possui a estrutura e dígitos verificadores corretos."""
    cpf = ''.join(filter(str.isdigit, cpf))
    if len(cpf) != 11 or cpf == cpf[0] * 11: return False
    
    for j in (10, 11):
        soma = sum(int(cpf[i]) * (j - i) for i in range(j - 1))
        resto = (soma * 10) % 11
        if resto == 10: resto = 0
        if resto != int(cpf[j - 1]): return False
    return True

def criar_usuario(nome, email, cpf, senha, telefone, idade):
    """Garante unicamente a persistência do usuário após validação prévia."""
    conexao = obter_conexao()
    if not conexao: return False

    cursor = conexao.cursor()
    sql = """
        INSERT INTO usuarios (nome, email, cpf, senha, telefone, idade)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    try:
        # Garante o salvamento com strings limpas (sem espaços sobressalentes)
        cursor.execute(sql, (nome.strip(), email.strip().lower(), cpf, senha_hash, telefone, idade))       
        conexao.commit()
        print(f"✅ Usuário {nome} cadastrado com sucesso!")
        return True
    except Exception as e:
        conexao.rollback()
        print(f"❌ Erro ao salvar no banco. CPF ou E-mail já existentes. Detalhes: {e}")
        return False
    finally:
        cursor.close()
        conexao.close()

def autenticar_usuario(cpf, senha):
    """Verifica as credenciais informadas contra o banco de dados."""
    conexao = obter_conexao()
    if not conexao: return None
    cursor = conexao.cursor()

    try:
        cursor.execute("SELECT id, nome, saldo, senha FROM usuarios WHERE cpf = %s", (cpf,))
        usuario = cursor.fetchone()
        if not usuario: return None

        senha_hash = usuario[3]
        if bcrypt.checkpw(senha.encode('utf-8'), senha_hash.encode('utf-8')):
            return {"id": usuario[0], "nome": usuario[1], "saldo": float(usuario[2])}
        return None
    except Exception as e:
        print(f"❌ Erro ao autenticar: {e}")
        return None
    finally:
        cursor.close()
        conexao.close()