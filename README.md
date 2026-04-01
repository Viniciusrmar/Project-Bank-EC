# 🏦 Banco Digital API — Python + Flask + MySQL

Projeto acadêmico de sistema bancário digital com três módulos:
conta digital, carteira de investimentos e controle de gastos.

---

## 📁 Estrutura de Pastas

```
bancodigital-python/
│
├── app.py                  ← Arquivo principal (inicializa o Flask)
├── config.py               ← Conexão com o MySQL
├── validators.py           ← Funções de validação reutilizáveis
├── requirements.txt        ← Dependências Python
├── banco.sql               ← Script para criar o banco e as tabelas
├── exemplos.json           ← JSONs de teste para todos os endpoints
├── README.md               ← Este arquivo
│
└── routes/
    ├── __init__.py
    ├── usuarios.py         ← POST /usuarios/cadastro, POST /login, GET /usuarios
    ├── contas.py           ← GET /contas/usuario/<id>
    ├── transacoes.py       ← POST /transacoes, GET /transacoes/conta/<id>
    ├── gastos.py           ← POST /gastos, GET /gastos/usuario/<id>
    └── investimentos.py    ← POST /investimentos, GET /investimentos/usuario/<id>
```

---

## ✅ Pré-requisitos

- Python 3.10 ou superior
- MySQL 8.0 instalado e rodando
- pip atualizado

---

## 🚀 Passo a Passo para Rodar

### 1. Clone ou copie o projeto

```bash
cd bancodigital-python
```

### 2. Crie e ative o ambiente virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure o banco de dados

Abra o MySQL e execute o script:

```bash
mysql -u root -p < banco.sql
```

Ou cole o conteúdo de `banco.sql` direto no MySQL Workbench / DBeaver.

### 5. Ajuste as credenciais do banco

Edite o arquivo `config.py` com seu usuário e senha do MySQL:

```python
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "SUA_SENHA_AQUI",   # <- altere aqui
    "database": "bancodigital",
}
```

### 6. Rode a aplicação

```bash
python app.py
```

Saída esperada:
```
==================================================
  Banco Digital API rodando!
  Acesse: http://localhost:5000
==================================================
```

---

## 🔌 Endpoints Disponíveis

| Método | Rota                                | Descrição                          |
|--------|-------------------------------------|------------------------------------|
| GET    | /                                   | Health check / lista de rotas      |
| POST   | /usuarios/cadastro                  | Cadastra usuário + cria conta      |
| POST   | /usuarios/login                     | Login por email e senha            |
| GET    | /usuarios                           | Lista todos os usuários            |
| GET    | /contas/usuario/`<usuario_id>`      | Contas de um usuário               |
| POST   | /transacoes                         | Cria transação (ENTRADA ou SAIDA)  |
| GET    | /transacoes/conta/`<conta_id>`      | Extrato de uma conta               |
| POST   | /gastos                             | Cadastra um gasto                  |
| GET    | /gastos/usuario/`<usuario_id>`      | Gastos de um usuário + resumo      |
| POST   | /investimentos                      | Cadastra um investimento           |
| GET    | /investimentos/usuario/`<id>`       | Investimentos de um usuário        |

---

## 🧪 Testando com curl

### Cadastrar usuário
```bash
curl -X POST http://localhost:5000/usuarios/cadastro \
  -H "Content-Type: application/json" \
  -d '{
    "nome": "Maria Oliveira",
    "email": "maria@email.com",
    "senha": "senha123",
    "data_nascimento": "1995-08-20",
    "cpf": "987.654.321-00",
    "cep": "01310-100",
    "logradouro": "Avenida Paulista",
    "numero": "1000",
    "bairro": "Bela Vista",
    "cidade": "São Paulo",
    "estado": "SP"
  }'
```

### Login
```bash
curl -X POST http://localhost:5000/usuarios/login \
  -H "Content-Type: application/json" \
  -d '{"email": "maria@email.com", "senha": "senha123"}'
```

### Depositar (transação de entrada)
```bash
curl -X POST http://localhost:5000/transacoes \
  -H "Content-Type: application/json" \
  -d '{"conta_id": 1, "tipo_transacao": "ENTRADA", "descricao": "Salário", "valor": 3000.00}'
```

### Ver extrato
```bash
curl http://localhost:5000/transacoes/conta/1
```

### Cadastrar gasto
```bash
curl -X POST http://localhost:5000/gastos \
  -H "Content-Type: application/json" \
  -d '{"usuario_id": 1, "categoria": "Alimentação", "descricao": "Mercado", "valor": 250.00}'
```

### Cadastrar investimento
```bash
curl -X POST http://localhost:5000/investimentos \
  -H "Content-Type: application/json" \
  -d '{"usuario_id": 1, "tipo_investimento": "CDB", "nome_ativo": "CDB Banco XP 115% CDI", "valor_aplicado": 1000.00, "rentabilidade": 13.5}'
```

---

## ⚠️ Observações Acadêmicas

- **Senha em texto puro**: armazenada sem hash apenas para simplificar. Em produção, use `bcrypt` ou `argon2`.
- **Sem autenticação JWT**: o login retorna apenas os dados do usuário. Em produção, use tokens JWT.
- **CORS aberto**: liberado para qualquer origem. Em produção, restrinja ao domínio do frontend.
- **debug=True**: não use em produção. Use um servidor WSGI como `gunicorn`.