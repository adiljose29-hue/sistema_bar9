import json
import os

class Configuracao:
    def __init__(self, arquivo_config='config.json'):
        self.arquivo_config = arquivo_config
        self.carregar_config()
    
    def carregar_config(self):
        try:
            with open(self.arquivo_config, 'r', encoding='utf-8') as f:
                self.dados = json.load(f)
        except FileNotFoundError:
            self.dados = self._config_padrao()
            self.salvar_config()
        except json.JSONDecodeError as e:
            print(f"Erro no ficheiro de configuração: {e}")
            self.dados = self._config_padrao()
            self.salvar_config()
    
    def salvar_config(self):
        try:
            with open(self.arquivo_config, 'w', encoding='utf-8') as f:
                json.dump(self.dados, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Erro ao salvar configuração: {e}")
            return False
    
    def carregar_layout_botoes(self):
        try:
            layout_file = self.dados['touchscreen']['layout_botoes']
            with open(layout_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Ficheiro de layout não encontrado: {layout_file}")
            return {"categorias": []}
        except Exception as e:
            print(f"Erro ao carregar layout: {e}")
            return {"categorias": []}
    
    def _config_padrao(self):
        return {
            "sistema": {
                "nome": "Sistema Bar Dois Computadores",
                "versao": "1.0",
                "moeda": "Kz",
                "simbolo_moeda": "Kz",
                "ativo_desconto": True,
                "ativo_multiforma_pagamento": True,
                "controlo_stock": True,
                "som_ativo": False,
                "mostrar_iva_ecra": False,
                "mostrar_iva_recibo": False,
                "iva_incluido_preco": True,
                "timeout_sessao": 300
            },
            "banco_dados": {
                "host": "localhost",
                "porta": 3306,
                "nome": "sistema_bar",
                "usuario": "root",
                "senha": ""
            },
            "recibo": {
                "tamanho_papel": 80,
                "cabecalho": {
                    "texto": "BAR DOIS COMPUTADORES",
                    "negrito": True,
                    "centralizado": True
                },
                "empresa": {
                    "nome": "Bar Dois Computadores, Lda",
                    "nif": "500000001",
                    "endereco": "Rua Principal, 123 - Luanda",
                    "telefone": "+244 900 000 000"
                },
                "detalhes": {
                    "mostrar_iva": False,
                    "mostrar_codigo_produto": True,
                    "mostrar_calculo_iva": False,
                    "mostrar_vendedor": True
                },
                "rodape": {
                    "texto": "Obrigado pela sua visita! Volte sempre!",
                    "centralizado": True
                },
                "local_guardar": "recibos/"
            },
            "impressora": {
                "tipo": "windows",
                "nome_impressora_windows": "Microsoft Print to PDF",
                "porta_usb": "USB001",
                "porta_ethernet": "192.168.1.100:9100",
                "comandos_escpos": {
                    "ativar_gaveta": "ESC p 0 60 240",
                    "corte_automatico": "ESC m",
                    "inicializar": "ESC @"
                },
                "corte_automatico": True
            },
            "supervisor": {
                "cartao_codigo_barras": "1234567890123",
                "validacao_usuario_senha": True
            },
            "touchscreen": {
                "teclado_virtual": True,
                "layout_botoes": "layout_botoes.json",
                "timeout_sessao": 300
            }
        }