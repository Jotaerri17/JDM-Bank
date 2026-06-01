import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def obter_conexao():
    url = os.getenv("NEON_DB_URL")
    
    
    if not url:
        print("❌ ERRO: O arquivo .env não foi carregado ou a variável NEON_DB_URL está vazia/com nome errado.")
        return None
        
    try:
        conexao = psycopg2.connect(url)
        return conexao
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco de dados: {e}")
        return None
    


def criar_tabelas():
    conexao = obter_conexao()
    if not conexao:
        return

    cursor = conexao.cursor()

    
    queries = [
        "DROP TABLE IF EXISTS investimentos_usuarios CASCADE;",
        "DROP TABLE IF EXISTS tipos_investimento CASCADE;",
        "DROP TABLE IF EXISTS movimentacoes CASCADE;",
        "DROP TABLE IF EXISTS usuarios CASCADE;",
        """
        CREATE TABLE IF NOT EXISTS usuarios (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            cpf VARCHAR(14) UNIQUE NOT NULL,
            senha VARCHAR(255) NOT NULL,
            telefone VARCHAR(20),
            idade INT NOT NULL,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            saldo NUMERIC(15,2) DEFAULT 0.00
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS movimentacoes (
            id SERIAL PRIMARY KEY,
            usuario_id INT REFERENCES usuarios(id),
            tipo VARCHAR(100) NOT NULL,
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
   6
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


        # Adicione isso ao final do seu database.py

def popular_investimentos_padrao():
    conexao = obter_conexao()
    if not conexao:
        return
    cursor = conexao.cursor()
    
    # Inserindo os 3 produtos com IDs automáticos
    produtos = [
        ('CDB Pós-Fixado',),
        ('FII JDM Properties',),
        ('Bitcoin (BTC)',)
    ]
    
    try:
        for (nome,) in produtos:
            # Só insere o produto se ele já não existir pelo nome
            cursor.execute("""
                INSERT INTO tipos_investimento (nome)
                SELECT %s
                WHERE NOT EXISTS (SELECT 1 FROM tipos_investimento WHERE nome = %s);
            """, (nome, nome))
        conexao.commit()
        print("✅ Tipos de investimentos verificados/populados com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao popular investimentos: {e}")
    finally:
        cursor.close()
        conexao.close()

# Altere o bloco principal do database.py para executar também essa função:
if __name__ == "__main__":
    criar_tabelas()
    popular_investimentos_padrao()

