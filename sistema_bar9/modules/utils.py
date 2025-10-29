import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from decimal import Decimal

class TecladoVirtual:
    def __init__(self):
        self.layout = self._criar_layout()
    
    def _criar_layout(self):
        return [
            ['7', '8', '9'],
            ['4', '5', '6'],
            ['1', '2', '3'],
            ['0', '.', '⌫']
        ]
    
    def processar_toque(self, tecla, valor_atual):
        if tecla == '⌫':
            return valor_atual[:-1] if valor_atual else ""
        elif tecla == '.' and '.' not in valor_atual:
            return valor_atual + tecla if valor_atual else "0."
        elif tecla.isdigit():
            return valor_atual + tecla
        return valor_atual

class CalculadoraTroco:
    def __init__(self, config):
        self.config = config
        self.moeda = config.dados['sistema']['moeda']
        self.simbolo = config.dados['sistema']['simbolo_moeda']
    
    def calcular_troco(self, total, valor_pago, forma_pagamento):
        # Converter para Decimal para evitar problemas de precisão
        try:
            total_decimal = Decimal(str(total))
            valor_pago_decimal = Decimal(str(valor_pago))
        except:
            return None, "Erro nos valores numéricos"
        
        if forma_pagamento != 'dinheiro':
            if valor_pago_decimal > total_decimal:
                return None, f"Não é permitido troco em pagamentos com {forma_pagamento}"
            return Decimal('0'), ""
        
        if valor_pago_decimal < total_decimal:
            faltante = total_decimal - valor_pago_decimal
            return None, f"Valor insuficiente. Faltam {float(faltante):.2f} {self.simbolo}"
        
        troco = valor_pago_decimal - total_decimal
        return troco, f"Troco: {float(troco):.2f} {self.simbolo}"

class DatePicker:
    def __init__(self, parent):
        self.parent = parent
        self.data_selecionada = None
        
    def mostrar(self, data_inicial=None):
        self.data_selecionada = data_inicial or datetime.now().date()
        
        popup = tk.Toplevel(self.parent)
        popup.title("Selecionar Data")
        popup.geometry("300x250")
        popup.transient(self.parent)
        popup.grab_set()
        
        # Frame do calendário
        frame_cal = ttk.Frame(popup)
        frame_cal.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Controles de mês/ano
        frame_controles = ttk.Frame(frame_cal)
        frame_controles.pack(fill=tk.X)
        
        ttk.Button(frame_controles, text="<", 
                  command=lambda: self._alterar_mes(-1)).pack(side=tk.LEFT)
        
        self.label_mes_ano = ttk.Label(frame_controles, text="", font=('Arial', 10, 'bold'))
        self.label_mes_ano.pack(side=tk.LEFT, expand=True)
        
        ttk.Button(frame_controles, text=">", 
                  command=lambda: self._alterar_mes(1)).pack(side=tk.RIGHT)
        
        # Dias da semana
        frame_dias_semana = ttk.Frame(frame_cal)
        frame_dias_semana.pack(fill=tk.X)
        
        dias_semana = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
        for dia in dias_semana:
            ttk.Label(frame_dias_semana, text=dia, width=4).pack(side=tk.LEFT)
        
        self.frame_dias = ttk.Frame(frame_cal)
        self.frame_dias.pack(fill=tk.BOTH, expand=True)
        
        # Botões
        frame_botoes = ttk.Frame(popup)
        frame_botoes.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(frame_botoes, text="Hoje", 
                  command=lambda: self._selecionar_hoje()).pack(side=tk.LEFT)
        ttk.Button(frame_botoes, text="Cancelar", 
                  command=popup.destroy).pack(side=tk.RIGHT)
        ttk.Button(frame_botoes, text="OK", 
                  command=popup.destroy).pack(side=tk.RIGHT, padx=5)
        
        self._atualizar_calendario()
        
        self.parent.wait_window(popup)
        return self.data_selecionada
    
    def _alterar_mes(self, delta):
        try:
            year = self.data_selecionada.year
            month = self.data_selecionada.month + delta
            if month > 12:
                month = 1
                year += 1
            elif month < 1:
                month = 12
                year -= 1
            self.data_selecionada = self.data_selecionada.replace(year=year, month=month)
            self._atualizar_calendario()
        except ValueError:
            pass
    
    def _selecionar_hoje(self):
        self.data_selecionada = datetime.now().date()
        self._atualizar_calendario()
    
    def _atualizar_calendario(self):
        # Limpar dias anteriores
        for widget in self.frame_dias.winfo_children():
            widget.destroy()
        
        # Atualizar label do mês/ano
        self.label_mes_ano.config(text=self.data_selecionada.strftime("%B %Y"))
        
        # Calcular primeiro dia do mês
        primeiro_dia = self.data_selecionada.replace(day=1)
        dia_semana = primeiro_dia.weekday()  # 0=Segunda, 6=Domingo
        
        # Preencher calendário
        row, col = 0, 0
        for i in range(42):  # 6 semanas
            if i < dia_semana:
                # Dias vazios antes do primeiro dia
                ttk.Label(self.frame_dias, text="").grid(row=row, column=col, padx=2, pady=2)
            else:
                dia_num = i - dia_semana + 1
                try:
                    dia_data = self.data_selecionada.replace(day=dia_num)
                    btn = ttk.Button(self.frame_dias, text=str(dia_num),
                                   command=lambda d=dia_data: self._selecionar_dia(d))
                    btn.grid(row=row, column=col, padx=2, pady=2)
                    
                    if dia_data == datetime.now().date():
                        btn.config(style='Accent.TButton')
                    
                except ValueError:
                    # Dia inválido (fora do mês)
                    ttk.Label(self.frame_dias, text="").grid(row=row, column=col, padx=2, pady=2)
            
            col += 1
            if col > 6:
                col = 0
                row += 1
    
    def _selecionar_dia(self, dia):
        self.data_selecionada = dia

def formatar_moeda(valor, simbolo="Kz"):
    try:
        return f"{float(valor):.2f} {simbolo}"
    except:
        return f"0.00 {simbolo}"

def validar_numero_trabalhador(numero):
    return len(numero) == 5 and numero.isdigit()

def validar_senha(senha):
    return len(senha) == 4 and senha.isdigit()

def converter_para_float(valor):
    """Converter valor para float de forma segura"""
    try:
        if isinstance(valor, (int, float)):
            return float(valor)
        elif isinstance(valor, Decimal):
            return float(valor)
        else:
            return float(str(valor).replace(',', '.'))
    except (ValueError, TypeError):
        return 0.0