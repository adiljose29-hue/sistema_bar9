from .database import Database
from datetime import datetime
import random
from decimal import Decimal

class VendaManager:
    def __init__(self, db):
        self.db = db
    
    def criar_venda(self, id_vendedor, itens, desconto=0, forma_pagamento='dinheiro', id_supervisor=None):
        # Calcular totais usando Decimal para precisão
        total = Decimal('0')
        for item in itens:
            # Converter preço para Decimal
            preco = Decimal(str(item['preco']))
            quantidade = Decimal(str(item['quantidade']))
            total += preco * quantidade
        
        desconto_decimal = Decimal(str(desconto))
        total_final = total - desconto_decimal
        
        # Gerar número da venda
        numero_venda = f"V{datetime.now().strftime('%Y%m%d')}{random.randint(1000, 9999)}"
        
        # Inserir venda (converter para float para o banco)
        query = """
        INSERT INTO vendas (numero_venda, id_vendedor, total, desconto, total_final, forma_pagamento, id_supervisor)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        id_venda = self.db.executar_query(query, (
            numero_venda, 
            id_vendedor, 
            float(total), 
            float(desconto_decimal), 
            float(total_final), 
            forma_pagamento, 
            id_supervisor
        ), fetch=False)
        
        if id_venda:
            # Inserir itens
            for item in itens:
                self.adicionar_item_venda(id_venda, item)
            
            # Atualizar stock
            self.atualizar_stock(itens)
            
            # Registrar log
            self.registrar_log(id_vendedor, f'Venda criada: {numero_venda}', f'Total: {float(total_final):.2f}')
        
        return id_venda, numero_venda
    
    # ... restante do código permanece igual

  
    def adicionar_item_venda(self, id_venda, item):
        total_item = item['preco'] * item['quantidade']
        query = """
        INSERT INTO venda_itens (id_venda, id_produto, quantidade, preco_unitario, total_item)
        VALUES (%s, %s, %s, %s, %s)
        """
        return self.db.executar_query(query, (
            id_venda, item['id_produto'], item['quantidade'], item['preco'], total_item
        ), fetch=False)
    
    def obter_venda_por_numero(self, numero_venda):
        query = """
        SELECT v.*, u.nome as nome_vendedor
        FROM vendas v
        JOIN usuarios u ON v.id_vendedor = u.id_usuario
        WHERE v.numero_venda = %s
        """
        return self.db.executar_query(query, (numero_venda,))
    
    def obter_itens_venda(self, id_venda):
        query = """
        SELECT vi.*, p.nome as nome_produto, p.codigo_barras
        FROM venda_itens vi
        JOIN produtos p ON vi.id_produto = p.id_produto
        WHERE vi.id_venda = %s AND vi.anulado = FALSE
        """
        return self.db.executar_query(query, (id_venda,))
    
    def anular_item(self, id_item, id_supervisor):
        query = """
        UPDATE venda_itens 
        SET anulado = TRUE, id_supervisor_anulacao = %s 
        WHERE id_item = %s
        """
        resultado = self.db.executar_query(query, (id_supervisor, id_item), fetch=False)
        
        if resultado:
            # Obter dados do item para atualizar stock
            query_item = "SELECT id_produto, quantidade FROM venda_itens WHERE id_item = %s"
            item = self.db.executar_query(query_item, (id_item,))
            if item:
                # Devolver stock
                query_stock = "UPDATE produtos SET stock_atual = stock_atual + %s WHERE id_produto = %s"
                self.db.executar_query(query_stock, (item[0]['quantidade'], item[0]['id_produto']), fetch=False)
            
            self.registrar_log(id_supervisor, f'Item anulado: {id_item}')
        
        return resultado
    
    def aplicar_desconto(self, id_venda, desconto, id_supervisor):
        query = """
        UPDATE vendas 
        SET desconto = %s, total_final = total - %s, id_supervisor = %s 
        WHERE id_venda = %s
        """
        resultado = self.db.executar_query(query, (desconto, desconto, id_supervisor, id_venda), fetch=False)
        
        if resultado:
            self.registrar_log(id_supervisor, f'Desconto aplicado: {desconto} na venda {id_venda}')
        
        return resultado
    
    def atualizar_stock(self, itens):
        for item in itens:
            query = "UPDATE produtos SET stock_atual = stock_atual - %s WHERE id_produto = %s"
            self.db.executar_query(query, (item['quantidade'], item['id_produto']), fetch=False)
    
    def obter_vendas_periodo(self, data_inicio, data_fim):
        query = """
        SELECT v.*, u.nome as nome_vendedor
        FROM vendas v
        JOIN usuarios u ON v.id_vendedor = u.id_usuario
        WHERE v.data_venda BETWEEN %s AND %s AND v.estado = 'concluida'
        ORDER BY v.data_venda DESC
        """
        return self.db.executar_query(query, (data_inicio, data_fim))
    
    def registrar_log(self, id_usuario, acao, detalhes=None):
        query = "INSERT INTO logs_sistema (id_usuario, acao, detalhes) VALUES (%s, %s, %s)"
        return self.db.executar_query(query, (id_usuario, acao, detalhes), fetch=False)