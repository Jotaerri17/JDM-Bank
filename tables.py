#
from database import obter_conexao

def criar_tabelas():
    conexao = obter_conexao()
    if not conexao:
        return

    cursor = conexao.cursor()

    
    queries = [
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            cpf VARCHAR(14) UNIQUE NOT NULL,
            telefone VARCHAR(20),
            idade INT CHECK (idade >= 18),
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            saldo NUMERIC(15,2) DEFAULT 0.00
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS movimentacoes (
            id SERIAL PRIMARY KEY,
            usuario_id INT REFERENCES usuarios(id),
            tipo VARCHAR(25) NOT NULL,
            valor NUMERIC(15,2) NOT NULL,
            email_destino VARCHAR(100),
            data TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS tipos_investimento (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(50) NOT NULL,
            taxa_rendimento NUMERIC(5,2),
            taxa_operacao NUMERIC(5,2) DEFAULT 0.00
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS investimentos_usuarios (
            id SERIAL PRIMARY KEY,
            usuario_id INT REFERENCES usuarios(id),
            investimento_id INT REFERENCES tipos_investimento(id),
            valor_investido NUMERIC(15,2) NOT NULL,
            cotacao_compra NUMERIC(15,2),
            data_aplicacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    ]

    try:
        for query in queries:
            cursor.execute(query)
        conexao.commit() # Confirma as alterações no banco
        print("Tabelas criadas com sucesso!")
    except Exception as e:
        conexao.rollback() # Desfaz em caso de erro
        print(f"Erro ao criar tabelas: {e}")
    finally:
        cursor.close()
        conexao.close()

if __name__ == "__main__":
    criar_tabelas()