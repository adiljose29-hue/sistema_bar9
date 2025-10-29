import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta

class InterfaceGerente:
    def __init__(self, sistema):
        self.sistema = sistema
        self.usuario = None
        self.root = tk.Tk()
        self.root.title("Sistema de Gestão - Gerente")
        self.root.geometry("1200x700")
        self.root.minsize(1000, 600)
        
        self.criar_interface()
    
    def criar_interface(self):
        # Configurar estilo
        self.configurar_estilo()
        
        # Frame principal
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Barra superior
        self.criar_barra_superior(main_frame)
        
        # Notebook (abas)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Criar abas
        self.criar_aba_dashboard()
        self.criar_aba_produtos()
        self.criar_aba_promocoes()
        self.criar_aba_vendas()
        self.criar_aba_usuarios()
        self.criar_aba_configuracoes()
    
    def configurar_estilo(self):
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Subtitle.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Accent.TButton', font=('Arial', 10, 'bold'))
    
    def criar_barra_superior(self, parent):
        frame_barra = ttk.Frame(parent)
        frame_barra.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(
            frame_barra, 
            text="SISTEMA DE GESTÃO - GERENTE", 
            style='Title.TLabel'
        ).pack(side=tk.LEFT)
        
        self.label_usuario = ttk.Label(
            frame_barra, 
            text="Usuário: Não autenticado",
            font=('Arial', 10)
        )
        self.label_usuario.pack(side=tk.RIGHT)
        
        ttk.Button(
            frame_barra, 
            text="Sair", 
            command=self.root.quit
        ).pack(side=tk.RIGHT, padx=(10, 0))
    
    def criar_aba_dashboard(self):
        frame_dashboard = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(frame_dashboard, text="Dashboard")
        
        # Frame de resumo
        frame_resumo = ttk.LabelFrame(frame_dashboard, text="Resumo do Dia", padding=10)
        frame_resumo.pack(fill=tk.X, pady=10)
        
        # Buscar dados reais
        from modules.vendas import VendaManager
        venda_manager = VendaManager(self.sistema.db)
        
        hoje = datetime.now().strftime('%Y-%m-%d')
        vendas_hoje = venda_manager.obter_vendas_periodo(hoje + " 00:00:00", hoje + " 23:59:59")
        
        total_vendas = len(vendas_hoje)
        valor_total = sum(venda['total_final'] for venda in vendas_hoje) if vendas_hoje else 0
        
        # Buscar produtos com stock baixo
        from modules.produtos import ProdutoManager
        produto_manager = ProdutoManager(self.sistema.db)
        produtos_baixo_stock = produto_manager.obter_produtos_baixo_stock()
        total_baixo_stock = len(produtos_baixo_stock)
        
        # Calcular total de produtos vendidos
        total_produtos_vendidos = 0
        for venda in vendas_hoje:
            itens = venda_manager.obter_itens_venda(venda['id_venda'])
            total_produtos_vendidos += sum(item['quantidade'] for item in itens) if itens else 0
        
        # Criar widgets de resumo com dados reais
        col = 0
        metricas = [
            ("Vendas Hoje", str(total_vendas), "#3498db"),
            (f"Receita Total", f"{valor_total:.2f} Kz", "#2ecc71"),
            ("Produtos Vendidos", str(total_produtos_vendidos), "#e74c3c"),
            ("Stock Baixo", str(total_baixo_stock), "#f39c12")
        ]
        
        for texto, valor, cor in metricas:
            frame_metrica = ttk.Frame(frame_resumo, relief='raised', borderwidth=1)
            frame_metrica.grid(row=0, column=col, padx=10, pady=5, sticky='nsew')
            
            ttk.Label(
                frame_metrica, 
                text=texto, 
                font=('Arial', 10)
            ).pack(pady=5)
            
            ttk.Label(
                frame_metrica, 
                text=valor, 
                font=('Arial', 16, 'bold'),
                foreground=cor
            ).pack(pady=5)
            
            col += 1
        
        frame_resumo.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Frame últimas vendas
        frame_graficos = ttk.LabelFrame(frame_dashboard, text="Últimas Vendas", padding=10)
        frame_graficos.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Treeview para últimas vendas
        colunas = ('Data', 'Recibo', 'Vendedor', 'Total', 'Pagamento')
        tree_vendas = ttk.Treeview(frame_graficos, columns=colunas, show='headings', height=10)
        
        for col in colunas:
            tree_vendas.heading(col, text=col)
            tree_vendas.column(col, width=120)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(frame_graficos, orient=tk.VERTICAL, command=tree_vendas.yview)
        tree_vendas.configure(yscrollcommand=scrollbar.set)
        
        tree_vendas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Adicionar vendas reais
        for venda in vendas_hoje[:10]:  # Últimas 10 vendas
            data_formatada = venda['data_venda'].strftime('%d/%m %H:%M') if hasattr(venda['data_venda'], 'strftime') else venda['data_venda']
            tree_vendas.insert('', tk.END, values=(
                data_formatada,
                venda['numero_venda'],
                venda.get('nome_vendedor', 'N/A'),
                f"{venda['total_final']:.2f} Kz",
                venda['forma_pagamento']
            ))
    
    def criar_aba_produtos(self):
        frame_produtos = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(frame_produtos, text="Gestão de Produtos")
        
        # Frame de controles
        frame_controles = ttk.Frame(frame_produtos)
        frame_controles.pack(fill=tk.X, pady=10)
        
        ttk.Button(
            frame_controles, 
            text="Novo Produto", 
            command=self.novo_produto,
            style='Accent.TButton'
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            frame_controles, 
            text="Atualizar Stock", 
            command=self.atualizar_stock
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            frame_controles, 
            text="Exportar", 
            command=self.exportar_produtos
        ).pack(side=tk.LEFT)
        
        # Frame pesquisa
        frame_pesquisa = ttk.Frame(frame_produtos)
        frame_pesquisa.pack(fill=tk.X, pady=10)
        
        ttk.Label(frame_pesquisa, text="Pesquisar:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.entry_pesquisa_produtos = ttk.Entry(frame_pesquisa, width=30)
        self.entry_pesquisa_produtos.pack(side=tk.LEFT, padx=(0, 10))
        self.entry_pesquisa_produtos.bind('<Return>', lambda e: self.pesquisar_produtos())
        
        ttk.Button(
            frame_pesquisa, 
            text="Pesquisar", 
            command=self.pesquisar_produtos
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            frame_pesquisa, 
            text="Limpar", 
            command=self.limpar_pesquisa_produtos
        ).pack(side=tk.LEFT)
        
        # Treeview de produtos
        frame_tree = ttk.Frame(frame_produtos)
        frame_tree.pack(fill=tk.BOTH, expand=True)
        
        colunas = ('ID', 'Código', 'Nome', 'Preço', 'Stock', 'Categoria', 'Status')
        self.tree_produtos = ttk.Treeview(frame_tree, columns=colunas, show='headings', height=15)
        
        for col in colunas:
            self.tree_produtos.heading(col, text=col)
            self.tree_produtos.column(col, width=100)
        
        # Scrollbars
        scrollbar_v = ttk.Scrollbar(frame_tree, orient=tk.VERTICAL, command=self.tree_produtos.yview)
        scrollbar_h = ttk.Scrollbar(frame_tree, orient=tk.HORIZONTAL, command=self.tree_produtos.xview)
        self.tree_produtos.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
        
        self.tree_produtos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_h.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Carregar produtos
        self.carregar_produtos()
    
    def criar_aba_promocoes(self):
        """Cria aba para gestão de promoções"""
        frame_promocoes = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(frame_promocoes, text="Gestão de Promoções")
        
        # Frame de controles
        frame_controles = ttk.Frame(frame_promocoes)
        frame_controles.pack(fill=tk.X, pady=10)
        
        ttk.Button(
            frame_controles, 
            text="Nova Promoção", 
            command=self.nova_promocao,
            style='Accent.TButton'
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            frame_controles, 
            text="Atualizar", 
            command=self.carregar_promocoes
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        # Frame de promoções ativas
        frame_ativas = ttk.LabelFrame(frame_promocoes, text="Promoções Ativas", padding=10)
        frame_ativas.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Treeview de promoções
        colunas = ('ID', 'Produto', 'Nome Promoção', 'Tipo', 'Valor', 'Início', 'Fim', 'Status')
        self.tree_promocoes = ttk.Treeview(frame_ativas, columns=colunas, show='headings', height=15)
        
        for col in colunas:
            self.tree_promocoes.heading(col, text=col)
            self.tree_promocoes.column(col, width=100)
        
        # Scrollbars
        scrollbar_v = ttk.Scrollbar(frame_ativas, orient=tk.VERTICAL, command=self.tree_promocoes.yview)
        scrollbar_h = ttk.Scrollbar(frame_ativas, orient=tk.HORIZONTAL, command=self.tree_promocoes.xview)
        self.tree_promocoes.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
        
        self.tree_promocoes.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_h.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Frame de ações
        frame_acoes = ttk.Frame(frame_ativas)
        frame_acoes.pack(fill=tk.X, pady=5)
        
        ttk.Button(frame_acoes, text="Editar Promoção", 
                  command=self.editar_promocao).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_acoes, text="Desativar Promoção", 
                  command=self.desativar_promocao).pack(side=tk.LEFT, padx=5)
        
        # Carregar promoções
        self.carregar_promocoes()
    
    def criar_aba_vendas(self):
        frame_vendas = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(frame_vendas, text="Relatórios de Vendas")
        
        # Frame filtros
        frame_filtros = ttk.LabelFrame(frame_vendas, text="Filtros", padding=10)
        frame_filtros.pack(fill=tk.X, pady=10)
        
        ttk.Label(frame_filtros, text="Data Início:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.entry_data_inicio = ttk.Entry(frame_filtros, width=12)
        self.entry_data_inicio.grid(row=0, column=1, padx=5, pady=5)
        self.entry_data_inicio.insert(0, datetime.now().strftime('%Y-%m-%d'))
        
        ttk.Label(frame_filtros, text="Data Fim:").grid(row=0, column=2, padx=5, pady=5, sticky='w')
        self.entry_data_fim = ttk.Entry(frame_filtros, width=12)
        self.entry_data_fim.grid(row=0, column=3, padx=5, pady=5)
        self.entry_data_fim.insert(0, datetime.now().strftime('%Y-%m-%d'))
        
        ttk.Button(
            frame_filtros, 
            text="Buscar", 
            command=self.buscar_vendas,
            style='Accent.TButton'
        ).grid(row=0, column=4, padx=10, pady=5)
        
        ttk.Button(
            frame_filtros, 
            text="Hoje", 
            command=self.filtrar_hoje
        ).grid(row=0, column=5, padx=5, pady=5)
        
        # Treeview de vendas
        frame_tree = ttk.Frame(frame_vendas)
        frame_tree.pack(fill=tk.BOTH, expand=True)
        
        colunas = ('Data', 'Recibo', 'Vendedor', 'Total', 'Desconto', 'Total Final', 'Pagamento')
        self.tree_vendas = ttk.Treeview(frame_tree, columns=colunas, show='headings', height=15)
        
        for col in colunas:
            self.tree_vendas.heading(col, text=col)
            self.tree_vendas.column(col, width=100)
        
        # Scrollbars
        scrollbar_v = ttk.Scrollbar(frame_tree, orient=tk.VERTICAL, command=self.tree_vendas.yview)
        scrollbar_h = ttk.Scrollbar(frame_tree, orient=tk.HORIZONTAL, command=self.tree_vendas.xview)
        self.tree_vendas.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
        
        self.tree_vendas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_h.pack(side=tk.BOTTOM, fill=tk.X)
    
    def criar_aba_usuarios(self):
        frame_usuarios = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(frame_usuarios, text="Gestão de Usuários")
        
        # Frame de controles
        frame_controles = ttk.Frame(frame_usuarios)
        frame_controles.pack(fill=tk.X, pady=10)
        
        ttk.Button(
            frame_controles, 
            text="Novo Usuário", 
            command=self.novo_usuario,
            style='Accent.TButton'
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            frame_controles, 
            text="Atualizar", 
            command=self.carregar_usuarios
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        # Treeview de usuários
        frame_tree = ttk.Frame(frame_usuarios)
        frame_tree.pack(fill=tk.BOTH, expand=True)
        
        colunas = ('ID', 'Nº Trabalhador', 'Nome', 'Tipo', 'Status')
        self.tree_usuarios = ttk.Treeview(frame_tree, columns=colunas, show='headings', height=15)
        
        for col in colunas:
            self.tree_usuarios.heading(col, text=col)
            self.tree_usuarios.column(col, width=120)
        
        # Scrollbars
        scrollbar_v = ttk.Scrollbar(frame_tree, orient=tk.VERTICAL, command=self.tree_usuarios.yview)
        scrollbar_h = ttk.Scrollbar(frame_tree, orient=tk.HORIZONTAL, command=self.tree_usuarios.xview)
        self.tree_usuarios.configure(yscrollcommand=scrollbar_v.set, xscrollcommand=scrollbar_h.set)
        
        self.tree_usuarios.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_h.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Carregar usuários
        self.carregar_usuarios()
    
    def criar_aba_configuracoes(self):
        frame_config = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(frame_config, text="Configurações")
        
        ttk.Label(frame_config, text="Configurações do Sistema", style='Title.TLabel').pack(pady=10)
        
        # Notebook para diferentes configurações
        config_notebook = ttk.Notebook(frame_config)
        config_notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Aba Impressora
        frame_impressora = ttk.Frame(config_notebook, padding=10)
        config_notebook.add(frame_impressora, text="Impressora")
        
        self.criar_config_impressora(frame_impressora)
        
        # Aba Sistema
        frame_sistema = ttk.Frame(config_notebook, padding=10)
        config_notebook.add(frame_sistema, text="Sistema")
        
        self.criar_config_sistema(frame_sistema)
        
        # Aba Empresa
        frame_empresa = ttk.Frame(config_notebook, padding=10)
        config_notebook.add(frame_empresa, text="Empresa")
        
        self.criar_config_empresa(frame_empresa)
    
    def criar_config_impressora(self, parent):
        """Configurações da impressora"""
        # Tipo de impressora
        frame_tipo = ttk.LabelFrame(parent, text="Tipo de Impressora", padding=10)
        frame_tipo.pack(fill=tk.X, pady=5)
        
        self.tipo_impressora = tk.StringVar(value=self.sistema.config.dados['impressora']['tipo'])
        
        tipos = [
            ('Windows', 'windows'),
            ('USB', 'usb'),
            ('Ethernet', 'ethernet'),
            ('ESC/POS', 'escpos')
        ]
        
        for texto, valor in tipos:
            ttk.Radiobutton(frame_tipo, text=texto, variable=self.tipo_impressora, 
                           value=valor).pack(anchor=tk.W, pady=2)
        
        # Configurações específicas
        frame_detalhes = ttk.LabelFrame(parent, text="Configurações Detalhadas", padding=10)
        frame_detalhes.pack(fill=tk.X, pady=5)
        
        # Windows
        ttk.Label(frame_detalhes, text="Nome Impressora Windows:").grid(row=0, column=0, sticky='w', pady=2)
        self.entry_nome_impressora = ttk.Entry(frame_detalhes, width=30)
        self.entry_nome_impressora.insert(0, self.sistema.config.dados['impressora']['nome_impressora_windows'])
        self.entry_nome_impressora.grid(row=0, column=1, pady=2, padx=5)
        
        # USB
        ttk.Label(frame_detalhes, text="Porta USB:").grid(row=1, column=0, sticky='w', pady=2)
        self.entry_porta_usb = ttk.Entry(frame_detalhes, width=30)
        self.entry_porta_usb.insert(0, self.sistema.config.dados['impressora']['porta_usb'])
        self.entry_porta_usb.grid(row=1, column=1, pady=2, padx=5)
        
        # Ethernet
        ttk.Label(frame_detalhes, text="Endereço Ethernet:").grid(row=2, column=0, sticky='w', pady=2)
        self.entry_ethernet = ttk.Entry(frame_detalhes, width=30)
        self.entry_ethernet.insert(0, self.sistema.config.dados['impressora']['porta_ethernet'])
        self.entry_ethernet.grid(row=2, column=1, pady=2, padx=5)
        
        # Opções
        frame_opcoes = ttk.LabelFrame(parent, text="Opções", padding=10)
        frame_opcoes.pack(fill=tk.X, pady=5)
        
        self.corte_automatico = tk.BooleanVar(value=self.sistema.config.dados['impressora']['corte_automatico'])
        ttk.Checkbutton(frame_opcoes, text="Corte Automático de Papel", 
                       variable=self.corte_automatico).pack(anchor=tk.W)
        
        self.abrir_gaveta = tk.BooleanVar(value=self.sistema.config.dados['impressora'].get('abrir_gaveta', True))
        ttk.Checkbutton(frame_opcoes, text="Abrir Gaveta de Dinheiro", 
                       variable=self.abrir_gaveta).pack(anchor=tk.W)
        
        # Botões de ação
        frame_acoes = ttk.Frame(parent)
        frame_acoes.pack(fill=tk.X, pady=10)
        
        ttk.Button(frame_acoes, text="Testar Impressora", 
                  command=self.testar_impressora_config).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(frame_acoes, text="Listar Impressoras", 
                  command=self.listar_impressoras).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(frame_acoes, text="Salvar Configurações", 
                  command=self.salvar_config_impressora, style='Accent.TButton').pack(side=tk.RIGHT, padx=5)
    
    def criar_config_sistema(self, parent):
        """Configurações do sistema"""
        ttk.Label(parent, text="Configurações Gerais do Sistema", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        frame_configs = ttk.Frame(parent)
        frame_configs.pack(fill=tk.X, pady=10)
        
        # Moeda
        ttk.Label(frame_configs, text="Moeda:").grid(row=0, column=0, sticky='w', pady=5)
        self.entry_moeda = ttk.Entry(frame_configs, width=10)
        self.entry_moeda.insert(0, self.sistema.config.dados['sistema']['moeda'])
        self.entry_moeda.grid(row=0, column=1, pady=5, padx=5, sticky='w')
        
        # Símbolo da Moeda
        ttk.Label(frame_configs, text="Símbolo Moeda:").grid(row=0, column=2, sticky='w', pady=5)
        self.entry_simbolo_moeda = ttk.Entry(frame_configs, width=10)
        self.entry_simbolo_moeda.insert(0, self.sistema.config.dados['sistema']['simbolo_moeda'])
        self.entry_simbolo_moeda.grid(row=0, column=3, pady=5, padx=5, sticky='w')
        
        # Opções
        frame_opcoes = ttk.LabelFrame(parent, text="Opções do Sistema", padding=10)
        frame_opcoes.pack(fill=tk.X, pady=10)
        
        self.ativo_desconto = tk.BooleanVar(value=self.sistema.config.dados['sistema']['ativo_desconto'])
        ttk.Checkbutton(frame_opcoes, text="Ativar Descontos", 
                       variable=self.ativo_desconto).pack(anchor=tk.W)
        
        self.ativo_multiforma = tk.BooleanVar(value=self.sistema.config.dados['sistema']['ativo_multiforma_pagamento'])
        ttk.Checkbutton(frame_opcoes, text="Múltiplas Formas de Pagamento", 
                       variable=self.ativo_multiforma).pack(anchor=tk.W)
        
        self.controlo_stock = tk.BooleanVar(value=self.sistema.config.dados['sistema']['controlo_stock'])
        ttk.Checkbutton(frame_opcoes, text="Controlo de Stock", 
                       variable=self.controlo_stock).pack(anchor=tk.W)
        
        self.som_ativo = tk.BooleanVar(value=self.sistema.config.dados['sistema']['som_ativo'])
        ttk.Checkbutton(frame_opcoes, text="Som Ativo", 
                       variable=self.som_ativo).pack(anchor=tk.W)
        
        # Botão salvar
        ttk.Button(parent, text="Salvar Configurações do Sistema", 
                  command=self.salvar_config_sistema, style='Accent.TButton').pack(pady=20)
    
    def criar_config_empresa(self, parent):
        """Configurações da empresa"""
        ttk.Label(parent, text="Dados da Empresa", 
                 font=('Arial', 12, 'bold')).pack(pady=10)
        
        empresa = self.sistema.config.dados['recibo']['empresa']
        
        frame_dados = ttk.Frame(parent)
        frame_dados.pack(fill=tk.X, pady=10)
        
        # Nome da Empresa
        ttk.Label(frame_dados, text="Nome da Empresa:").grid(row=0, column=0, sticky='w', pady=5)
        self.entry_nome_empresa = ttk.Entry(frame_dados, width=40)
        self.entry_nome_empresa.insert(0, empresa['nome'])
        self.entry_nome_empresa.grid(row=0, column=1, pady=5, padx=5, sticky='w')
        
        # NIF
        ttk.Label(frame_dados, text="NIF:").grid(row=1, column=0, sticky='w', pady=5)
        self.entry_nif_empresa = ttk.Entry(frame_dados, width=20)
        self.entry_nif_empresa.insert(0, empresa['nif'])
        self.entry_nif_empresa.grid(row=1, column=1, pady=5, padx=5, sticky='w')
        
        # Endereço
        ttk.Label(frame_dados, text="Endereço:").grid(row=2, column=0, sticky='w', pady=5)
        self.entry_endereco_empresa = ttk.Entry(frame_dados, width=40)
        self.entry_endereco_empresa.insert(0, empresa['endereco'])
        self.entry_endereco_empresa.grid(row=2, column=1, pady=5, padx=5, sticky='w')
        
        # Telefone
        ttk.Label(frame_dados, text="Telefone:").grid(row=3, column=0, sticky='w', pady=5)
        self.entry_telefone_empresa = ttk.Entry(frame_dados, width=20)
        self.entry_telefone_empresa.insert(0, empresa['telefone'])
        self.entry_telefone_empresa.grid(row=3, column=1, pady=5, padx=5, sticky='w')
        
        # Botão salvar
        ttk.Button(parent, text="Salvar Dados da Empresa", 
                  command=self.salvar_config_empresa, style='Accent.TButton').pack(pady=20)

    # ... (continuar com os outros métodos existentes)
    def testar_impressora_config(self):
        """Testa a impressora com configurações atuais"""
        from modules.impressora import ImpressoraManager
        impressora = ImpressoraManager(self.sistema.config)
        if impressora.testar_impressora():
            messagebox.showinfo("Sucesso", "Teste de impressora realizado com sucesso!")
        else:
            messagebox.showerror("Erro", "Falha no teste de impressora. Verifique as configurações.")
    
    def listar_impressoras(self):
        """Lista impressoras disponíveis no Windows"""
        from modules.impressora import ImpressoraManager
        impressora = ImpressoraManager(self.sistema.config)
        impressoras = impressora.listar_impressoras_windows()
        
        if impressoras:
            janela = tk.Toplevel(self.root)
            janela.title("Impressoras Disponíveis")
            janela.geometry("400x300")
            
            frame = ttk.Frame(janela, padding=10)
            frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(frame, text="Impressoras Disponíveis no Windows", 
                     font=('Arial', 12, 'bold')).pack(pady=10)
            
            lista = tk.Listbox(frame)
            lista.pack(fill=tk.BOTH, expand=True, pady=10)
            
            for printer in impressoras:
                lista.insert(tk.END, printer[2])
            
            def selecionar_impressora():
                selecao = lista.curselection()
                if selecao:
                    impressora_selecionada = impressoras[selecao[0]][2]
                    self.entry_nome_impressora.delete(0, tk.END)
                    self.entry_nome_impressora.insert(0, impressora_selecionada)
                    janela.destroy()
            
            ttk.Button(frame, text="Selecionar", 
                      command=selecionar_impressora).pack(pady=5)
        else:
            messagebox.showinfo("Impressoras", "Nenhuma impressora local encontrada.")
    
    def salvar_config_impressora(self):
        """Salva as configurações da impressora"""
        try:
            self.sistema.config.dados['impressora']['tipo'] = self.tipo_impressora.get()
            self.sistema.config.dados['impressora']['nome_impressora_windows'] = self.entry_nome_impressora.get()
            self.sistema.config.dados['impressora']['porta_usb'] = self.entry_porta_usb.get()
            self.sistema.config.dados['impressora']['porta_ethernet'] = self.entry_ethernet.get()
            self.sistema.config.dados['impressora']['corte_automatico'] = self.corte_automatico.get()
            self.sistema.config.dados['impressora']['abrir_gaveta'] = self.abrir_gaveta.get()
            
            if self.sistema.config.salvar_config():
                messagebox.showinfo("Sucesso", "Configurações salvas com sucesso!")
            else:
                messagebox.showerror("Erro", "Erro ao salvar configurações!")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar configurações: {e}")
    
    def salvar_config_sistema(self):
        """Salva as configurações do sistema"""
        try:
            self.sistema.config.dados['sistema']['moeda'] = self.entry_moeda.get()
            self.sistema.config.dados['sistema']['simbolo_moeda'] = self.entry_simbolo_moeda.get()
            self.sistema.config.dados['sistema']['ativo_desconto'] = self.ativo_desconto.get()
            self.sistema.config.dados['sistema']['ativo_multiforma_pagamento'] = self.ativo_multiforma.get()
            self.sistema.config.dados['sistema']['controlo_stock'] = self.controlo_stock.get()
            self.sistema.config.dados['sistema']['som_ativo'] = self.som_ativo.get()
            
            if self.sistema.config.salvar_config():
                messagebox.showinfo("Sucesso", "Configurações do sistema salvas com sucesso!")
            else:
                messagebox.showerror("Erro", "Erro ao salvar configurações!")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar configurações: {e}")
    
    def salvar_config_empresa(self):
        """Salva as configurações da empresa"""
        try:
            self.sistema.config.dados['recibo']['empresa']['nome'] = self.entry_nome_empresa.get()
            self.sistema.config.dados['recibo']['empresa']['nif'] = self.entry_nif_empresa.get()
            self.sistema.config.dados['recibo']['empresa']['endereco'] = self.entry_endereco_empresa.get()
            self.sistema.config.dados['recibo']['empresa']['telefone'] = self.entry_telefone_empresa.get()
            
            if self.sistema.config.salvar_config():
                messagebox.showinfo("Sucesso", "Dados da empresa salvos com sucesso!")
            else:
                messagebox.showerror("Erro", "Erro ao salvar dados!")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar dados: {e}")

    # ... (continuar com os métodos existentes de produtos, promoções, etc.)
    def carregar_promocoes(self):
        """Carrega as promoções na treeview"""
        # Limpar treeview
        for item in self.tree_promocoes.get_children():
            self.tree_promocoes.delete(item)
        
        from modules.promocoes import PromocaoManager
        promocao_manager = PromocaoManager(self.sistema.db)
        promocoes = promocao_manager.obter_todas_promocoes()
        
        for promocao in promocoes:
            # Determinar tipo e valor
            if promocao['preco_promocao']:
                tipo = "Preço Fixo"
                valor = f"{promocao['preco_promocao']:.2f} Kz"
            else:
                tipo = "Desconto %"
                valor = f"{promocao['desconto_percentual']:.1f}%"
            
            # Status
            agora = datetime.now()
            data_fim = promocao['data_fim'] if isinstance(promocao['data_fim'], datetime) else datetime.strptime(str(promocao['data_fim']), '%Y-%m-%d %H:%M:%S')
            status = "Ativa" if promocao['ativa'] and agora <= data_fim else "Inativa"
            
            self.tree_promocoes.insert('', tk.END, values=(
                promocao['id_promocao'],
                promocao['nome_produto'],
                promocao['nome_promocao'],
                tipo,
                valor,
                promocao['data_inicio'].strftime('%d/%m/%Y'),
                promocao['data_fim'].strftime('%d/%m/%Y'),
                status
            ))
    
    def nova_promocao(self):
        """Cria uma nova promoção"""
        janela = tk.Toplevel(self.root)
        janela.title("Nova Promoção")
        janela.geometry("500x600")
        janela.transient(self.root)
        janela.grab_set()
        
        main_frame = ttk.Frame(janela, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Nova Promoção", 
                 font=('Arial', 16, 'bold')).pack(pady=10)
        
        # Produto
        frame_produto = ttk.Frame(main_frame)
        frame_produto.pack(fill=tk.X, pady=5)
        ttk.Label(frame_produto, text="Produto:*", width=15).pack(side=tk.LEFT)
        
        # Carregar produtos
        from modules.produtos import ProdutoManager
        produto_manager = ProdutoManager(self.sistema.db)
        produtos = produto_manager.obter_todos_produtos()
        
        produtos_dict = {f"{p['nome']} ({p['codigo_barras']})": p['id_produto'] for p in produtos}
        
        produto_var = tk.StringVar()
        combo_produto = ttk.Combobox(frame_produto, textvariable=produto_var, values=list(produtos_dict.keys()), state="readonly")
        combo_produto.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Nome da promoção
        frame_nome = ttk.Frame(main_frame)
        frame_nome.pack(fill=tk.X, pady=5)
        ttk.Label(frame_nome, text="Nome Promoção:*", width=15).pack(side=tk.LEFT)
        entry_nome = ttk.Entry(frame_nome)
        entry_nome.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Tipo de promoção
        frame_tipo = ttk.Frame(main_frame)
        frame_tipo.pack(fill=tk.X, pady=5)
        ttk.Label(frame_tipo, text="Tipo:*", width=15).pack(side=tk.LEFT)
        
        tipo_var = tk.StringVar(value="desconto")
        ttk.Radiobutton(frame_tipo, text="Desconto Percentual", variable=tipo_var, value="desconto").pack(side=tk.LEFT)
        ttk.Radiobutton(frame_tipo, text="Preço Fixo", variable=tipo_var, value="preco_fixo").pack(side=tk.LEFT)
        
        # Valor
        frame_valor = ttk.Frame(main_frame)
        frame_valor.pack(fill=tk.X, pady=5)
        ttk.Label(frame_valor, text="Valor:*", width=15).pack(side=tk.LEFT)
        entry_valor = ttk.Entry(frame_valor)
        entry_valor.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Datas
        frame_data_inicio = ttk.Frame(main_frame)
        frame_data_inicio.pack(fill=tk.X, pady=5)
        ttk.Label(frame_data_inicio, text="Data Início:*", width=15).pack(side=tk.LEFT)
        entry_data_inicio = ttk.Entry(frame_data_inicio)
        entry_data_inicio.insert(0, datetime.now().strftime('%Y-%m-%d 00:00:00'))
        entry_data_inicio.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        frame_data_fim = ttk.Frame(main_frame)
        frame_data_fim.pack(fill=tk.X, pady=5)
        ttk.Label(frame_data_fim, text="Data Fim:*", width=15).pack(side=tk.LEFT)
        entry_data_fim = ttk.Entry(frame_data_fim)
        entry_data_fim.insert(0, (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d 23:59:59'))
        entry_data_fim.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Ativa
        frame_ativa = ttk.Frame(main_frame)
        frame_ativa.pack(fill=tk.X, pady=5)
        ativa_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(frame_ativa, text="Promoção Ativa", variable=ativa_var).pack(anchor=tk.W)
        
        def salvar_promocao():
            try:
                # Validar campos
                if not produto_var.get() or not entry_nome.get():
                    messagebox.showerror("Erro", "Preencha todos os campos obrigatórios!")
                    return
                
                id_produto = produtos_dict[produto_var.get()]
                nome_promocao = entry_nome.get()
                tipo = tipo_var.get()
                
                if tipo == "desconto":
                    desconto_percentual = float(entry_valor.get())
                    preco_promocao = None
                else:
                    desconto_percentual = None
                    preco_promocao = float(entry_valor.get())
                
                dados_promocao = {
                    'id_produto': id_produto,
                    'nome_promocao': nome_promocao,
                    'desconto_percentual': desconto_percentual,
                    'preco_promocao': preco_promocao,
                    'data_inicio': entry_data_inicio.get(),
                    'data_fim': entry_data_fim.get(),
                    'ativa': ativa_var.get()
                }
                
                from modules.promocoes import PromocaoManager
                promocao_manager = PromocaoManager(self.sistema.db)
                resultado = promocao_manager.criar_promocao(dados_promocao)
                
                if resultado:
                    messagebox.showinfo("Sucesso", "Promoção criada com sucesso!")
                    self.carregar_promocoes()
                    janela.destroy()
                else:
                    messagebox.showerror("Erro", "Erro ao criar promoção!")
                    
            except ValueError as e:
                messagebox.showerror("Erro", f"Valor inválido: {e}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar promoção: {e}")
        
        # Botões
        frame_botoes = ttk.Frame(main_frame)
        frame_botoes.pack(fill=tk.X, pady=20)
        
        ttk.Button(frame_botoes, text="SALVAR", command=salvar_promocao, 
                  style='Accent.TButton').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(frame_botoes, text="CANCELAR", command=janela.destroy).pack(side=tk.RIGHT)
    
    def editar_promocao(self):
        """Edita promoção selecionada"""
        selecao = self.tree_promocoes.selection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione uma promoção para editar!")
            return
        
        # Implementar edição similar à criação
        messagebox.showinfo("Info", "Funcionalidade de edição em desenvolvimento!")
    
    def desativar_promocao(self):
        """Desativa promoção selecionada"""
        selecao = self.tree_promocoes.selection()
        if not selecao:
            messagebox.showwarning("Aviso", "Selecione uma promoção para desativar!")
            return
        
        item = self.tree_promocoes.item(selecao[0])
        valores = item['values']
        id_promocao = valores[0]
        nome_promocao = valores[2]
        
        if messagebox.askyesno("Confirmar", f"Desativar a promoção '{nome_promocao}'?"):
            from modules.promocoes import PromocaoManager
            promocao_manager = PromocaoManager(self.sistema.db)
            if promocao_manager.desativar_promocao(id_promocao):
                messagebox.showinfo("Sucesso", "Promoção desativada!")
                self.carregar_promocoes()
            else:
                messagebox.showerror("Erro", "Erro ao desativar promoção!")

    # Métodos para Gestão de Produtos
    def carregar_produtos(self):
        """Carrega os produtos na treeview"""
        # Limpar treeview
        for item in self.tree_produtos.get_children():
            self.tree_produtos.delete(item)
        
        from modules.produtos import ProdutoManager
        produto_manager = ProdutoManager(self.sistema.db)
        produtos = produto_manager.obter_todos_produtos()
        
        for produto in produtos:
            status = "OK" if produto['stock_atual'] > produto['stock_minimo'] else "BAIXO"
            self.tree_produtos.insert('', tk.END, values=(
                produto['id_produto'],
                produto['codigo_barras'],
                produto['nome'],
                f"{produto['preco_venda']:.2f} Kz",
                produto['stock_atual'],
                produto['categoria'],
                status
            ))

    def novo_produto(self):
        """Cria um novo produto"""
        janela = tk.Toplevel(self.root)
        janela.title("Novo Produto")
        janela.geometry("500x600")
        janela.transient(self.root)
        janela.grab_set()
        
        main_frame = ttk.Frame(janela, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Novo Produto", 
                 font=('Arial', 16, 'bold')).pack(pady=10)
        
        # Campos do formulário
        campos = [
            ("Código de Barras*:", "entry_codigo"),
            ("Nome do Produto*:", "entry_nome"),
            ("Descrição:", "entry_descricao"),
            ("Preço de Venda*:", "entry_preco_venda"),
            ("Preço de Custo:", "entry_preco_custo"),
            ("Stock Atual*:", "entry_stock_atual"),
            ("Stock Mínimo:", "entry_stock_minimo"),
            ("IVA (%):", "entry_iva"),
            ("Categoria:", "entry_categoria")
        ]
        
        entries = {}
        for texto, var_name in campos:
            frame_campo = ttk.Frame(main_frame)
            frame_campo.pack(fill=tk.X, pady=5)
            
            ttk.Label(frame_campo, text=texto, width=15).pack(side=tk.LEFT)
            
            entry = ttk.Entry(frame_campo)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            entries[var_name] = entry
        
        # Botões
        frame_botoes = ttk.Frame(main_frame)
        frame_botoes.pack(fill=tk.X, pady=20)
        
        def salvar_produto():
            try:
                # Validar campos obrigatórios
                if not entries['entry_codigo'].get() or not entries['entry_nome'].get():
                    messagebox.showerror("Erro", "Código e Nome são obrigatórios!")
                    return
                
                from modules.produtos import ProdutoManager
                produto_manager = ProdutoManager(self.sistema.db)
                
                dados_produto = {
                    'codigo_barras': entries['entry_codigo'].get(),
                    'nome': entries['entry_nome'].get(),
                    'descricao': entries['entry_descricao'].get(),
                    'preco_venda': float(entries['entry_preco_venda'].get() or 0),
                    'preco_custo': float(entries['entry_preco_custo'].get() or 0),
                    'stock_atual': int(entries['entry_stock_atual'].get() or 0),
                    'stock_minimo': int(entries['entry_stock_minimo'].get() or 0),
                    'iva': float(entries['entry_iva'].get() or 0),
                    'categoria': entries['entry_categoria'].get()
                }
                
                resultado = produto_manager.criar_produto(dados_produto)
                
                if resultado:
                    messagebox.showinfo("Sucesso", "Produto criado com sucesso!")
                    self.carregar_produtos()
                    janela.destroy()
                else:
                    messagebox.showerror("Erro", "Erro ao criar produto!")
                    
            except ValueError as e:
                messagebox.showerror("Erro", f"Valores numéricos inválidos: {e}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar produto: {e}")
        
        ttk.Button(frame_botoes, text="SALVAR", command=salvar_produto, 
                  style='Accent.TButton').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(frame_botoes, text="CANCELAR", command=janela.destroy).pack(side=tk.RIGHT)

    def pesquisar_produtos(self):
        """Pesquisa produtos"""
        messagebox.showinfo("Info", "Funcionalidade de pesquisa em desenvolvimento")

    def limpar_pesquisa_produtos(self):
        """Limpa a pesquisa de produtos"""
        self.entry_pesquisa_produtos.delete(0, tk.END)
        self.carregar_produtos()

    def atualizar_stock(self):
        """Atualiza stock de produtos"""
        messagebox.showinfo("Info", "Funcionalidade em desenvolvimento")

    def exportar_produtos(self):
        """Exporta produtos"""
        messagebox.showinfo("Info", "Funcionalidade em desenvolvimento")
    
    def buscar_vendas(self):
        # Implementar busca de vendas
        messagebox.showinfo("Info", "Funcionalidade em desenvolvimento")
    
    def filtrar_hoje(self):
        hoje = datetime.now().strftime('%Y-%m-%d')
        self.entry_data_inicio.delete(0, tk.END)
        self.entry_data_inicio.insert(0, hoje)
        self.entry_data_fim.delete(0, tk.END)
        self.entry_data_fim.insert(0, hoje)
        self.buscar_vendas()
    
    def criar_janela_produto(self, produto=None):
        janela = tk.Toplevel(self.root)
        janela.title("Novo Produto" if not produto else "Editar Produto")
        janela.geometry("500x600")
        janela.transient(self.root)
        janela.grab_set()
        
        main_frame = ttk.Frame(janela, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Dados do Produto", 
                 style='Title.TLabel').pack(pady=10)
        
        # Campos do formulário
        campos = [
            ("Código de Barras*:", "entry_codigo"),
            ("Nome do Produto*:", "entry_nome"),
            ("Descrição:", "entry_descricao"),
            ("Preço de Venda*:", "entry_preco_venda"),
            ("Preço de Custo:", "entry_preco_custo"),
            ("Stock Atual*:", "entry_stock_atual"),
            ("Stock Mínimo:", "entry_stock_minimo"),
            ("IVA (%):", "entry_iva"),
            ("Categoria:", "entry_categoria")
        ]
        
        for texto, var_name in campos:
            frame_campo = ttk.Frame(main_frame)
            frame_campo.pack(fill=tk.X, pady=5)
            
            ttk.Label(frame_campo, text=texto, width=15).pack(side=tk.LEFT)
            
            entry = ttk.Entry(frame_campo)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            setattr(self, var_name, entry)
        
        # Botões
        frame_botoes = ttk.Frame(main_frame)
        frame_botoes.pack(fill=tk.X, pady=20)
        
        ttk.Button(
            frame_botoes, 
            text="SALVAR", 
            command=lambda: self.salvar_produto(janela),
            style='Accent.TButton'
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            frame_botoes, 
            text="CANCELAR", 
            command=janela.destroy
        ).pack(side=tk.RIGHT)
        
        # Preencher campos se for edição
        if produto:
            self.preencher_campos_produto(produto)
    
    def preencher_campos_produto(self, produto):
        self.entry_codigo.insert(0, produto.get('codigo_barras', ''))
        self.entry_nome.insert(0, produto.get('nome', ''))
        self.entry_descricao.insert(0, produto.get('descricao', ''))
        self.entry_preco_venda.insert(0, str(produto.get('preco_venda', '')))
        self.entry_preco_custo.insert(0, str(produto.get('preco_custo', '')))
        self.entry_stock_atual.insert(0, str(produto.get('stock_atual', '')))
        self.entry_stock_minimo.insert(0, str(produto.get('stock_minimo', '')))
        self.entry_iva.insert(0, str(produto.get('iva', '')))
        self.entry_categoria.insert(0, produto.get('categoria', ''))
 
# Adicionar estes métodos à classe InterfaceGerente:

 

    def criar_aba_relatorios(self):
        frame_relatorios = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(frame_relatorios, text="Relatórios Avançados")
        
        # Frame de filtros
        frame_filtros = ttk.LabelFrame(frame_relatorios, text="Filtros do Relatório", padding=10)
        frame_filtros.pack(fill=tk.X, pady=10)
        
        # Período
        ttk.Label(frame_filtros, text="Período:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.periodo_relatorio = tk.StringVar(value='hoje')
        
        periodos = [
            ('Hoje', 'hoje'),
            ('Esta Semana', 'semana'),
            ('Este Mês', 'mes'),
            ('Personalizado', 'personalizado')
        ]
        
        for i, (texto, valor) in enumerate(periodos):
            ttk.Radiobutton(frame_filtros, text=texto, variable=self.periodo_relatorio, 
                           value=valor).grid(row=0, column=i+1, padx=5, pady=5)
        
        # Datas personalizadas
        frame_datas = ttk.Frame(frame_filtros)
        frame_datas.grid(row=1, column=0, columnspan=5, sticky='we', pady=5)
        
        ttk.Label(frame_datas, text="De:").pack(side=tk.LEFT, padx=5)
        self.data_inicio_rel = ttk.Entry(frame_datas, width=12)
        self.data_inicio_rel.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(frame_datas, text="Até:").pack(side=tk.LEFT, padx=5)
        self.data_fim_rel = ttk.Entry(frame_datas, width=12)
        self.data_fim_rel.pack(side=tk.LEFT, padx=5)
        
        # Botões de ação
        frame_acoes_rel = ttk.Frame(frame_filtros)
        frame_acoes_rel.grid(row=2, column=0, columnspan=5, pady=10)
        
        ttk.Button(frame_acoes_rel, text="Gerar Relatório", 
                  command=self.gerar_relatorio, style='Accent.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_acoes_rel, text="Exportar PDF", 
                  command=self.exportar_pdf).pack(side=tk.LEFT, padx=5)
        ttk.Button(frame_acoes_rel, text="Exportar Excel", 
                  command=self.exportar_excel).pack(side=tk.LEFT, padx=5)
        
        # Frame de resultados
        frame_resultados = ttk.LabelFrame(frame_relatorios, text="Resultados", padding=10)
        frame_resultados.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Métricas
        frame_metricas = ttk.Frame(frame_resultados)
        frame_metricas.pack(fill=tk.X, pady=10)
        
        self.metricas = {
            'total_vendas': ttk.Label(frame_metricas, text="Total Vendas: 0", font=('Arial', 12)),
            'valor_total': ttk.Label(frame_metricas, text="Valor Total: 0.00 Kz", font=('Arial', 12, 'bold')),
            'ticket_medio': ttk.Label(frame_metricas, text="Ticket Médio: 0.00 Kz", font=('Arial', 12)),
            'produto_mais_vendido': ttk.Label(frame_metricas, text="Produto Mais Vendido: -", font=('Arial', 10))
        }
        
        for i, (key, label) in enumerate(self.metricas.items()):
            label.grid(row=0, column=i, padx=10, pady=5, sticky='w')
        
        # Gráfico (placeholder)
        self.canvas_relatorio = tk.Canvas(frame_resultados, bg='white', height=200)
        self.canvas_relatorio.pack(fill=tk.X, pady=10)
        self.canvas_relatorio.create_text(100, 100, text="Gráfico será exibido aqui", fill='gray')
    
    def gerar_relatorio(self):
        """Gera relatório com base nos filtros"""
        try:
            periodo = self.periodo_relatorio.get()
            hoje = datetime.now().date()
            
            if periodo == 'hoje':
                data_inicio = hoje.strftime('%Y-%m-%d')
                data_fim = hoje.strftime('%Y-%m-%d')
            elif periodo == 'semana':
                data_inicio = (hoje - timedelta(days=hoje.weekday())).strftime('%Y-%m-%d')
                data_fim = hoje.strftime('%Y-%m-%d')
            elif periodo == 'mes':
                data_inicio = hoje.replace(day=1).strftime('%Y-%m-%d')
                data_fim = hoje.strftime('%Y-%m-%d')
            else:  # personalizado
                data_inicio = self.data_inicio_rel.get()
                data_fim = self.data_fim_rel.get()
            
            from modules.vendas import VendaManager
            venda_manager = VendaManager(self.sistema.db)
            vendas = venda_manager.obter_vendas_periodo(f"{data_inicio} 00:00:00", f"{data_fim} 23:59:59")
            
            # Calcular métricas
            total_vendas = len(vendas)
            valor_total = sum(venda['total_final'] for venda in vendas)
            ticket_medio = valor_total / total_vendas if total_vendas > 0 else 0
            
            # Atualizar métricas
            self.metricas['total_vendas'].config(text=f"Total Vendas: {total_vendas}")
            self.metricas['valor_total'].config(text=f"Valor Total: {valor_total:.2f} Kz")
            self.metricas['ticket_medio'].config(text=f"Ticket Médio: {ticket_medio:.2f} Kz")
            
            messagebox.showinfo("Relatório", f"Relatório gerado para o período selecionado!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar relatório: {e}")
    
    def exportar_pdf(self):
        messagebox.showinfo("PDF", "Funcionalidade de exportação PDF em desenvolvimento!")
    
    def exportar_excel(self):
        messagebox.showinfo("Excel", "Funcionalidade de exportação Excel em desenvolvimento!")
 
    def salvar_produto(self, janela):
        # Validar campos obrigatórios
        if not self.entry_codigo.get() or not self.entry_nome.get():
            messagebox.showerror("Erro", "Código e Nome são obrigatórios!")
            return
        
        try:
            from modules.produtos import ProdutoManager
            produto_manager = ProdutoManager(self.sistema.db)
            
            dados_produto = {
                'codigo_barras': self.entry_codigo.get(),
                'nome': self.entry_nome.get(),
                'descricao': self.entry_descricao.get(),
                'preco_venda': float(self.entry_preco_venda.get() or 0),
                'preco_custo': float(self.entry_preco_custo.get() or 0),
                'stock_atual': int(self.entry_stock_atual.get() or 0),
                'stock_minimo': int(self.entry_stock_minimo.get() or 0),
                'iva': float(self.entry_iva.get() or 0),
                'categoria': self.entry_categoria.get()
            }
            
            resultado = produto_manager.criar_produto(dados_produto)
            
            if resultado:
                messagebox.showinfo("Sucesso", "Produto criado com sucesso!")
                self.carregar_produtos()
                janela.destroy()
            else:
                messagebox.showerror("Erro", "Erro ao criar produto!")
                
        except ValueError as e:
            messagebox.showerror("Erro", f"Valores numéricos inválidos: {e}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar produto: {e}")

    # Métodos para Gestão de Usuários
    def carregar_usuarios(self):
        """Carrega os usuários na treeview"""
        # Limpar treeview
        for item in self.tree_usuarios.get_children():
            self.tree_usuarios.delete(item)
        
        from modules.usuarios import UsuarioManager
        usuario_manager = UsuarioManager(self.sistema.db)
        usuarios = usuario_manager.obter_usuarios()
        
        for usuario in usuarios:
            status = "Ativo" if usuario['ativo'] else "Inativo"
            self.tree_usuarios.insert('', tk.END, values=(
                usuario['id_usuario'],
                usuario['numero_trabalhador'],
                usuario['nome'],
                usuario['tipo'],
                status
            ))

    def novo_usuario(self):
        """Cria um novo usuário"""
        messagebox.showinfo("Info", "Funcionalidade de novo usuário em desenvolvimento")
    
    def set_usuario(self, usuario):
        self.usuario = usuario
        self.label_usuario.config(text=f"Usuário: {usuario['nome']} ({usuario['tipo']})")
    
    def executar(self):
        self.root.mainloop()






    

 