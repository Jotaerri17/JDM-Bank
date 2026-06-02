from database.database import obter_conexao

def realizar_deposito(usuario_id, valor):
    """Adiciona saldo à conta do usuário logado."""
    if valor <= 0:
        print("❌ Erro: O valor do depósito deve ser maior que zero.")
        return False

    conexao = obter_conexao()
    if not conexao: return False
    cursor = conexao.cursor()

    try:
        # Atualiza o saldo do usuário
        cursor.execute("UPDATE usuarios SET saldo = saldo + %s WHERE id = %s", (valor, usuario_id))
        
        # Registra o depósito no histórico
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
    """Realiza a transferência entre dois usuários via E-mail (Garante ACID e evita concorrência)."""
    if valor <= 0:
        print("❌ Erro: O valor do transferência deve ser maior que zero.")
        return False

    conexao = obter_conexao()
    if not conexao: return False
    cursor = conexao.cursor()

    try:
        # 1. Verifica o saldo aplicando FOR UPDATE para bloquear a linha contra cliques duplos simultâneos
        cursor.execute("SELECT saldo, email FROM usuarios WHERE id = %s FOR UPDATE", (id_remetente,))
        resultado_remetente = cursor.fetchone()
        
        if not resultado_remetente:
            print("❌ Erro: Conta de origem não encontrada.")
            return False
            
        saldo_atual = float(resultado_remetente[0])
        email_remetente = resultado_remetente[1]
        
        if saldo_atual < valor:
            print(f"❌ Erro: Saldo insuficiente. Seu saldo atual é R$ {saldo_atual:.2f}")
            return False

        # 2. Busca o ID do destinatário pelo e-mail informado
        cursor.execute("SELECT id FROM usuarios WHERE email = %s", (email_destino,))
        resultado_destino = cursor.fetchone()
        
        if not resultado_destino:
            print("❌ Erro: Usuário de destino não encontrado com este e-mail.")
            return False
            
        id_destino = resultado_destino[0]

        if id_remetente == id_destino:
            print("❌ Erro: Você não pode transferir para si mesmo.")
            return False

        # 3. Executa o débito e o crédito nas duas contas
        cursor.execute("UPDATE usuarios SET saldo = saldo - %s WHERE id = %s", (valor, id_remetente))
        cursor.execute("UPDATE usuarios SET saldo = saldo + %s WHERE id = %s", (valor, id_destino))

        # 4. Registra os dois lados da transação para fins de extrato/auditoria
        cursor.execute("""
            INSERT INTO movimentacoes (usuario_id, tipo, valor, email_destino)
            VALUES (%s, 'TRANSFERENCIA_ENVIADA', %s, %s)
        """, (id_remetente, valor, email_destino))

        cursor.execute("""
            INSERT INTO movimentacoes (usuario_id, tipo, valor, email_destino)
            VALUES (%s, 'TRANSFERENCIA_RECEBIDA', %s, %s)
        """, (id_destino, valor, email_remetente))

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