# Crie este arquivo em: modelos/contas.py
from database.database import obter_conexao

class ContaBase:
    """Classe base que contém o comportamento padrão de qualquer conta do JDM Bank."""
    def __init__(self, id_conta, nome, saldo, tipo_conta):
        self.id = id_conta
        self.nome = nome
        self.saldo = saldo
        self.tipo_conta = tipo_conta

    def exibir_dados(self):
        return f"👤 {self.nome} | Tipo: {self.tipo_conta} | Saldo: R$ {self.saldo:.2f}"

    def sincronizar_saldo(self):
        """Atualiza o saldo do objeto consultando o banco de dados."""
        conexao = obter_conexao()
        if not conexao: return
        cursor = conexao.cursor()
        try:
            cursor.execute("SELECT saldo FROM usuarios WHERE id = %s", (self.id,))
            resultado = cursor.fetchone()
            if resultado:
                self.saldo = float(resultado[0])
        except Exception as e:
            print(f"Erro ao sincronizar: {e}")
        finally:
            cursor.close()
            conexao.close()



class ContaCorrente(ContaBase):
    def __init__(self, id_conta, nome, saldo):
        
        super().__init__(id_conta, nome, saldo, 'CORRENTE')

class ContaPoupanca(ContaBase):
    def __init__(self, id_conta, nome, saldo):
        super().__init__(id_conta, nome, saldo, 'POUPANCA')
        
    def aplicar_rendimento_mensal(self):
        
        pass

class ContaPJ(ContaBase):
    def __init__(self, id_conta, nome, saldo):
        super().__init__(id_conta, nome, saldo, 'PJ')
        
    
    def exibir_dados(self):
        return f"🏢 EMPRESA: {self.nome} | Tipo: {self.tipo_conta} | Saldo: R$ {self.saldo:.2f}"