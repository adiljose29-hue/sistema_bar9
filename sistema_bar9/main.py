import os
import sys
from modules.config import Configuracao
from modules.database import Database

class SistemaBar:
    def __init__(self):
        print("Iniciando Sistema Bar...")
        self.config = Configuracao()
        self.db = Database(self.config)
        
    def executar_touchscreen(self):
        """Executar interface touchscreen para vendas"""
        from interfaces.touchscreen import InterfaceTouchscreen
        app = InterfaceTouchscreen(self)
        app.executar()
    
    def executar_gerente(self):
        """Executar interface do gerente"""
        from interfaces.gerente import InterfaceGerente
        app = InterfaceGerente(self)
        app.executar()
    
    def autenticar_usuario(self, numero_trabalhador, senha):
        """Autenticar usuário no sistema"""
        from modules.usuarios import UsuarioManager
        usuario_manager = UsuarioManager(self.db)
        return usuario_manager.autenticar(numero_trabalhador, senha)
    
    def validar_supervisor(self, codigo_cartao, numero_trabalhador, senha):
        """Validar supervisor com cartão código de barras"""
        from modules.usuarios import UsuarioManager
        usuario_manager = UsuarioManager(self.db)
        return usuario_manager.validar_supervisor(codigo_cartao, numero_trabalhador, senha)

def main():
    # Criar diretórios necessários
    os.makedirs("recibos", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs("assets/images", exist_ok=True)
    os.makedirs("assets/sounds", exist_ok=True)
    
    sistema = SistemaBar()
    
    if len(sys.argv) > 1:
        modo = sys.argv[1].lower()
        if modo == "touchscreen":
            sistema.executar_touchscreen()
        elif modo == "gerente":
            from interfaces.login import InterfaceLogin
            login = InterfaceLogin(sistema)
            if login.executar():
                sistema.executar_gerente()
        else:
            print("Modo inválido. Use: touchscreen ou gerente")
    else:
        # Modo interativo
        print("=== SISTEMA BAR DOIS COMPUTADORES ===")
        print("1 - Touchscreen (Vendas)")
        print("2 - Gerente (Gestão)")
        
        opcao = input("Selecione o modo: ").strip()
        
        if opcao == "1":
            sistema.executar_touchscreen()
        elif opcao == "2":
            from interfaces.login import InterfaceLogin
            login = InterfaceLogin(sistema)
            if login.executar():
                sistema.executar_gerente()
        else:
            print("Opção inválida")

if __name__ == "__main__":
    main()