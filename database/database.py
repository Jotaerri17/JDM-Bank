import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def obter_conexao():
    url = os.getenv("NEON_DB_URL")
    
    if not url:
        print("❌ ERRO: O arquivo .env não foi carregado ou a variável NEON_DB_URL está vazia.")
        return None
        
    try:
        conexao = psycopg2.connect(url)
        
        cursor = conexao.cursor()
        cursor.execute("SET TIME ZONE 'America/Sao_Paulo';")
        cursor.close()
        
        return conexao
    
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco de dados: {e}")
        return None

def criar_tabelas():
    conexao = obter_conexao()
    if not conexao: return

    cursor = conexao.cursor()

    sql_estrutura = """
    DROP TABLE IF EXISTS investimentos_usuarios CASCADE;
    DROP TABLE IF EXISTS tipos_investimento CASCADE;
    DROP TABLE IF EXISTS movimentacoes CASCADE;
    DROP TABLE IF EXISTS usuarios CASCADE;

    CREATE TABLE usuarios (
        id SERIAL PRIMARY KEY,
        nome VARCHAR(100) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        cpf VARCHAR(14) UNIQUE NOT NULL,
        senha VARCHAR(255) NOT NULL,
        telefone VARCHAR(20),
        idade INT NOT NULL,
        data_criacao TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
        saldo NUMERIC(15,2) DEFAULT 0.00
    );

    CREATE TABLE movimentacoes (
        id SERIAL PRIMARY KEY,
        usuario_id INT REFERENCES usuarios(id) ON DELETE CASCADE,
        tipo VARCHAR(100) NOT NULL,
        valor NUMERIC(15,2) NOT NULL,
        email_destino VARCHAR(100),
        data TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE tipos_investimento (
        id SERIAL PRIMARY KEY,
        nome VARCHAR(50) NOT NULL,
        taxa_rendimento NUMERIC(5,2) DEFAULT 0.00,
        taxa_operacao NUMERIC(5,2) DEFAULT 0.00
    );

    CREATE TABLE investimentos_usuarios (
        id SERIAL PRIMARY KEY,
        usuario_id INT REFERENCES usuarios(id) ON DELETE CASCADE,
        investimento_id INT REFERENCES tipos_investimento(id) ON DELETE CASCADE,
        valor_investido NUMERIC(15,2) NOT NULL,
        cotacao_compra NUMERIC(15,2),
        data_aplicacao TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
    );
    """

    try:
        cursor.execute(sql_estrutura)
        conexao.commit()
        print("✅ Estrutura do banco de dados criada com sucesso!")

    except Exception as e:
        conexao.rollback()
        print(f"❌ Erro ao criar tabelas: {e}")

    finally:
        cursor.close()
        conexao.close()

def popular_investimentos_padrao():
    conexao = obter_conexao()
    if not conexao: return
    
    cursor = conexao.cursor()
    produtos = ['CDB Pós-Fixado', 'FII JDM Properties', 'Bitcoin (BTC)']
    
    try:
        for nome in produtos:

            cursor.execute("""
                INSERT INTO tipos_investimento (nome)
                SELECT %s
                WHERE NOT EXISTS (SELECT 1 FROM tipos_investimento WHERE nome = %s);
            """, (nome, nome))

        conexao.commit()

        print("✅ Tipos de investimentos populados com sucesso!")

    except Exception as e:
        conexao.rollback()
        print(f"❌ Erro ao popular investimentos: {e}")

    finally:
        cursor.close()
        conexao.close()

if __name__ == "__main__":
    criar_tabelas()
    popular_investimentos_padrao()