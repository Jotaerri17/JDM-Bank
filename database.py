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