# sistema_bar9
Sistema de gestão para bares com dois computadores: um para vendas (touchscreen) e outro para gestão.

# Sistema Bar - Dois Computadores

Sistema de gestão para bares com dois computadores: um para vendas (touchscreen) e outro para gestão.

## Instalação

1. Instalar Python 3.8+
2. Instalar MySQL
3. Executar: `pip install -r requirements.txt`
4. Configurar banco de dados: `scripts/setup_database.sql`
5. Executar: `python main.py`

## Uso

- **Touchscreen**: `python main.py touchscreen`
- **Gerente**: `python main.py gerente`

## Credenciais de Teste

- Admin: 00001 / 1234
- Gerente: 10001 / 1111  
- Supervisor: 20001 / 2222
- Vendedor: 30001 / 3333


# Sistema Bar - Dois Computadores

Sistema de gestão para bares com dois computadores: um para vendas (touchscreen) e outro para gestão.

## Funcionalidades

### Computador Touchscreen (Vendas)
- Interface otimizada para touchscreen
- Botões configuráveis para produtos
- Teclado virtual para entrada de dados
- Cálculo automático de troco
- Múltiplas formas de pagamento
- Impressão de recibos
- Controle de stock em tempo real

### Computador Gerente (Gestão)
- Gestão de produtos e stock
- Relatórios de vendas
- Gestão de usuários
- Configuração de promoções
- Controle de devoluções
- Configurações do sistema

## Instalação

1. **Instalar Python 3.8+**
2. **Instalar MySQL**
3. **Criar ambiente virtual (opcional)**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Linux/Mac:
   source venv/bin/activate
