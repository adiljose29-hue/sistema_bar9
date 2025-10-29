import mysql.connector
from mysql.connector import Error
import logging
import sys

class Database:
    def __init__(self, config):
        self.config = config
        self.conexao = None
        
        # Configurar logging
        logging.basicConfig(
            filename='logs/sistema.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        self.conectar()
    
    def conectar(self):
        try:
            db_config = self.config.dados['banco_dados']
            self.conexao = mysql.connector.connect(
                host=db_config['host'],
                port=db_config['porta'],
                database=db_config['nome'],
                user=db_config['usuario'],
                password=db_config['senha'],
                autocommit=True
            )
            self.logger.info("Conexão com banco de dados estabelecida")
            print("✓ Conexão com banco de dados estabelecida")
        except Error as e:
            self.logger.error(f"Erro na conexão com banco de dados: {e}")
            print(f"✗ Erro na conexão com banco de dados: {e}")
            print("Verifique se o MySQL está rodando e a base de dados existe")
            sys.exit(1)
    
    def executar_query(self, query, params=None, fetch=True):
        try:
            cursor = self.conexao.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if fetch and query.strip().upper().startswith('SELECT'):
                resultado = cursor.fetchall()
                return resultado
            else:
                self.conexao.commit()
                if query.strip().upper().startswith('INSERT'):
                    return cursor.lastrowid
                return True
        except Error as e:
            self.logger.error(f"Erro na query: {e} - Query: {query}")
            print(f"Erro na query: {e}")
            return None
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    def testar_conexao(self):
        """Testar se a conexão está ativa"""
        try:
            resultado = self.executar_query("SELECT 1 as test")
            return resultado is not None
        except:
            return False