import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
from datetime import datetime
from decimal import Decimal

class InterfaceTouchscreen:
    def __init__(self, sistema):
        self.sistema = sistema
        self.root = tk.Tk()
        self.root.title("Sistema de Vendas - Touchscreen")
        self.root.attributes('-fullscreen', True)
        
        self.carrinho = []
        self.valor_digitado = ""
        self.campo_ativo = None
        self.layout_botoes = self.sistema.config.carregar_layout_botoes()
        self.vendedor_autenticado = None
        
        # Importar utilitários
        from modules.utils import TecladoVirtual, CalculadoraTroco, converter_para_float
        self.teclado_virtual = TecladoVirtual()
        self.calculadora_troco = CalculadoraTroco(self.sistema.config)
        self.converter_para_float = converter_para_float
        
        self.criar_interface()
        self.autenticar_vendedor()
    
    def configurar_estilo(self):
        """Configura o estilo da interface"""
        try:
            style = ttk.Style()
            style.configure('Accent.TButton', font=('Arial', 10, 'bold'), background='#0078D4')
            style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        except:
            pass  # Ignora erros de estilo
    
    def autenticar_vendedor(self):
        """Autentica o vendedor no início da sessão"""
        from interfaces.login_vendedor import LoginVendedor
        login = LoginVendedor(self.root, self.sistema)
        self.vendedor_autenticado = login.mostrar()
        
        if not self.vendedor_autenticado:
            messagebox.showerror("Erro", "Autenticação necessária!")
            self.root.quit()
            return
    
    def criar_interface(self):
        # Configurar estilo
        self.configurar_estilo()
        
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Barra superior com informações
        self.criar_barra_superior(main_frame)
        
        # Frame superior (carrinho e totais)
        frame_superior = ttk.Frame(main_frame)
        frame_superior.pack(fill=tk.X, pady=(0, 10))
        
        # Frame do carrinho (expandido)
        frame_carrinho = ttk.LabelFrame(frame_superior, text="Carrinho de Compras", padding=10)
        frame_carrinho.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, padx=(0, 10))
        
        # Lista do carrinho com scrollbar
        frame_lista = ttk.Frame(frame_carrinho)
        frame_lista.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(frame_lista)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.lista_carrinho = tk.Listbox(
            frame_lista, 
            font=('Arial', 12),
            yscrollcommand=scrollbar.set,
            selectmode=tk.SINGLE
        )
        self.lista_carrinho.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        self.lista_carrinho.bind('<Double-Button-1>', self.editar_item_carrinho)
        scrollbar.config(command=self.lista_carrinho.yview)
        
        # Frame totais
        frame_totais = ttk.Frame(frame_carrinho)
        frame_totais.pack(fill=tk.X, pady=5)
        
        self.label_total = ttk.Label(
            frame_totais, 
            text="Total: 0.00 Kz", 
            font=('Arial', 16, 'bold'),
            foreground='green'
        )
        self.label_total.pack(side=tk.LEFT)
        
        # Frame botões ação do carrinho
        frame_acoes = ttk.Frame(frame_carrinho)
        frame_acoes.pack(fill=tk.X, pady=5)
        
        ttk.Button(
            frame_acoes, 
            text="FINALIZAR VENDA", 
            command=self.finalizar_venda
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            frame_acoes, 
            text="EDITAR ITEM", 
            command=self.editar_item_selecionado
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            frame_acoes, 
            text="REMOVER ITEM", 
            command=self.remover_item_selecionado
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            frame_acoes, 
            text="LIMPAR TUDO", 
            command=self.limpar_carrinho
        ).pack(side=tk.LEFT, padx=2)
        
        # Frame pesquisa e teclado
        frame_lateral = ttk.Frame(frame_superior)
        frame_lateral.pack(fill=tk.BOTH, side=tk.RIGHT)
        
        # Frame pesquisa
        frame_pesquisa = ttk.LabelFrame(frame_lateral, text="Pesquisa Rápida", padding=10)
        frame_pesquisa.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(frame_pesquisa, text="Código do Produto:").pack(anchor=tk.W)
        
        frame_codigo = ttk.Frame(frame_pesquisa)
        frame_codigo.pack(fill=tk.X, pady=5)
        
        self.entry_codigo = ttk.Entry(frame_codigo, font=('Arial', 14), justify='center')
        self.entry_codigo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.entry_codigo.bind('<FocusIn>', lambda e: self.definir_campo_ativo('codigo'))
        self.entry_codigo.bind('<Return>', lambda e: self.adicionar_por_codigo())
        
        ttk.Button(
            frame_codigo, 
            text="➕", 
            command=self.adicionar_por_codigo,
            width=3
        ).pack(side=tk.RIGHT)
        
        # Botão de leitor de código de barras (simulado)
        ttk.Button(
            frame_pesquisa, 
            text="📷 Simular Leitor Código", 
            command=self.simular_leitor_codigo_barras
        ).pack(fill=tk.X, pady=5)
        
        # Teclado virtual
        self.criar_teclado_virtual(frame_lateral)
        
        # Frame produtos (abas por categoria)
        frame_produtos = ttk.LabelFrame(main_frame, text="Produtos", padding=10)
        frame_produtos.pack(fill=tk.BOTH, expand=True)
        
        self.criar_botoes_produtos(frame_produtos)
    
    def criar_barra_superior(self, parent):
        frame_barra = ttk.Frame(parent)
        frame_barra.pack(fill=tk.X, pady=(0, 10))
        
        # Informações do vendedor e hora
        self.label_info = ttk.Label(
            frame_barra, 
            text="Vendedor: Não autenticado | Hora: --:--:--", 
            font=('Arial', 10)
        )
        self.label_info.pack(side=tk.LEFT)
        
        # Botões de sistema
        frame_botoes_sistema = ttk.Frame(frame_barra)
        frame_botoes_sistema.pack(side=tk.RIGHT)
        
        ttk.Button(
            frame_botoes_sistema, 
            text="🔧 Configurações", 
            command=self.mostrar_configuracoes_rapidas
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            frame_botoes_sistema, 
            text="📊 Relatório Diário", 
            command=self.mostrar_relatorio_diario
        ).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(
            frame_botoes_sistema, 
            text="🚪 Sair", 
            command=self.root.quit
        ).pack(side=tk.LEFT, padx=2)
        
        # Atualizar hora
        self.atualizar_hora()
    
    def atualizar_hora(self):
        """Atualiza a hora na barra superior"""
        if self.vendedor_autenticado:
            hora_atual = datetime.now().strftime("%H:%M:%S")
            self.label_info.config(
                text=f"Vendedor: {self.vendedor_autenticado['nome']} | Hora: {hora_atual}"
            )
        self.root.after(1000, self.atualizar_hora)
    
    def criar_teclado_virtual(self, parent):
        frame_teclado = ttk.LabelFrame(parent, text="Teclado Virtual", padding=10)
        frame_teclado.pack(fill=tk.BOTH, expand=True)
        
        # Display do valor digitado
        self.display_valor = ttk.Entry(
            frame_teclado, 
            font=('Arial', 16), 
            justify=tk.CENTER,
            state='readonly'
        )
        self.display_valor.pack(fill=tk.X, pady=5)
        
        # Teclado numérico
        frame_teclas = ttk.Frame(frame_teclado)
        frame_teclas.pack(fill=tk.BOTH, expand=True)
        
        for row, linha_teclas in enumerate(self.teclado_virtual.layout):
            for col, tecla in enumerate(linha_teclas):
                btn = ttk.Button(
                    frame_teclas,
                    text=tecla,
                    command=lambda t=tecla: self.processar_tecla(t)
                )
                btn.grid(row=row, column=col, padx=2, pady=2, sticky='nsew')
                frame_teclas.grid_columnconfigure(col, weight=1)
            
            frame_teclas.grid_rowconfigure(row, weight=1)
    
    def criar_botoes_produtos(self, parent):
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        for categoria in self.layout_botoes['categorias']:
            frame_categoria = ttk.Frame(notebook, padding=5)
            notebook.add(frame_categoria, text=categoria['nome'])
            
            # Configurar grid
            for i in range(4):
                frame_categoria.grid_columnconfigure(i, weight=1)
            for i in range(3):
                frame_categoria.grid_rowconfigure(i, weight=1)
            
            row, col = 0, 0
            for botao in categoria['botoes']:
                try:
                    # Verificar se tem promoção
                    from modules.produtos import ProdutoManager
                    produto_manager = ProdutoManager(self.sistema.db)
                    produto = produto_manager.obter_produto_por_codigo(botao['codigo'])
                    
                    if produto:
                        from modules.promocoes import PromocaoManager
                        promocao_manager = PromocaoManager(self.sistema.db)
                        preco_final = promocao_manager.obter_preco_com_promocao(produto['id_produto'])
                        
                        # Verificar se tem desconto
                        tem_promocao = preco_final < produto['preco_venda']
                        
                        texto_botao = f"{botao['texto']}\n"
                        if tem_promocao:
                            texto_botao += f"~~{produto['preco_venda']:.2f}~~\n"
                            texto_botao += f"🔴 {preco_final:.2f} Kz"
                        else:
                            texto_botao += f"{preco_final:.2f} Kz"
                        
                        btn = tk.Button(
                            frame_categoria,
                            text=texto_botao,
                            bg=botao['cor'],
                            fg='white',
                            font=('Arial', 10, 'bold'),
                            width=15,
                            height=4,
                            relief='raised',
                            bd=3,
                            command=lambda cod=botao['codigo']: self.adicionar_produto(cod),
                            cursor='hand2',
                            wraplength=120
                        )
                        
                        if tem_promocao:
                            btn.config(bg='#e74c3c')  # Vermelho para promoções
                        
                        btn.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
                    
                    col += 1
                    if col > 3:
                        col = 0
                        row += 1
                        
                except Exception as e:
                    print(f"Erro ao criar botão {botao['texto']}: {e}")
                    continue

    def definir_campo_ativo(self, tipo_campo):
        """Define qual campo está ativo para receber input do teclado virtual"""
        self.campo_ativo = tipo_campo
        if tipo_campo == 'codigo':
            self.valor_digitado = self.entry_codigo.get()
        elif tipo_campo == 'valor_pago':
            self.valor_digitado = self.entry_valor_pago.get() if hasattr(self, 'entry_valor_pago') else ""
        
        self.atualizar_display_teclado()
    
    def atualizar_display_teclado(self):
        """Atualiza o display do teclado virtual com o valor atual"""
        self.display_valor.config(state='normal')
        self.display_valor.delete(0, tk.END)
        self.display_valor.insert(0, self.valor_digitado)
        self.display_valor.config(state='readonly')
    
    def processar_tecla(self, tecla):
        """Processa tecla pressionada no teclado virtual"""
        self.valor_digitado = self.teclado_virtual.processar_toque(tecla, self.valor_digitado)
        self.atualizar_display_teclado()
        
        # Atualizar o campo ativo
        if self.campo_ativo == 'codigo':
            self.entry_codigo.delete(0, tk.END)
            self.entry_codigo.insert(0, self.valor_digitado)
        elif self.campo_ativo == 'valor_pago' and hasattr(self, 'entry_valor_pago'):
            self.entry_valor_pago.delete(0, tk.END)
            self.entry_valor_pago.insert(0, self.valor_digitado)
            # Recalcular troco se for o caso
            if hasattr(self, 'total_venda_atual'):
                self.calcular_troco_dinamico(self.total_venda_atual)
    
    def adicionar_por_codigo(self):
        codigo = self.entry_codigo.get().strip()
        if codigo:
            self.adicionar_produto(codigo)
            self.entry_codigo.delete(0, tk.END)
            self.valor_digitado = ""
            self.atualizar_display_teclado()
            self.entry_codigo.focus()
    
    def adicionar_produto(self, codigo_produto):
        from modules.produtos import ProdutoManager
        produto_manager = ProdutoManager(self.sistema.db)
        produto = produto_manager.obter_produto_por_codigo(codigo_produto)
        
        if not produto:
            messagebox.showerror("Erro", f"Produto não encontrado: {codigo_produto}")
            return
        
        if produto['stock_atual'] <= 0:
            messagebox.showerror("Erro", f"Produto sem stock: {produto['nome']}")
            return
        
        # Calcular preço com promoção
        from modules.promocoes import PromocaoManager
        promocao_manager = PromocaoManager(self.sistema.db)
        preco_final = promocao_manager.obter_preco_com_promocao(produto['id_produto'])
        
        # Converter para float para consistência
        preco_final_float = float(preco_final)
        preco_original_float = float(produto['preco_venda'])
        
        # Verificar se já está no carrinho
        for item in self.carrinho:
            if item['id_produto'] == produto['id_produto']:
                item['quantidade'] += 1
                break
        else:
            self.carrinho.append({
                'id_produto': produto['id_produto'],
                'nome': produto['nome'],
                'preco': preco_final_float,
                'quantidade': 1,
                'codigo_barras': produto['codigo_barras'],
                'preco_original': preco_original_float
            })
        
        self.atualizar_carrinho()
    
    def atualizar_carrinho(self):
        self.lista_carrinho.delete(0, tk.END)
        total = 0
        
        for item in self.carrinho:
            # Converter para float para evitar problemas de tipos
            preco = float(item['preco'])
            preco_original = float(item['preco_original'])
            subtotal = preco * item['quantidade']
            total += subtotal
            
            # Mostrar se tem desconto
            if preco < preco_original:
                desconto = preco_original - preco
                texto = f"{item['nome']} x{item['quantidade']} = {subtotal:.2f} Kz (🔴 -{desconto:.2f})"
            else:
                texto = f"{item['nome']} x{item['quantidade']} = {subtotal:.2f} Kz"
                
            self.lista_carrinho.insert(tk.END, texto)
        
        self.label_total.config(text=f"Total: {total:.2f} Kz")
    
    def simular_leitor_codigo_barras(self):
        """Simula um leitor de código de barras"""
        codigo = simpledialog.askstring("Leitor Código Barras", "Digite o código de barras:")
        if codigo:
            self.entry_codigo.delete(0, tk.END)
            self.entry_codigo.insert(0, codigo)
            self.adicionar_por_codigo()
    
    def editar_item_carrinho(self, event):
        """Edita item com duplo clique"""
        self.editar_item_selecionado()
    
    def editar_item_selecionado(self):
        """Edita o item selecionado no carrinho"""
        selecao = self.lista_carrinho.curselection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione um item para editar!")
            return
        
        index = selecao[0]
        if index < len(self.carrinho):
            item = self.carrinho[index]
            self.editar_quantidade_item(item, index)
    
    def remover_item_selecionado(self):
        """Remove o item selecionado do carrinho"""
        selecao = self.lista_carrinho.curselection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione um item para remover!")
            return
        
        index = selecao[0]
        if index < len(self.carrinho):
            item = self.carrinho[index]
            if messagebox.askyesno("Confirmar", f"Remover {item['nome']} do carrinho?"):
                del self.carrinho[index]
                self.atualizar_carrinho()
    
    def editar_quantidade_item(self, item, index):
        """Janela para editar quantidade do item"""
        janela = tk.Toplevel(self.root)
        janela.title(f"Editar {item['nome']}")
        janela.geometry("350x250")
        janela.transient(self.root)
        janela.grab_set()
        
        main_frame = ttk.Frame(janela, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text=item['nome'], font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Mostrar preço original e com desconto (convertido para float)
        preco = float(item['preco'])
        preco_original = float(item['preco_original'])
        
        if preco < preco_original:
            texto_preco = f"Preço: ~~{preco_original:.2f}~~ {preco:.2f} Kz 🔴 PROMOÇÃO!"
            ttk.Label(main_frame, text=texto_preco, foreground='red', font=('Arial', 11)).pack(pady=5)
        else:
            ttk.Label(main_frame, text=f"Preço: {preco:.2f} Kz", font=('Arial', 11)).pack(pady=5)
        
        frame_quantidade = ttk.Frame(main_frame)
        frame_quantidade.pack(pady=15)
        
        ttk.Label(frame_quantidade, text="Quantidade:", font=('Arial', 11)).pack(side=tk.LEFT)
        
        quantidade_var = tk.StringVar(value=str(item['quantidade']))
        spinbox = ttk.Spinbox(frame_quantidade, from_=1, to=100, textvariable=quantidade_var, 
                             width=10, font=('Arial', 11))
        spinbox.pack(side=tk.LEFT, padx=10)
        
        def confirmar():
            try:
                nova_quantidade = int(quantidade_var.get())
                if nova_quantidade > 0:
                    self.carrinho[index]['quantidade'] = nova_quantidade
                    self.atualizar_carrinho()
                    janela.destroy()
                else:
                    messagebox.showerror("Erro", "Quantidade deve ser maior que zero!")
            except ValueError:
                messagebox.showerror("Erro", "Quantidade inválida!")
        
        frame_botoes = ttk.Frame(main_frame)
        frame_botoes.pack(pady=20)
        
        ttk.Button(frame_botoes, text="✅ Confirmar", command=confirmar, 
                  width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_botoes, text="❌ Cancelar", command=janela.destroy,
                  width=12).pack(side=tk.RIGHT, padx=5)
        
        # Focar no spinbox
        spinbox.focus()
        spinbox.select_range(0, tk.END)
    
    def limpar_carrinho(self):
        if self.carrinho:
            if messagebox.askyesno("Confirmar", "Limpar carrinho?"):
                self.carrinho.clear()
                self.atualizar_carrinho()
    
    def finalizar_venda(self):
        if not self.carrinho:
            messagebox.showwarning("Aviso", "Carrinho vazio!")
            return
        
        # Criar janela de finalização
        self.criar_janela_finalizacao()
    
    def criar_janela_finalizacao(self):
        janela = tk.Toplevel(self.root)
        janela.title("Finalizar Venda")
        janela.geometry("500x600")
        janela.transient(self.root)
        janela.grab_set()
        
        # Calcular total
        total = sum(item['preco'] * item['quantidade'] for item in self.carrinho)
        self.total_venda_atual = total
        
        main_frame = ttk.Frame(janela, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="FINALIZAR VENDA", 
                 font=('Arial', 16, 'bold')).pack(pady=10)
        
        # Resumo com destaque para promoções
        frame_resumo = ttk.LabelFrame(main_frame, text="Resumo da Venda", padding=10)
        frame_resumo.pack(fill=tk.X, pady=10)
        
        for item in self.carrinho:
            subtotal = item['preco'] * item['quantidade']
            if item['preco'] < item['preco_original']:
                texto = f"{item['nome']} x{item['quantidade']} = {subtotal:.2f} Kz 🔴"
                label = ttk.Label(frame_resumo, text=texto)
                label.pack(anchor=tk.W)
                # Mudar cor para vermelho manualmente
                try:
                    label.configure(foreground='red')
                except:
                    pass
            else:
                texto = f"{item['nome']} x{item['quantidade']} = {subtotal:.2f} Kz"
                ttk.Label(frame_resumo, text=texto).pack(anchor=tk.W)
        
        ttk.Label(frame_resumo, text=f"TOTAL: {total:.2f} Kz", 
                 font=('Arial', 12, 'bold'), foreground='green').pack(anchor=tk.W, pady=(10, 0))
        
        # Forma de pagamento
        frame_pagamento = ttk.LabelFrame(main_frame, text="Forma de Pagamento", padding=10)
        frame_pagamento.pack(fill=tk.X, pady=10)
        
        self.forma_pagamento = tk.StringVar(value='dinheiro')
        
        formas = [
            ('💵 Dinheiro', 'dinheiro'),
            ('💳 Multicaixa', 'multicaixa'),
            ('🏦 Transferência', 'transferencia'),
            ('📄 Outro', 'outro')
        ]
        
        # Usar tk.Radiobutton em vez de ttk.Radiobutton para suportar font
        for texto, valor in formas:
            rb = tk.Radiobutton(
                frame_pagamento, 
                text=texto, 
                variable=self.forma_pagamento, 
                value=valor,
                font=('Arial', 10),
                anchor='w'
            )
            rb.pack(anchor=tk.W, pady=2, fill='x')
        
        # Valor pago (apenas para dinheiro)
        frame_valor = ttk.LabelFrame(main_frame, text="Valor Pago", padding=10)
        frame_valor.pack(fill=tk.X, pady=10)
        
        self.entry_valor_pago = ttk.Entry(
            frame_valor, 
            font=('Arial', 16), 
            justify='center'
        )
        self.entry_valor_pago.pack(fill=tk.X, pady=5, ipady=8)
        self.entry_valor_pago.insert(0, f"{total:.2f}")
        self.entry_valor_pago.bind('<FocusIn>', lambda e: self.definir_campo_ativo('valor_pago'))
        
        self.label_troco = ttk.Label(
            frame_valor, 
            text="",
            font=('Arial', 12, 'bold')
        )
        self.label_troco.pack(pady=5)
        # Configurar cor azul manualmente
        try:
            self.label_troco.configure(foreground='blue')
        except:
            pass
        
        # Botões
        frame_botoes = ttk.Frame(main_frame)
        frame_botoes.pack(fill=tk.X, pady=20)
        
        ttk.Button(
            frame_botoes, 
            text="✅ CONFIRMAR VENDA", 
            command=lambda: self.confirmar_venda(janela, total)
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            frame_botoes, 
            text="❌ CANCELAR", 
            command=janela.destroy
        ).pack(side=tk.RIGHT)
        
        # Bind events para cálculo dinâmico do troco
        self.entry_valor_pago.bind('<KeyRelease>', 
                                 lambda e: self.calcular_troco_dinamico(total))
        self.forma_pagamento.trace('w', 
                                 lambda *args: self.calcular_troco_dinamico(total))
        
        # Calcular troco inicial
        self.calcular_troco_dinamico(total)
        
        # Focar no campo de valor pago
        self.entry_valor_pago.focus()
        self.entry_valor_pago.select_range(0, tk.END)
    
    def calcular_troco_dinamico(self, total):
        try:
            valor_pago_texto = self.entry_valor_pago.get().strip()
            if not valor_pago_texto:
                self.label_troco.config(text="")
                return
                
            valor_pago = float(valor_pago_texto)
            forma_pagamento = self.forma_pagamento.get()
            
            # Usar a calculadora de troco
            troco, mensagem = self.calculadora_troco.calcular_troco(
                total, valor_pago, forma_pagamento
            )
            
            if troco is None:
                # Erro - mostrar em vermelho
                self.label_troco.config(text=mensagem)
                try:
                    self.label_troco.configure(foreground='red')
                except:
                    pass
            else:
                # Sucesso - mostrar em azul ou verde
                self.label_troco.config(text=mensagem)
                if troco > 0:
                    try:
                        self.label_troco.configure(foreground='green')
                    except:
                        pass
                else:
                    try:
                        self.label_troco.configure(foreground='blue')
                    except:
                        pass
            
        except ValueError:
            self.label_troco.config(text="Valor inválido")
            try:
                self.label_troco.configure(foreground='red')
            except:
                pass
    
    def confirmar_venda(self, janela, total):
        try:
            forma_pagamento = self.forma_pagamento.get()
            valor_pago_texto = self.entry_valor_pago.get().strip()
            
            if not valor_pago_texto:
                messagebox.showerror("Erro", "Digite o valor pago!")
                self.entry_valor_pago.focus()
                return
                
            valor_pago = float(valor_pago_texto)
            
            # Verificar troco
            if forma_pagamento == 'dinheiro':
                troco, mensagem = self.calculadora_troco.calcular_troco(
                    total, valor_pago, forma_pagamento
                )
                if troco is None:
                    messagebox.showerror("Erro", mensagem)
                    self.entry_valor_pago.focus()
                    self.entry_valor_pago.select_range(0, tk.END)
                    return
            else:
                if valor_pago > total:
                    messagebox.showerror("Erro", 
                                       "Não é permitido troco em pagamentos não monetários")
                    self.entry_valor_pago.focus()
                    self.entry_valor_pago.select_range(0, tk.END)
                    return
            
            # Criar venda no banco de dados
            from modules.vendas import VendaManager
            venda_manager = VendaManager(self.sistema.db)
            
            # Preparar itens para a venda
            itens_venda = []
            for item in self.carrinho:
                itens_venda.append({
                    'id_produto': item['id_produto'],
                    'nome': item['nome'],
                    'preco': item['preco'],
                    'quantidade': item['quantidade']
                })
            
            # Usar ID do vendedor autenticado
            id_vendedor = self.vendedor_autenticado['id_usuario']
            
            id_venda, numero_venda = venda_manager.criar_venda(
                id_vendedor, 
                itens_venda, 
                0,  # desconto
                forma_pagamento
            )
            
            if id_venda:
                # Gerar recibo
                from modules.impressora import ImpressoraManager
                impressora = ImpressoraManager(self.sistema.config)
                
                # Calcular troco final
                troco_final = valor_pago - total if forma_pagamento == 'dinheiro' else 0
                
                dados_venda = {
                    'numero_venda': numero_venda,
                    'data': datetime.now().strftime('%d/%m/%Y %H:%M'),
                    'vendedor': self.vendedor_autenticado['nome'],
                    'itens': [],
                    'total': total,
                    'desconto': 0,
                    'total_final': total,
                    'forma_pagamento': forma_pagamento,
                    'troco': troco_final
                }
                
                # Preparar itens para o recibo
                for item in self.carrinho:
                    dados_venda['itens'].append({
                        'nome': item['nome'],
                        'quantidade': item['quantidade'],
                        'preco': item['preco'],
                        'total_item': item['preco'] * item['quantidade']
                    })
                
                texto_recibo = impressora.gerar_texto_recibo(dados_venda)
                
                # Guardar recibo em arquivo
                self.guardar_recibo_arquivo(numero_venda, texto_recibo)
                
                # Imprimir recibo
                sucesso_impressao = impressora.imprimir_recibo(texto_recibo)
                
                if sucesso_impressao:
                    messagebox.showinfo("Sucesso", 
                                      f"Venda realizada com sucesso!\nRecibo: {numero_venda}\nRecibo guardado e impresso.")
                else:
                    messagebox.showwarning("Aviso", 
                                         f"Venda realizada mas erro na impressão!\nRecibo: {numero_venda}\nRecibo guardado em arquivo.")
                
                # Limpar carrinho e fechar janela
                self.carrinho.clear()
                self.atualizar_carrinho()
                janela.destroy()
                
                # Reproduzir som de sucesso
                self.reproduzir_som_venda()
            
            else:
                messagebox.showerror("Erro", "Erro ao registrar venda no sistema!")
                
        except ValueError:
            messagebox.showerror("Erro", "Valor pago inválido!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar venda: {e}")
    
    def guardar_recibo_arquivo(self, numero_venda, texto_recibo):
        """Guarda o recibo em arquivo texto"""
        try:
            nome_arquivo = f"recibos/recibo_{numero_venda}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(nome_arquivo, 'w', encoding='utf-8') as f:
                f.write(texto_recibo)
            print(f"✓ Recibo guardado em: {nome_arquivo}")
        except Exception as e:
            print(f"✗ Erro ao guardar recibo: {e}")
    
    def reproduzir_som_venda(self):
        """Reproduz som de venda concluída se configurado"""
        if self.sistema.config.dados['sistema']['som_ativo']:
            try:
                # Simulação de som - pode ser implementado com pygame
                print("🔊 Som de venda concluída")
            except:
                pass
    
    def mostrar_configuracoes_rapidas(self):
        """Mostra configurações rápidas"""
        janela = tk.Toplevel(self.root)
        janela.title("Configurações Rápidas")
        janela.geometry("400x300")
        janela.transient(self.root)
        janela.grab_set()
        
        main_frame = ttk.Frame(janela, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Configurações Rápidas", font=('Arial', 16, 'bold')).pack(pady=10)
        
        # Testar impressora
        ttk.Button(
            main_frame, 
            text="🖨️ Testar Impressora", 
            command=self.testar_impressora,
            width=20
        ).pack(pady=5)
        
        # Ver stock
        ttk.Button(
            main_frame, 
            text="📦 Ver Stock Baixo", 
            command=self.ver_stock_baixo,
            width=20
        ).pack(pady=5)
        
        # Trocar vendedor
        ttk.Button(
            main_frame, 
            text="👤 Trocar Vendedor", 
            command=self.trocar_vendedor,
            width=20
        ).pack(pady=5)
        
        # Ver promoções ativas
        ttk.Button(
            main_frame, 
            text="🏷️ Ver Promoções Ativas", 
            command=self.ver_promocoes_ativas,
            width=20
        ).pack(pady=5)
        
        ttk.Button(
            main_frame, 
            text="Fechar", 
            command=janela.destroy
        ).pack(pady=20)
    
    def testar_impressora(self):
        """Testa a impressora"""
        from modules.impressora import ImpressoraManager
        impressora = ImpressoraManager(self.sistema.config)
        if impressora.testar_impressora():
            messagebox.showinfo("Sucesso", "Teste de impressora realizado!")
        else:
            messagebox.showerror("Erro", "Falha no teste de impressora!")
    
    def ver_stock_baixo(self):
        """Mostra produtos com stock baixo"""
        from modules.produtos import ProdutoManager
        produto_manager = ProdutoManager(self.sistema.db)
        produtos_baixo_stock = produto_manager.obter_produtos_baixo_stock()
        
        if not produtos_baixo_stock:
            messagebox.showinfo("Stock", "Nenhum produto com stock baixo!")
            return
        
        janela = tk.Toplevel(self.root)
        janela.title("Produtos com Stock Baixo")
        janela.geometry("500x400")
        
        frame = ttk.Frame(janela, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Produtos com Stock Baixo", font=('Arial', 14, 'bold')).pack(pady=10)
        
        tree = ttk.Treeview(frame, columns=('Produto', 'Stock Atual', 'Stock Mínimo'), show='headings', height=15)
        tree.heading('Produto', text='Produto')
        tree.heading('Stock Atual', text='Stock Atual')
        tree.heading('Stock Mínimo', text='Stock Mínimo')
        
        for produto in produtos_baixo_stock:
            tree.insert('', tk.END, values=(
                produto['nome'],
                produto['stock_atual'],
                produto['stock_minimo']
            ))
        
        tree.pack(fill=tk.BOTH, expand=True)
    
    def ver_promocoes_ativas(self):
        """Mostra promoções ativas"""
        from modules.promocoes import PromocaoManager
        promocao_manager = PromocaoManager(self.sistema.db)
        
        try:
            promocoes = promocao_manager.obter_promocoes_ativas()
        except AttributeError:
            # Fallback se o método não existir
            messagebox.showinfo("Promoções", "Funcionalidade em desenvolvimento!")
            return
        
        if not promocoes:
            messagebox.showinfo("Promoções", "Nenhuma promoção ativa no momento!")
            return
        
        janela = tk.Toplevel(self.root)
        janela.title("Promoções Ativas")
        janela.geometry("600x400")
        
        frame = ttk.Frame(janela, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Promoções Ativas", font=('Arial', 14, 'bold')).pack(pady=10)
        
        tree = ttk.Treeview(frame, columns=('Produto', 'Promoção', 'Desconto', 'Preço Promoção', 'Válida Até'), show='headings', height=15)
        tree.heading('Produto', text='Produto')
        tree.heading('Promoção', text='Promoção')
        tree.heading('Desconto', text='Desconto')
        tree.heading('Preço Promoção', text='Preço Promoção')
        tree.heading('Válida Até', text='Válida Até')
        
        for promocao in promocoes:
            if promocao.get('preco_promocao'):
                desconto = f"Preço Fixo: {promocao['preco_promocao']:.2f} Kz"
                preco_promo = f"{promocao['preco_promocao']:.2f} Kz"
            else:
                desconto = f"{promocao.get('desconto_percentual', 0):.1f}%"
                preco_normal = promocao.get('preco_normal', 0)
                preco_promo = preco_normal * (1 - promocao.get('desconto_percentual', 0) / 100)
                preco_promo = f"{preco_promo:.2f} Kz"
            
            data_fim = promocao['data_fim'].strftime('%d/%m/%Y') if hasattr(promocao['data_fim'], 'strftime') else str(promocao['data_fim'])[:10]
            
            tree.insert('', tk.END, values=(
                promocao.get('nome_produto', 'N/A'),
                promocao.get('nome_promocao', 'N/A'),
                desconto,
                preco_promo,
                data_fim
            ))
        
        tree.pack(fill=tk.BOTH, expand=True)
    
    def trocar_vendedor(self):
        """Permite trocar de vendedor"""
        if messagebox.askyesno("Trocar Vendedor", "Deseja trocar de vendedor?"):
            self.autenticar_vendedor()
    
    def mostrar_relatorio_diario(self):
        """Mostra relatório diário detalhado"""
        from modules.vendas import VendaManager
        venda_manager = VendaManager(self.sistema.db)
        
        hoje = datetime.now().strftime('%Y-%m-%d')
        vendas_hoje = venda_manager.obter_vendas_periodo(hoje + " 00:00:00", hoje + " 23:59:59")
        
        janela = tk.Toplevel(self.root)
        janela.title("Relatório Diário")
        janela.geometry("600x500")
        
        frame = ttk.Frame(janela, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text=f"Relatório Diário - {datetime.now().strftime('%d/%m/%Y')}", 
                 font=('Arial', 16, 'bold')).pack(pady=10)
        
        # Resumo
        total_vendas = len(vendas_hoje)
        valor_total = sum(venda['total_final'] for venda in vendas_hoje) if vendas_hoje else 0
        
        frame_resumo = ttk.LabelFrame(frame, text="Resumo", padding=10)
        frame_resumo.pack(fill=tk.X, pady=10)
        
        ttk.Label(frame_resumo, text=f"Total de Vendas: {total_vendas}").pack(anchor=tk.W)
        ttk.Label(frame_resumo, text=f"Valor Total: {valor_total:.2f} Kz", 
                 font=('Arial', 12, 'bold')).pack(anchor=tk.W)
        
        # Lista de vendas
        if vendas_hoje:
            frame_vendas = ttk.LabelFrame(frame, text="Últimas Vendas", padding=10)
            frame_vendas.pack(fill=tk.BOTH, expand=True, pady=10)
            
            tree = ttk.Treeview(frame_vendas, columns=('Hora', 'Recibo', 'Valor', 'Pagamento'), show='headings', height=10)
            tree.heading('Hora', text='Hora')
            tree.heading('Recibo', text='Recibo')
            tree.heading('Valor', text='Valor')
            tree.heading('Pagamento', text='Pagamento')
            
            for venda in vendas_hoje[:10]:
                hora = venda['data_venda'].strftime('%H:%M') if hasattr(venda['data_venda'], 'strftime') else venda['data_venda']
                tree.insert('', tk.END, values=(
                    hora,
                    venda['numero_venda'],
                    f"{venda['total_final']:.2f} Kz",
                    venda['forma_pagamento']
                ))
            
            tree.pack(fill=tk.BOTH, expand=True)
    
    def executar(self):
        self.root.mainloop()