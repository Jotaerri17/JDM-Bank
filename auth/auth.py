from database.database import obter_conexao


def criar_usuario(nome, email, cpf, senha, telefone, idade):
    """Cadastra um novo usuário no banco de dados."""
    if idade < 18:
        print("❌ Erro: O usuário precisa ter 18 anos ou mais.")
        return False

    conexao = obter_conexao()
    if not conexao:
        return False
        
    cursor = conexao.cursor()

    sql = """
        INSERT INTO usuarios (nome, email, cpf, senha, telefone, idade)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    
    try:
        cursor.execute(sql, (nome, email, cpf, senha, telefone, idade))
        conexao.commit()
        print(f"✅ Usuário {nome} cadastrado com sucesso!")
        return True
    except Exception as e:
        conexao.rollback()
        print(f"❌ Erro ao cadastrar usuário. Talvez o CPF ou E-mail já estejam em uso. Detalhes: {e}")
        return False
    finally:
        cursor.close()
        conexao.close()


def autenticar_usuario(cpf, senha):
    """Verifica se o CPF e a Senha batem com algum usuário no banco e retorna a sessão."""
    conexao = obter_conexao()
    if not conexao:
        return None

    cursor = conexao.cursor()
    try:
        # Busca o ID, nome e saldo filtrando por CPF e Senha
        cursor.execute(
            "SELECT id, nome, saldo FROM usuarios WHERE cpf = %s AND senha = %s", 
            (cpf, senha)
        )
        usuario = cursor.fetchone()
        
        if usuario:
            
            return {
                "id": usuario[0],
                "nome": usuario[1],
                "saldo": float(usuario[2]) # Converte o Decimal do Postgres para Float do Python
            }
            
        return None 

    except Exception as e:
        print(f"❌ Erro ao autenticar: {e}")
        return None
        
    finally:
        cursor.close()
        conexao.close()
