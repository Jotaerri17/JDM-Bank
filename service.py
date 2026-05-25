
from database import obter_conexao

def criar_usuario(nome, email, cpf, telefone, idade):
    """Cadastra um novo usuário no banco de dados."""
    if idade < 18:
        print("❌ Erro: O usuário precisa ter 18 anos ou mais.")
        return False

    conexao = obter_conexao()
    if not conexao:
        return False
        
    cursor = conexao.cursor()

    sql = """
        INSERT INTO usuarios (nome, email, cpf, telefone, idade)
        VALUES (%s, %s, %s, %s, %s)
    """
    
    try:
        cursor.execute(sql, (nome, email, cpf, telefone, idade))
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


def autenticar_usuario(email, cpf):
    """Verifica se o e-mail e CPF batem com algum usuário no banco e retorna a sessão."""
    conexao = obter_conexao()
    if not conexao:
        return None

    cursor = conexao.cursor()
    try:
        cursor.execute("SELECT id, nome, saldo FROM usuarios WHERE email = %s AND cpf = %s", (email, cpf))
        usuario = cursor.fetchone()
        
        if usuario:
            # Retorna um dicionário com os dados essenciais da sessão
            return {
                "id": usuario[0],
                "nome": usuario[1],
                "saldo": float(usuario[2]) # Converte de Decimal do banco para Float do Python
            }
        else:
            return None
    except Exception as e:
        print(f"❌ Erro ao autenticar: {e}")
        return None
    finally:
        cursor.close()
        conexao.close()


def realizar_deposito(usuario_id, valor):
    """Adiciona saldo à conta do usuário logado."""
    if valor <= 0:
        print("❌ Erro: O valor do depósito deve ser maior que zero.")
        return False

    conexao = obter_conexao()
    if not conexao:
        return False

    cursor = conexao.cursor()
    try:
        # Atualiza o saldo
        cursor.execute("UPDATE usuarios SET saldo = saldo + %s WHERE id = %s", (valor, usuario_id))
        
        # Registra no extrato
        cursor.execute("""
            INSERT INTO movimentacoes (usuario_id, tipo, valor)
            VALUES (%s, 'DEPOSITO', %s)
        """, (usuario_id, valor))
        
        conexao.commit()
        print(f"✅ Depósito de R$ {valor:.2f} realizado com sucesso!")
        return True
    except Exception as e:
        conexao.rollback()
        print(f"❌ Erro ao depositar: {e}")
        return False
    finally:
        cursor.close()
        conexao.close()


def realizar_transferencia(id_remetente, email_destino, valor):
    """Realiza a transferência entre dois usuários via E-mail, usando transações de banco (ACID)."""
    if valor <= 0:
        print("❌ Erro: O valor da transferência deve ser maior que zero.")
        return False

    conexao = obter_conexao()
    if not conexao:
        return False

    cursor = conexao.cursor()

    try:
        # 1. Checa o saldo do remetente
        cursor.execute("SELECT saldo, email FROM usuarios WHERE id = %s", (id_remetente,))
        resultado_remetente = cursor.fetchone()
        
        if not resultado_remetente:
            print("❌ Erro: Conta de origem não encontrada.")
            return False
            
        saldo_atual = float(resultado_remetente[0])
        email_remetente = resultado_remetente[1]
        
        if saldo_atual < valor:
            print(f"❌ Erro: Saldo insuficiente. Seu saldo atual é R$ {saldo_atual:.2f}")
            return False

        # 2. Busca o ID do destinatário pelo e-mail
        cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email_destino,))
        resultado_destino = cursor.fetchone()
        
        if not resultado_destino:
            print("❌ Erro: Usuário de destino não encontrado com este e-mail.")
            return False
            
        id_destino = resultado_destino[0]

        if id_remetente == id_destino:
            print("❌ Erro: Você não pode transferir para si mesmo.")
            return False

        # 3. Deduz o valor do remetente
        cursor.execute("UPDATE usuarios SET saldo = saldo - %s WHERE id = %s", (valor, id_remetente))

        # 4. Adiciona o valor ao destinatário
        cursor.execute("UPDATE usuarios SET saldo = saldo + %s WHERE id = %s", (valor, id_destino))

        # 5. Registra no extrato do Remetente
        cursor.execute("""
            INSERT INTO movimentacoes (usuario_id, tipo, valor, email_destino)
            VALUES (%s, 'TRANSFERENCIA_ENVIADA', %s, %s)
        """, (id_remetente, valor, email_destino))

        # 6. Registra no extrato do Destinatário
        cursor.execute("""
            INSERT INTO movimentacoes (usuario_id, tipo, valor, email_destino)
            VALUES (%s, 'TRANSFERENCIA_RECEBIDA', %s, %s)
        """, (id_destino, valor, email_remetente))

        # 7. Confirma a transação
        conexao.commit()
        print(f"✅ Transferência PIX de R$ {valor:.2f} para {email_destino} realizada com sucesso!")
        return True

    except Exception as e:
        conexao.rollback()
        print(f"❌ Erro inesperado durante a transferência: {e}")
        return False

    finally:
        cursor.close()
        conexao.close()