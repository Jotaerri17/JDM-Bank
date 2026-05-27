from database.database import obter_conexao

def exibir_saldo(usuario_id):
    """Busca e exibe o saldo atualizado direto do banco de dados."""
    conexao = obter_conexao()
    if not conexao:
        return

    cursor = conexao.cursor()
    try:
        cursor.execute("SELECT saldo FROM usuarios WHERE id = %s", (usuario_id,))
        resultado = cursor.fetchone()
        
        if resultado:
            saldo = float(resultado[0])
            print("\n" + "="*40)
            print(f" 💵 SALDO ATUAL: R$ {saldo:.2f}")
            print("="*40)
        else:
            print("❌ Usuário não encontrado.")
            
    except Exception as e:
        print(f"❌ Erro ao buscar saldo: {e}")
    finally:
        cursor.close()
        conexao.close()


def exibir_extrato(usuario_id):
    """Busca o histórico completo de movimentações (Depósitos e Transferências)."""
    conexao = obter_conexao()
    if not conexao:
        return

    cursor = conexao.cursor()
    try:
        print("\n" + "="*50)
        print(" 📑 HISTÓRICO DE MOVIMENTAÇÕES (EXTRATO)")
        print("="*50)

        cursor.execute("""
            SELECT tipo, valor, email_destino, data 
            FROM movimentacoes 
            WHERE usuario_id = %s 
            ORDER BY data DESC
        """, (usuario_id,))
        
        movimentacoes = cursor.fetchall()
        
        if not movimentacoes:
            print("   Nenhuma movimentação realizada nesta conta.")
        else:
            for tipo, valor, email_destino, data in movimentacoes:
                data_formatada = data.strftime("%d/%m/%Y %H:%M")
                
                if "RECEBIDA" in tipo or "DEPOSITO" in tipo:
                    sinal = "+"
                    indicador = "🟢"
                else:
                    sinal = "-"
                    indicador = "🔴"
                
                info_destino = f" (Para/De: {email_destino})" if email_destino else ""
                print(f" {indicador} [{data_formatada}] {tipo:<22} | {sinal}R$ {valor:>8.2f}{info_destino}")
                
        print("="*50)
    except Exception as e:
        print(f"❌ Erro ao carregar extrato: {e}")
    finally:
        cursor.close()
        conexao.close()


def exibir_carteira_investimentos(usuario_id):
    """Realiza um JOIN para buscar as aplicações do usuário e o nome do ativo."""
    conexao = obter_conexao()
    if not conexao:
        return

    cursor = conexao.cursor()
    try:
        print("\n" + "="*60)
        print(" 📈 CARTEIRA DE INVESTIMENTOS ATIVOS")
        print("="*60)

        cursor.execute("""
            SELECT t.nome, i.valor_investido, i.cotacao_compra, i.data_aplicacao 
            FROM investimentos_usuarios i
            JOIN tipos_investimento t ON i.investimento_id = t.id
            WHERE i.usuario_id = %s
            ORDER BY i.data_aplicacao DESC
        """, (usuario_id,))
        
        investimentos = cursor.fetchall()
        
        if not investimentos:
            print("   Você ainda não possui investimentos aplicados.")
        else:
            print(f" {'Ativo':<10} | {'Valor Aplicado':<15} | {'Cotação Compra':<15} | {'Data':<12}")
            print("-" * 60)
            for nome, valor, cotacao, data in investimentos:
                data_formatada = data.strftime("%d/%m/%Y")
                cotacao_val = f"R$ {cotacao:.2f}" if cotacao else "N/A"
                print(f" {nome:<10} | R$ {valor:<12.2f} | {cotacao_val:<15} | {data_formatada:<12}")
                
        print("="*60)
    except Exception as e:
        print(f"❌ Erro ao carregar investimentos: {e}")
    finally:
        cursor.close()
        conexao.close()