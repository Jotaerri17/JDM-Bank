
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def obter_conexao():
    """ Conexão com o banco de dados Neon."""
    try:
        conexao = psycopg2.connect(os.getenv("NEON_DB_URL"))
        return conexao
    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None