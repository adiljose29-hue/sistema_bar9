import tkinter as tk
from tkinter import ttk, messagebox

class LoginVendedor:
    def __init__(self, parent, sistema):
        self.parent = parent
        self.sistema = sistema
        self.usuario = None
        
    
    def mostrar(self):
        janela = tk.Toplevel(self.parent)
        janela.title("Login Vendedor")
        janela.geometry("350x350")
        janela.transient(self.parent)
        janela.grab_set()
        
        # Centralizar a janela manualmente
        self.centralizar_janela(janela)
        
        main_frame = ttk.Frame(janela, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="Login Vendedor", 
                 font=('Arial', 14, 'bold')).pack(pady=10)
        
        # Número de trabalhador
        ttk.Label(main_frame, text="Nº Trabalhador:").pack(anchor=tk.W, pady=(10, 5))
        self.entry_numero = ttk.Entry(main_frame, font=('Arial', 12), justify='center')
        self.entry_numero.pack(fill=tk.X, pady=5)
        
        # Senha
        ttk.Label(main_frame, text="Senha:").pack(anchor=tk.W, pady=(10, 5))
        self.entry_senha = ttk.Entry(main_frame, show="*", font=('Arial', 12), justify='center')
        self.entry_senha.pack(fill=tk.X, pady=5)
        
        def fazer_login():
            numero = self.entry_numero.get().strip()
            senha = self.entry_senha.get().strip()
            
            if not numero or not senha:
                messagebox.showerror("Erro", "Preencha todos os campos!")
                return
            
            # Usar o sistema passado como parâmetro
            usuario = self.sistema.autenticar_usuario(numero, senha)
            
            if usuario and usuario['tipo'] in ['vendedor', 'admin', 'gerente', 'supervisor']:
                self.usuario = usuario
                janela.destroy()
            else:
                messagebox.showerror("Erro", "Acesso negado! Apenas vendedores podem aceder.")
                self.entry_senha.delete(0, tk.END)
                self.entry_numero.focus()
        
        # Botões
        frame_botoes = ttk.Frame(main_frame)
        frame_botoes.pack(fill=tk.X, pady=20)
        
        ttk.Button(frame_botoes, text="Login", command=fazer_login).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(frame_botoes, text="Sair", command=self.parent.quit).pack(side=tk.RIGHT)
        
        # Bind Enter key
        self.entry_senha.bind('<Return>', lambda e: fazer_login())
        
        # Focar no primeiro campo
        self.entry_numero.focus()
        
        self.parent.wait_window(janela)
        return self.usuario
    
    def centralizar_janela(self, janela):
        """Centraliza a janela na tela"""
        janela.update_idletasks()
        width = janela.winfo_width()
        height = janela.winfo_height()
        x = (janela.winfo_screenwidth() // 2) - (width // 2)
        y = (janela.winfo_screenheight() // 2) - (height // 2)
        janela.geometry('{}x{}+{}+{}'.format(width, height, x, y))