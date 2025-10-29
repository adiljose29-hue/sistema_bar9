from .database import Database
from decimal import Decimal

class ProdutoManager:
    def __init__(self, db):
        self.db = db
    
    def obter_produto_por_codigo(self, codigo):
        query = """
        SELECT p.*, 
               prom.desconto_percentual, 
               prom.preco_promocao,
               prom.data_inicio,
               prom.data_fim
        FROM produtos p
        LEFT JOIN promocoes prom ON p.id_produto = prom.id_produto 
            AND prom.ativa = TRUE 
            AND NOW() BETWEEN prom.data_inicio AND prom.data_fim
        WHERE (p.codigo_barras = %s OR p.id_produto = %s) AND p.ativo = TRUE
        """
        resultado = self.db.executar_query(query, (codigo, codigo))
        return resultado[0] if resultado else None
    
    # ... restante do código

    def obter_todos_produtos(self):
        query = """
        SELECT p.*, 
               COALESCE(prom.preco_promocao, p.preco_venda * (1 - COALESCE(prom.desconto_percentual, 0) / 100)) as preco_atual,
               prom.nome_promocao
        FROM produtos p
        LEFT JOIN promocoes prom ON p.id_produto = prom.id_produto 
            AND prom.ativa = TRUE 
            AND NOW() BETWEEN prom.data_inicio AND prom.data_fim
        WHERE p.ativo = TRUE
        ORDER BY p.categoria, p.nome
        """
        return self.db.executar_query(query)
    
    def obter_produtos_por_categoria(self, categoria):
        query = "SELECT * FROM produtos WHERE categoria = %s AND ativo = TRUE ORDER BY nome"
        return self.db.executar_query(query, (categoria,))
    
    def criar_produto(self, dados):
        query = """
        INSERT INTO produtos (codigo_barras, nome, descricao, preco_venda, preco_custo, stock_atual, stock_minimo, iva, categoria)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        return self.db.executar_query(query, (
            dados['codigo_barras'],
            dados['nome'],
            dados['descricao'],
            dados['preco_venda'],
            dados['preco_custo'],
            dados['stock_atual'],
            dados['stock_minimo'],
            dados['iva'],
            dados['categoria']
        ), fetch=False)
    
    def atualizar_produto(self, id_produto, dados):
        query = """
        UPDATE produtos 
        SET codigo_barras = %s, nome = %s, descricao = %s, preco_venda = %s, 
            preco_custo = %s, stock_atual = %s, stock_minimo = %s, iva = %s, categoria = %s
        WHERE id_produto = %s
        """
        return self.db.executar_query(query, (
            dados['codigo_barras'],
            dados['nome'],
            dados['descricao'],
            dados['preco_venda'],
            dados['preco_custo'],
            dados['stock_atual'],
            dados['stock_minimo'],
            dados['iva'],
            dados['categoria'],
            id_produto
        ), fetch=False)
    
    def atualizar_stock(self, id_produto, quantidade):
        query = "UPDATE produtos SET stock_atual = stock_atual + %s WHERE id_produto = %s"
        return self.db.executar_query(query, (quantidade, id_produto), fetch=False)
    
    def obter_produtos_baixo_stock(self):
        query = "SELECT * FROM produtos WHERE stock_atual <= stock_minimo AND ativo = TRUE"
        return self.db.executar_query(query)