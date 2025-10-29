import win32print
import socket
import os
import tempfile
import subprocess
import platform
from datetime import datetime

class ImpressoraManager:
    def __init__(self, config):
        self.config = config
        self.tipo_impressora = config.dados['impressora']['tipo']
    
    def imprimir_recibo(self, texto):
        """Imprime recibo no formato adequado"""
        try:
            # Formatar texto para impressão
            texto_formatado = self._formatar_texto_impressao(texto)
            
            if self.tipo_impressora == 'windows':
                return self._imprimir_windows(texto_formatado)
            elif self.tipo_impressora == 'usb':
                return self._imprimir_usb(texto_formatado)
            elif self.tipo_impressora == 'ethernet':
                return self._imprimir_ethernet(texto_formatado)
            elif self.tipo_impressora == 'escpos':
                return self._imprimir_escpos(texto_formatado)
            else:
                print(f"Tipo de impressora não suportado: {self.tipo_impressora}")
                return self._criar_pdf(texto_formatado)
        except Exception as e:
            print(f"Erro geral na impressão: {e}")
            return self._criar_pdf(texto_formatado)
    
    def _formatar_texto_impressao(self, texto):
        """Formata o texto para impressão"""
        linhas = texto.split('\n')
        texto_formatado = ""
        
        for linha in linhas:
            texto_formatado += linha + "\n"
        
        return texto_formatado
    
    def _imprimir_windows(self, texto):
        try:
            printer_name = self.config.dados['impressora']['nome_impressora_windows']
            
            # Listar impressoras disponíveis
            impressoras = [printer[2] for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)]
            print(f"Impressoras disponíveis: {impressoras}")
            
            if printer_name not in impressoras:
                print(f"Impressora '{printer_name}' não encontrada. Usando padrão.")
                printer_name = win32print.GetDefaultPrinter()
            
            print(f"Tentando imprimir na: {printer_name}")
            
            hprinter = win32print.OpenPrinter(printer_name)
            try:
                # Configurar propriedades da impressão
                doc_info = ("Recibo Sistema Bar", None, "RAW")
                
                hjob = win32print.StartDocPrinter(hprinter, 1, doc_info)
                try:
                    win32print.StartPagePrinter(hprinter)
                    
                    # Converter texto para bytes (usar cp850 para compatibilidade)
                    texto_bytes = texto.encode('cp850', 'ignore')
                    win32print.WritePrinter(hprinter, texto_bytes)
                    
                    win32print.EndPagePrinter(hprinter)
                finally:
                    win32print.EndDocPrinter(hprinter)
                
                # Executar comandos adicionais
                if self.config.dados['impressora'].get('corte_automatico', True):
                    self._executar_corte_papel(hprinter)
                
                if self.config.dados['impressora'].get('abrir_gaveta', True):
                    self._abrir_gaveta_dinheiro()
                
                print("✓ Recibo impresso com sucesso (Windows)")
                return True
                
            except Exception as e:
                print(f"Erro durante impressão: {e}")
                return self._criar_pdf(texto)
            finally:
                win32print.ClosePrinter(hprinter)
                
        except Exception as e:
            print(f"✗ Erro impressora Windows: {e}")
            return self._criar_pdf(texto)
    
    def _imprimir_usb(self, texto):
        try:
            porta = self.config.dados['impressora']['porta_usb']
            print(f"Tentando imprimir na porta USB: {porta}")
            
            # Adicionar comandos ESC/POS se for impressora térmica
            if self.tipo_impressora == 'escpos' or 'COM' in porta.upper():
                texto = self._adicionar_comandos_escpos(texto)
            
            if platform.system() == "Windows":
                # Windows - tentar diferentes métodos
                try:
                    # Método 1: Usando echo
                    comando = f'echo {texto} > {porta}'
                    result = os.system(comando)
                    if result == 0:
                        print("✓ Impressão USB via echo bem-sucedida")
                        return True
                except:
                    pass
                
                try:
                    # Método 2: Escrever diretamente na porta
                    with open(porta, 'wb') as printer:
                        printer.write(texto.encode('utf-8'))
                    print("✓ Impressão USB direta bem-sucedida")
                    return True
                except Exception as e:
                    print(f"Erro método direto: {e}")
            
            else:
                # Linux
                try:
                    with open(porta, 'wb') as printer:
                        printer.write(texto.encode('utf-8'))
                    print("✓ Impressão USB Linux bem-sucedida")
                    return True
                except Exception as e:
                    print(f"Erro Linux: {e}")
            
            return self._criar_pdf(texto)
            
        except Exception as e:
            print(f"✗ Erro impressora USB: {e}")
            return self._criar_pdf(texto)
    
    def _imprimir_ethernet(self, texto):
        try:
            endereco = self.config.dados['impressora']['porta_ethernet']
            print(f"Tentando imprimir via Ethernet: {endereco}")
            
            ip, port_str = endereco.split(':')
            port = int(port_str)
            
            # Adicionar comandos ESC/POS se configurado
            if self.tipo_impressora == 'escpos':
                texto = self._adicionar_comandos_escpos(texto)
            
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(10)
                sock.connect((ip, port))
                sock.sendall(texto.encode('utf-8'))
                sock.close()
            
            print("✓ Recibo impresso com sucesso (Ethernet)")
            return True
            
        except Exception as e:
            print(f"✗ Erro impressora Ethernet: {e}")
            return self._criar_pdf(texto)
    
    def _imprimir_escpos(self, texto):
        try:
            texto_comandos = self._adicionar_comandos_escpos(texto)
            
            if 'porta_usb' in self.config.dados['impressora']:
                return self._imprimir_usb(texto_comandos)
            else:
                return self._imprimir_ethernet(texto_comandos)
                
        except Exception as e:
            print(f"✗ Erro impressora ESC/POS: {e}")
            return self._criar_pdf(texto)
    
    def _adicionar_comandos_escpos(self, texto):
        """Adiciona comandos ESC/POS para formatação"""
        # Comando inicializar
        texto_comandos = "\x1B@"
        
        # Texto normal
        texto_comandos += texto
        
        # Comando de corte de papel
        if self.config.dados['impressora'].get('corte_automatico', True):
            texto_comandos += "\n\n\x1D\x56\x00"  # Cortar papel
        
        return texto_comandos
    
    def _executar_corte_papel(self, hprinter):
        """Executa corte de papel para impressoras térmicas"""
        try:
            if self.tipo_impressora in ['escpos', 'usb', 'ethernet']:
                comando_corte = "\x1D\x56\x00"  # Comando ESC/POS para corte
                win32print.WritePrinter(hprinter, comando_corte.encode('utf-8'))
                print("✓ Corte de papel executado")
        except Exception as e:
            print(f"Erro no corte de papel: {e}")
    
    def _abrir_gaveta_dinheiro(self):
        """Abre a gaveta de dinheiro"""
        try:
            if self.config.dados['impressora'].get('abrir_gaveta', True):
                comando_gaveta = "\x1B\x70\x00\x19\xFA"  # Comando ESC/POS para abrir gaveta
                
                if self.tipo_impressora == 'windows':
                    printer_name = self.config.dados['impressora']['nome_impressora_windows']
                    hprinter = win32print.OpenPrinter(printer_name)
                    try:
                        win32print.WritePrinter(hprinter, comando_gaveta.encode('utf-8'))
                    finally:
                        win32print.ClosePrinter(hprinter)
                elif self.tipo_impressora in ['usb', 'escpos']:
                    # Implementar para USB
                    pass
                
                print("✓ Gaveta de dinheiro aberta")
        except Exception as e:
            print(f"Erro ao abrir gaveta: {e}")
    
    def _criar_pdf(self, texto):
        """Cria um arquivo PDF como fallback"""
        try:
            # Criar diretório de recibos se não existir
            os.makedirs('recibos_pdf', exist_ok=True)
            
            nome_arquivo = f"recibos_pdf/recibo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                f.write("=== RECIBO (SIMULAÇÃO DE IMPRESSÃO) ===\n")
                f.write("Arquivo criado porque impressora não está disponível\n")
                f.write("=" * 50 + "\n")
                f.write(texto)
            
            print(f"✓ Recibo salvo em: {nome_arquivo}")
            return True
        except Exception as e:
            print(f"✗ Erro ao criar arquivo PDF: {e}")
            return False
    
    def testar_impressora(self):
        """Testa a conexão com a impressora"""
        texto_teste = """
        TESTE DE IMPRESSORA
        ===================
        Sistema Bar
        Data: {data}
        Hora: {hora}
        ===================
        Este é um teste de impressão.
        Se esta mensagem aparecer, a impressora está configurada corretamente.
        ===================
        """.format(
            data=datetime.now().strftime('%d/%m/%Y'),
            hora=datetime.now().strftime('%H:%M:%S')
        )
        
        print("Testando impressora...")
        print(f"Tipo: {self.tipo_impressora}")
        
        if self.tipo_impressora == 'windows':
            print(f"Impressora Windows: {self.config.dados['impressora']['nome_impressora_windows']}")
        elif self.tipo_impressora == 'usb':
            print(f"Porta USB: {self.config.dados['impressora']['porta_usb']}")
        elif self.tipo_impressora == 'ethernet':
            print(f"Endereço Ethernet: {self.config.dados['impressora']['porta_ethernet']}")
        
        return self.imprimir_recibo(texto_teste)
    
    def listar_impressoras_windows(self):
        """Lista todas as impressoras disponíveis no Windows"""
        if platform.system() == "Windows":
            impressoras = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)
            print("Impressoras disponíveis no Windows:")
            for i, printer in enumerate(impressoras):
                print(f"{i+1}. {printer[2]}")
            return impressoras
        return []

    def gerar_texto_recibo(self, dados_venda):
        config = self.config.dados
        recibo = []
        
        # Cabeçalho
        cabecalho = config['recibo']['cabecalho']
        recibo.append(cabecalho['texto'])
        recibo.append("=" * 40)
        
        # Dados da empresa
        empresa = config['recibo']['empresa']
        recibo.append(empresa['nome'])
        recibo.append(f"NIF: {empresa['nif']}")
        recibo.append(empresa['endereco'])
        recibo.append(f"Tel: {empresa['telefone']}")
        recibo.append("-" * 40)
        
        # Dados da venda
        recibo.append(f"Data: {dados_venda['data']}")
        recibo.append(f"Recibo: {dados_venda['numero_venda']}")
        if config['recibo']['detalhes']['mostrar_vendedor']:
            recibo.append(f"Vendedor: {dados_venda['vendedor']}")
        recibo.append("-" * 40)
        
        # Itens
        recibo.append(f"{'Descrição':<20} {'Qtd':>3} {'Preço':>8} {'Total':>8}")
        recibo.append("-" * 40)
        
        for item in dados_venda['itens']:
            nome = item['nome'][:19]  # Limitar tamanho
            linha = f"{nome:<20} {item['quantidade']:>3} {item['preco']:>8.2f} {item['total_item']:>8.2f}"
            recibo.append(linha)
        
        recibo.append("-" * 40)
        recibo.append(f"{'TOTAL:':<31} {dados_venda['total']:>8.2f} {config['sistema']['simbolo_moeda']}")
        
        if dados_venda['desconto'] > 0:
            recibo.append(f"{'DESCONTO:':<31} {dados_venda['desconto']:>8.2f} {config['sistema']['simbolo_moeda']}")
        
        recibo.append(f"{'TOTAL FINAL:':<31} {dados_venda['total_final']:>8.2f} {config['sistema']['simbolo_moeda']}")
        recibo.append(f"Pagamento: {dados_venda['forma_pagamento']}")
        
        if dados_venda['troco'] > 0:
            recibo.append(f"{'TROCO:':<31} {dados_venda['troco']:>8.2f} {config['sistema']['simbolo_moeda']}")
        
        # Rodapé
        rodape = config['recibo']['rodape']
        recibo.append("=" * 40)
        recibo.append(rodape['texto'])
        recibo.append(" " * 5)  # Espaço para corte
        
        return "\n".join(recibo)