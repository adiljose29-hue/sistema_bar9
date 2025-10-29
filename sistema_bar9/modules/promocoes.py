from .database import Database
from datetime import datetime
from decimal import Decimal

class PromocaoManager:
    def __init__(self, db):
        self.db = db
    
    def obter_preco_com_promocao(self, id_produto):
        query = """
        SELECT p.preco_venda, prom.desconto_percentual, prom.preco_promocao
        FROM produtos p
        LEFT JOIN promocoes prom ON p.id_produto = prom.id_produto 
            AND prom.ativa = TRUE 
            AND NOW() BETWEEN prom.data_inicio AND prom.data_fim
        WHERE p.id_produto = %s
        """
        resultado = self.db.executar_query(query, (id_produto,))
        
        if resultado and resultado[0]['desconto_percentual'] is not None:
            preco_base = Decimal(str(resultado[0]['preco_venda']))
            
            if resultado[0]['preco_promocao'] is not None:  # Preço fixo promocional
                return float(Decimal(str(resultado[0]['preco_promocao'])))
            else:  # Desconto percentual
                desconto = Decimal(str(resultado[0]['desconto_percentual'] or 0))
                preco_final = preco_base * (Decimal('1') - desconto / Decimal('100'))
                return float(preco_final)
        
        return float(Decimal(str(resultado[0]['preco_venda']))) if resultado else 0.0
    
    # ... restante do código permanece igual
   
    def obter_todas_promocoes(self):
        query = """
        SELECT p.*, prod.nome as nome_produto, prod.preco_venda as preco_normal
        FROM promocoes p
        JOIN produtos prod ON p.id_produto = prod.id_produto
        ORDER BY p.ativa DESC, p.data_inicio DESC
        """
        return self.db.executar_query(query)
    
    def obter_todas_promocoes(self):
        query = """
        SELECT p.*, prod.nome as nome_produto
        FROM promocoes p
        JOIN produtos prod ON p.id_produto = prod.id_produto
        ORDER BY p.data_inicio DESC
        """
        return self.db.executar_query(query)

    def obter_promocoes_ativas(self):
        """Obtém todas as promoções ativas"""
        query = """
        SELECT p.*, prod.nome as nome_produto, prod.preco_venda as preco_normal
        FROM promocoes p
        JOIN produtos prod ON p.id_produto = prod.id_produto
        WHERE p.ativa = TRUE AND NOW() BETWEEN p.data_inicio AND p.data_fim
        ORDER BY p.data_inicio
        """
        return self.db.executar_query(query)
    
    def criar_promocao(self, dados):
        query = """
        INSERT INTO promocoes (id_produto, nome_promocao, desconto_percentual, preco_promocao, data_inicio, data_fim, ativa)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        return self.db.executar_query(query, (
            dados['id_produto'],
            dados['nome_promocao'],
            dados['desconto_percentual'],
            dados['preco_promocao'],
            dados['data_inicio'],
            dados['data_fim'],
            dados['ativa']
        ), fetch=False)
    
    def atualizar_promocao(self, id_promocao, dados):
        query = """
        UPDATE promocoes 
        SET id_produto = %s, nome_promocao = %s, desconto_percentual = %s, 
            preco_promocao = %s, data_inicio = %s, data_fim = %s, ativa = %s
        WHERE id_promocao = %s
        """
        return self.db.executar_query(query, (
            dados['id_produto'],
            dados['nome_promocao'],
            dados['desconto_percentual'],
            dados['preco_promocao'],
            dados['data_inicio'],
            dados['data_fim'],
            dados['ativa'],
            id_promocao
        ), fetch=False)
    
    def desativar_promocao(self, id_promocao):
        query = "UPDATE promocoes SET ativa = FALSE WHERE id_promocao = %s"
        return self.db.executar_query(query, (id_promocao,), fetch=False)