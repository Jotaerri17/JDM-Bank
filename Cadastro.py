
from database import obter_conexao

def criar_usuario(nome, email, cpf, telefone, idade):
    if idade < 18:
        print("Erro: O usuário precisa ter 18 anos ou mais.")
        return False

    conexao = obter_conexao()
    cursor = conexao.cursor()

    sql = """
        INSERT INTO usuarios (nome, email, cpf, telefone, idade)
        VALUES (%s, %s, %s, %s, %s)
    """
    
    try:
        
        cursor.execute(sql, (nome, email, cpf, telefone, idade))
        conexao.commit()
        print(f"Usuário {nome} cadastrado com sucesso!")
        return True
    except Exception as e:
        conexao.rollback()
        print(f"Erro ao cadastrar usuário. Talvez CPF ou E-mail já existam. Detalhes: {e}")
        return False
    finally:
        cursor.close()
        conexao.close()