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
    email = email.strip().lower()
    regra = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(regra, email))

def validar_telefone(telefone):

    nums = ''.join(filter(str.isdigit, telefone))

    regra = r"^[1-9]{2}9[0-9]{8}$"
    return bool(re.match(regra, nums))

def validar_senha(senha):
    if len(senha) < 8: return False
    if not re.search(r"[A-Z]", password := senha): return False
    if not re.search(r"[a-z]", senha): return False
    if not re.search(r"\d", senha): return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=/\\]", senha): return False
    return True

def validar_cpf(cpf):
    # Mantida a sua validação original por algoritmo matemático
    cpf = ''.join(filter(str.isdigit, cpf))
    if len(cpf) != 11 or cpf == cpf[0] * 11: return False
    
    for j in (10, 11):
        soma = sum(int(cpf[i]) * (j - i) for i in range(j - 1))
        resto = (soma * 10) % 11
        if resto == 10: resto = 0
        if resto != int(cpf[j - 1]): return False
    return True



def criar_usuario(nome, email, cpf, senha, telefone, idade):
    conexao = obter_conexao()
    if not conexao: return None
    cursor = conexao.cursor()
    
    cpf_limpo = ''.join(filter(str.isdigit, cpf))
    
    # Adicionado RETURNING para capturar os dados gerados pelo banco
    sql = """
        INSERT INTO usuarios (nome, email, cpf, senha, telefone, idade)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id, nome, saldo
    """
    senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    try:
        cursor.execute(sql, (nome.strip(), email.strip().lower(), cpf_limpo, senha_hash, telefone, idade)) 
        
        # Recupera os dados retornados pelo INSERT
        id_gerado, nome_gerado, saldo_gerado = cursor.fetchone()
        
        conexao.commit()
        print(f"✅ Usuário {nome_gerado} cadastrado com sucesso!")
        
        # Retorna o dicionário no mesmo molde esperado pelo menu_logado
        return {"id": id_gerado, "nome": nome_gerado, "saldo": float(saldo_gerado)}
        
    except Exception as e:
        conexao.rollback()
        print(f"❌ Erro ao salvar no banco. CPF ou E-mail já existentes. Detalhes: {e}")
        return None
    finally:
        cursor.close()
        conexao.close()

def autenticar_usuario(cpf, senha):

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