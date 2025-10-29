import tkinter as tk
from tkinter import ttk, messagebox

class InterfaceLogin:
    def __init__(self, sistema):
        self.sistema = sistema
        self.root = tk.Tk()
        self.root.title("Login - Sistema Bar")
        self.root.geometry("350x350")
        self.root.resizable(False, False)
        self.root.eval('tk::PlaceWindow . center')
        
        self.usuario_autenticado = None
        
        self.criar_interface()
    
    def criar_interface(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        titulo = ttk.Label(main_frame, text="Sistema Bar - Login", 
                          font=('Arial', 16, 'bold'))
        titulo.pack(pady=10)
        
        # Frame dos campos
        frame_campos = ttk.Frame(main_frame)
        frame_campos.pack(fill=tk.X, pady=10)
        
        # Número de trabalhador
        ttk.Label(frame_campos, text="Nº Trabalhador (5 dígitos):", 
                 font=('Arial', 10)).pack(anchor=tk.W, pady=(10, 5))
        self.entry_numero = ttk.Entry(frame_campos, font=('Arial', 12), justify='center')
        self.entry_numero.pack(fill=tk.X, pady=5)
        
        # Senha
        ttk.Label(frame_campos, text="Senha (4 dígitos):", 
                 font=('Arial', 10)).pack(anchor=tk.W, pady=(10, 5))
        self.entry_senha = ttk.Entry(frame_campos, show="*", font=('Arial', 12), justify='center')
        self.entry_senha.pack(fill=tk.X, pady=5)
        
        # Frame dos botões
        frame_botoes = ttk.Frame(main_frame)
        frame_botoes.pack(fill=tk.X, pady=20)
        
        ttk.Button(frame_botoes, text="Login", command=self.fazer_login, 
                  style='Accent.TButton').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(frame_botoes, text="Cancelar", command=self.root.quit).pack(side=tk.RIGHT)
        
        # Bind Enter key
        self.entry_senha.bind('<Return>', lambda e: self.fazer_login())
        
        # Focar no primeiro campo
        self.entry_numero.focus()
    
    def fazer_login(self):
        numero = self.entry_numero.get().strip()
        senha = self.entry_senha.get().strip()
        
        if not numero or not senha:
            messagebox.showerror("Erro", "Preencha todos os campos!")
            return
        
        if len(numero) != 5 or not numero.isdigit():
            messagebox.showerror("Erro", "Número de trabalhador deve ter 5 dígitos!")
            self.entry_numero.focus()
            return
        
        if len(senha) != 4 or not senha.isdigit():
            messagebox.showerror("Erro", "Senha deve ter 4 dígitos!")
            self.entry_senha.focus()
            return
        
        usuario = self.sistema.autenticar_usuario(numero, senha)
        
        if usuario:
            self.usuario_autenticado = usuario
            self.root.destroy()
        else:
            messagebox.showerror("Erro", "Credenciais inválidas ou usuário inativo!")
            self.entry_senha.delete(0, tk.END)
            self.entry_numero.focus()
    
    def executar(self):
        self.root.mainloop()
        return self.usuario_autenticado is not None