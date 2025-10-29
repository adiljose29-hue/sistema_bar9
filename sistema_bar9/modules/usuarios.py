from .database import Database

class UsuarioManager:
    def __init__(self, db):
        self.db = db
    
    def autenticar(self, numero_trabalhador, senha):
        query = """
        SELECT id_usuario, numero_trabalhador, nome, tipo 
        FROM usuarios 
        WHERE numero_trabalhador = %s AND senha = %s AND ativo = TRUE
        """
        resultado = self.db.executar_query(query, (numero_trabalhador, senha))
        
        if resultado:
            return resultado[0]
        return None
    
    def validar_supervisor(self, codigo_cartao, numero_trabalhador, senha):
        from ..main import sistema
        codigo_config = sistema.config.dados['supervisor']['cartao_codigo_barras']
        
        if codigo_cartao != codigo_config:
            return None
        
        usuario = self.autenticar(numero_trabalhador, senha)
        if usuario and usuario['tipo'] in ['supervisor', 'admin', 'gerente']:
            return usuario
        return None
    
    def obter_usuarios(self):
        query = "SELECT id_usuario, numero_trabalhador, nome, tipo, ativo FROM usuarios ORDER BY nome"
        return self.db.executar_query(query)
    
    def criar_usuario(self, numero_trabalhador, senha, nome, tipo):
        query = """
        INSERT INTO usuarios (numero_trabalhador, senha, nome, tipo)
        VALUES (%s, %s, %s, %s)
        """
        return self.db.executar_query(query, (numero_trabalhador, senha, nome, tipo), fetch=False)
    
    def atualizar_usuario(self, id_usuario, dados):
        query = """
        UPDATE usuarios 
        SET numero_trabalhador = %s, nome = %s, tipo = %s, ativo = %s
        WHERE id_usuario = %s
        """
        return self.db.executar_query(query, (
            dados['numero_trabalhador'], 
            dados['nome'], 
            dados['tipo'], 
            dados['ativo'],
            id_usuario
        ), fetch=False)