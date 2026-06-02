from database.database import obter_conexao

def exibir_saldo(usuario_id):
    """Busca e exibe o saldo atualizado direto do banco de dados."""
    conexao = obter_conexao()
    if not conexao: return

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
    """Busca o histórico completo de movimentações incluindo transações e investimentos."""
    conexao = obter_conexao()
    if not conexao: return

    cursor = conexao.cursor()
    try:
        print("\n" + "="*60)
        print(" 📑 HISTÓRICO DE MOVIMENTAÇÕES (EXTRATO)")
        print("="*60)

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
                
                # Tratamento de cores dinâmico para depósitos, transferências e investimentos
                if "RECEBIDA" in tipo or "DEPOSITO" in tipo or "RESGATE" in tipo:
                    sinal = "+"
                    indicador = "🟢"
                else:
                    sinal = "-"
                    indicador = "🔴"
                
                info_destino = f" (Ref: {email_destino})" if email_destino else ""
                print(f" {indicador} [{data_formatada}] {tipo:<22} | {sinal}R$ {valor:>8.2f}{info_destino}")
                
        print("="*60)
    except Exception as e:
        print(f"❌ Erro ao carregar extrato: {e}")
    finally:
        cursor.close()
        conexao.close()


def exibir_carteira_investimentos(usuario_id):
    """Busca e exibe os investimentos ativos do usuário, incluindo o ID da aplicação."""
    conexao = obter_conexao()
    if not conexao: return

    cursor = conexao.cursor()
    try:
        query = """
            SELECT iu.id, ti.nome, iu.valor_investido, iu.cotacao_compra, iu.data_aplicacao
            FROM investimentos_usuarios iu
            JOIN tipos_investimento ti ON iu.investimento_id = ti.id
            WHERE iu.usuario_id = %s
            ORDER BY iu.data_aplicacao DESC
        """
        cursor.execute(query, (usuario_id,))
        investimentos = cursor.fetchall()

        print("\n" + "="*75)
        print(" 📈 CARTEIRA DE INVESTIMENTOS ATIVOS")
        print("="*75)

        if not investimentos:
            print("Você não possui investimentos ativos no momento.")
        else:
            print(f"{'ID':<5} | {'Ativo':<20} | {'Valor Aplicado':<15} | {'Cotação Compra':<15} | {'Data'}")
            print("-" * 75)
            
            for inv_id, nome, valor, cotacao, data in investimentos:
                data_str = data.strftime('%d/%m/%Y')
                print(f"{inv_id:<5} | {nome:<20} | R$ {valor:<12.2f} | R$ {cotacao:<12.2f} | {data_str}")
        print("="*75)

    except Exception as e:
        print(f"❌ Erro ao buscar carteira: {e}")
    finally:
        cursor.close()
        conexao.close()