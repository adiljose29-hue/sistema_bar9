from .database import Database
from datetime import datetime

class DevolucaoManager:
    def __init__(self, db):
        self.db = db
    
    def criar_devolucao_total(self, id_venda_original, id_supervisor, id_vendedor, motivo):
        # Obter dados da venda original
        query_venda = "SELECT total_final, numero_venda FROM vendas WHERE id_venda = %s"
        venda = self.db.executar_query(query_venda, (id_venda_original,))
        
        if not venda:
            return False, "Venda não encontrada"
        
        # Criar devolução total
        query = """
        INSERT INTO devolucoes (id_venda_original, id_supervisor, id_vendedor, motivo, tipo, valor_devolvido)
        VALUES (%s, %s, %s, %s, 'total', %s)
        """
        id_devolucao = self.db.executar_query(query, (
            id_venda_original, id_supervisor, id_vendedor, motivo, venda[0]['total_final']
        ), fetch=False)
        
        if not id_devolucao:
            return False, "Erro ao criar devolução"
        
        # Devolver todos os itens
        query_itens = """
        SELECT vi.id_item, vi.quantidade, vi.id_produto 
        FROM venda_itens vi 
        WHERE vi.id_venda = %s AND vi.anulado = FALSE
        """
        itens = self.db.executar_query(query_itens, (id_venda_original,))
        
        for item in itens:
            self._devolver_item(id_devolucao, item['id_item'], item['quantidade'])
        
        # Registrar log
        self._registrar_log(id_supervisor, f'Devolução total: {venda[0]["numero_venda"]}', motivo)
        
        return True, f"Devolução total realizada com sucesso. Valor: {venda[0]['total_final']}"
    
    def criar_devolucao_parcial(self, id_venda_original, id_supervisor, id_vendedor, itens_devolver, motivo):
        valor_total = 0
        
        # Criar devolução
        query = """
        INSERT INTO devolucoes (id_venda_original, id_supervisor, id_vendedor, motivo, tipo)
        VALUES (%s, %s, %s, %s, 'parcial')
        """
        id_devolucao = self.db.executar_query(query, (
            id_venda_original, id_supervisor, id_vendedor, motivo
        ), fetch=False)
        
        if not id_devolucao:
            return False, "Erro ao criar devolução parcial"
        
        # Processar itens a devolver
        for item in itens_devolver:
            valor_devolvido = self._devolver_item(id_devolucao, item['id_item'], item['quantidade'])
            valor_total += valor_devolvido
        
        # Atualizar valor total da devolução
        update_query = "UPDATE devolucoes SET valor_devolvido = %s WHERE id_devolucao = %s"
        self.db.executar_query(update_query, (valor_total, id_devolucao), fetch=False)
        
        # Registrar log
        self._registrar_log(id_supervisor, f'Devolução parcial: {id_venda_original}', 
                           f'Valor: {valor_total} - Motivo: {motivo}')
        
        return True, f"Devolução parcial realizada com sucesso. Valor: {valor_total}"
    
    def _devolver_item(self, id_devolucao, id_item_original, quantidade):
        # Obter valor do item
        query_item = """
        SELECT vi.preco_unitario, vi.total_item, vi.quantidade, p.id_produto
        FROM venda_itens vi
        JOIN produtos p ON vi.id_produto = p.id_produto
        WHERE vi.id_item = %s
        """
        item_data = self.db.executar_query(query_item, (id_item_original,))
        
        if not item_data:
            return 0
        
        item = item_data[0]
        preco_unitario = item['preco_unitario']
        valor_devolvido = preco_unitario * quantidade
        
        # Inserir item devolvido
        query = """
        INSERT INTO devolucao_itens (id_devolucao, id_item_original, quantidade_devolvida, valor_devolvido)
        VALUES (%s, %s, %s, %s)
        """
        self.db.executar_query(query, (id_devolucao, id_item_original, quantidade, valor_devolvido), fetch=False)
        
        # Atualizar stock
        update_stock = "UPDATE produtos SET stock_atual = stock_atual + %s WHERE id_produto = %s"
        self.db.executar_query(update_stock, (quantidade, item['id_produto']), fetch=False)
        
        return valor_devolvido
    
    def obter_devolucoes_periodo(self, data_inicio, data_fim):
        query = """
        SELECT d.*, v.numero_venda, u.nome as nome_supervisor, uv.nome as nome_vendedor
        FROM devolucoes d
        JOIN vendas v ON d.id_venda_original = v.id_venda
        JOIN usuarios u ON d.id_supervisor = u.id_usuario
        JOIN usuarios uv ON d.id_vendedor = uv.id_usuario
        WHERE d.data_devolucao BETWEEN %s AND %s
        ORDER BY d.data_devolucao DESC
        """
        return self.db.executar_query(query, (data_inicio, data_fim))
    
    def _registrar_log(self, id_usuario, acao, detalhes):
        query = "INSERT INTO logs_sistema (id_usuario, acao, detalhes) VALUES (%s, %s, %s)"
        return self.db.executar_query(query, (id_usuario, acao, detalhes), fetch=False)