import bcrypt
import re
from database.database import obter_conexao


def validar_senha(senha):
    """Valida se a senha possui:
    - mínimo 8 caracteres
    - 1 letra maiúscula
    - 1 letra minúscula
    - 1 número
    - 1 caractere especial
    """

    if len(senha) < 8:
        return False

    if not re.search(r"[A-Z]", senha):
        return False

    if not re.search(r"[a-z]", senha):
        return False

    if not re.search(r"\d", senha):
        return False

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=/\\]", senha):
        return False

    return True


def validar_cpf(cpf):
    """Valida CPF"""

    cpf = ''.join(filter(str.isdigit, cpf))

    if len(cpf) != 11:
        return False

    if cpf == cpf[0] * 11:
        return False

    soma = 0
    for i in range(9):
        soma += int(cpf[i]) * (10 - i)

    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto

    soma = 0
    for i in range(10):
        soma += int(cpf[i]) * (11 - i)

    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto

    return cpf[-2:] == f"{digito1}{digito2}"


def criar_usuario(nome, email, cpf, senha, telefone, idade):
    """Cadastra um novo usuário no banco de dados."""

    if idade < 18:
        print("❌ Erro: O usuário precisa ter 18 anos ou mais.")
        return False
    
    erro = False

    if not validar_cpf(cpf):
        print("❌ Erro: CPF inválido.")
        erro = True

    if not validar_senha(senha):
        print(
            "❌ Erro: A senha deve conter no mínimo 8 caracteres, "
            "1 letra maiúscula, 1 letra minúscula, "
            "1 número e 1 caractere especial."
        )
        erro = True

    if erro:
        return False

    conexao = obter_conexao()
    if not conexao:
        return False

    cursor = conexao.cursor()

    sql = """
        INSERT INTO usuarios (nome, email, cpf, senha, telefone, idade)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    senha_hash = bcrypt.hashpw(
        senha.encode('utf-8'),
        bcrypt.gensalt()
    ).decode('utf-8')


    try:
        cursor.execute(
            sql,
            (nome, email, cpf, senha_hash, telefone, idade)
        )       
        conexao.commit()
        print(f"✅ Usuário {nome} cadastrado com sucesso!")
        return True

    except Exception as e:
        conexao.rollback()
        print(
            f"❌ Erro ao cadastrar usuário. "
            f"Talvez o CPF ou E-mail já estejam em uso. Detalhes: {e}"
        )
        return False

    finally:
        cursor.close()
        conexao.close()


def autenticar_usuario(cpf, senha):
    """Verifica se o CPF e a senha correspondem a um usuário."""

    conexao = obter_conexao()
    if not conexao:
        return None

    cursor = conexao.cursor()

    try:
        cursor.execute(
            """
            SELECT id, nome, saldo, senha
            FROM usuarios
            WHERE cpf = %s
            """,
            (cpf,)
        )

        usuario = cursor.fetchone()

        if not usuario:
            return None

        senha_hash = usuario[3]

        if bcrypt.checkpw(
            senha.encode('utf-8'),
            senha_hash.encode('utf-8')
        ):
            return {
                "id": usuario[0],
                "nome": usuario[1],
                "saldo": float(usuario[2])
            }

        return None

    except Exception as e:
        print(f"❌ Erro ao autenticar: {e}")
        return None

    finally:
        cursor.close()
        conexao.close()