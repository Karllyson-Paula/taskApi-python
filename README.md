# taskApi-python

API REST de gerenciamento de tarefas, construída com Flask e SQLite. Oferece cadastro e login de usuários, autenticação com JWT e operações de criação, consulta, atualização e exclusão de tarefas.

## Tecnologias

- Python
- Flask
- SQLite
- Flask-JWT-Extended
- Werkzeug para hash de senhas
- python-dotenv para carregar variáveis do arquivo `.env`

## Como rodar localmente

Execute os comandos a partir da pasta raiz do projeto.

Crie e ative um ambiente virtual:

```
python3 -m venv .venv
source .venv/bin/activate
```

No Windows PowerShell, ative-o com:

```
.venv\Scripts\Activate.ps1
```

Instale as dependências:

```
pip install -r requirements.txt
```

Crie um arquivo `.env` na raiz do projeto:

```
JWT_SECRET_KEY=coloque_sua_chave_secreta_aqui
```

Gere uma chave aleatória localmente e use o resultado no lugar do texto de exemplo:

```
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Não compartilhe nem envie o `.env` ao Git. O arquivo está listado no `.gitignore`.

Inicie a API:

```
python api/App.py
```

O servidor de desenvolvimento ficará disponível em `http://127.0.0.1:5000`. Na primeira execução, a API cria o arquivo SQLite `tasks.db` e as tabelas `users` e `tasks` na pasta atual.

## Autenticação

Cadastro e login são públicos. As rotas de tarefas exigem um token JWT.

1. Cadastre um usuário em `POST /auth/register`.
2. Faça login em `POST /auth/login`.
3. Copie `user.access_token` da resposta.
4. Envie o token nas requisições protegidas:

```
Authorization: Bearer SEU_ACCESS_TOKEN
```

No Postman, selecione **Authorization → Bearer Token** e cole o token no campo **Token**.

## Endpoints

| Método | Rota               | Autenticação | Descrição                                   |
| ------ | ------------------ | ------------ | ------------------------------------------- |
| GET    | `/`                | Não          | Retorna uma mensagem simples da API         |
| POST   | `/auth/register`   | Não          | Cadastra um usuário                         |
| POST   | `/auth/login`      | Não          | Verifica as credenciais e retorna um token  |
| POST   | `/tasks`           | Sim          | Cria uma tarefa para o usuário autenticado  |
| GET    | `/tasks`           | Sim          | Lista as tarefas do usuário autenticado     |
| GET    | `/tasks/<task_id>` | Sim          | Busca uma tarefa do usuário pelo ID         |
| PATCH  | `/tasks/<task_id>` | Sim          | Atualiza parcialmente uma tarefa do usuário |
| DELETE | `/tasks/<task_id>` | Sim          | Exclui uma tarefa do usuário                |

### Cadastro

`POST /auth/register`

```
{
  "name": "Ana",
  "email": "ana@example.com",
  "password": "uma-senha"
}
```

Retorna `201 Created`. O e-mail já cadastrado retorna `409 Conflict`; dados ausentes ou JSON inválido retornam `400 Bad Request`. A senha é armazenada como hash, não em texto puro.

### Login

`POST /auth/login`

```
{
  "email": "ana@example.com",
  "password": "uma-senha"
}
```

Retorna `200 OK` com os dados do usuário e `access_token`. Credenciais inválidas retornam `401 Unauthorized`.

### Criar tarefa

`POST /tasks` — requer token.

```
{
  "title": "Estudar Flask",
  "description": "Conectar a API ao SQLite"
}
```

`title` é obrigatório; `description` é opcional. Retorna `201 Created` com a tarefa criada.

### Listar e buscar tarefas

- `GET /tasks` retorna `{"tasks": [...]}` com as tarefas do usuário autenticado.
- `GET /tasks/1` retorna a tarefa com ID `1`, se pertencer ao usuário autenticado.

Se a tarefa não existir ou pertencer a outro usuário, a API retorna `404 Not Found`.

### Atualizar tarefa

`PATCH /tasks/1` — requer token. Envie apenas os campos que deseja alterar:

```
{
  "completed": true
}
```

Campos aceitos: `title` (texto não vazio), `description` (texto ou `null`) e `completed` (`true` ou `false`). Os demais campos permanecem inalterados.

### Excluir tarefa

`DELETE /tasks/1` — requer token. Retorna `200 OK` quando excluída e `404 Not Found` se a tarefa não existir ou não pertencer ao usuário autenticado.

## Estrutura

```
api/
  App.py            # aplicação Flask e rotas
  database.py       # conexão SQLite e criação das tabelas
models/
  task.py           # reservado para modelos
requirements.txt    # dependências com versões fixas
tasks.db            # criado localmente na primeira execução
```

## Observações

- Cada tarefa pertence a um usuário; as consultas protegidas filtram pelo usuário identificado no token.
- O token JWT é assinado, não criptografado. Não coloque senhas ou hashes nele.
- `app.run(debug=True)` é destinado ao desenvolvimento local, não à produção.

## Autor

Karllyson Eduardo — [@Karllyson-Paula](https://github.com/Karllyson-Paula)