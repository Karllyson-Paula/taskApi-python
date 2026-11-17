import sqlite3
from database import connect_db, create_table
from werkzeug.security import check_password_hash, generate_password_hash
from flask import Flask, request, jsonify
from dotenv import load_dotenv

import os
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)
create_table()
load_dotenv()

app.config["JWT_SECRET_KEY"] = os.environ["JWT_SECRET_KEY"]
JWTManager(app)

# teste retorno da api sem metodo http 
@app.route("/")
def cuida():
  return "Boa Noite Turma"

#Rotas de tarefas
#POST de tarefa
@app.route("/tasks", methods=["POST"])
@jwt_required()
def create_task():
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True)
    
    if not isinstance(data, dict):
      return jsonify({ "error": "Envie um objeto JSON válido"}), 400
      
    title = data.get("title")
    
    if not isinstance(title, str) or not title.strip():
      return jsonify({ "error": "Titulo é obrigatório para adicionar uma tarefa"}), 400
    
    description = data.get("description")
    if description is not None and not isinstance(description, str):
      return jsonify({ "error": "Descrição deve ser texto"}), 400

    title = title.strip()
    
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(
      "INSERT INTO tasks (user_id, title, description) VALUES (?,?,?)" ,
      (user_id, title, description)
    )
    
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    
    task_content = {
      "id": task_id,
      "user_id": user_id,
      "title": title,
      "description": description,
      "completed": False
    }
    
    
    return jsonify({
      "message": "Tarefa criada com sucesso!",
      "task": task_content
      }), 201
    
# GET: todas as tarefas e por id (get 1 e 2 respectivamente)
@app.route("/tasks", methods=["GET"])
@jwt_required()
def get_tasks():
  user_id = int(get_jwt_identity())
  conn = connect_db()
  rows = conn.execute(
    "SELECT id, title, description, completed FROM tasks "
    "WHERE user_id = ? ORDER BY id",
    (user_id,)
  ).fetchall()
  conn.close()
  
  tasks = [dict(row) for row in rows]
  for task in tasks:
    task["completed"] = bool(task["completed"])
  
  
  return jsonify({
    "tasks": tasks
  })


@app.route("/tasks/<int:task_id>", methods=["GET"])
@jwt_required()
def get_task(task_id):
  user_id = int(get_jwt_identity())
  conn = connect_db()
  row = conn.execute(
    "SELECT id, title, description, completed FROM tasks "
    "WHERE id = ? AND user_id = ?",
    (task_id, user_id)
  ).fetchone()
  conn.close()
  
  if row is None: 
    return jsonify({ "message": "Tarefa não encontrada"}), 404
  
  task = dict(row)
  task["completed"] = bool(task["completed"])
  return jsonify(task)


#PATCH - update de tarefas e status de conclusão
@app.route("/tasks/<int:task_id>", methods=["PATCH"])
@jwt_required()
def update_task(task_id):
  data = request.get_json(silent=True)
  if not isinstance(data, dict):
    return jsonify({ "error": "Envie um objeto JSON válido"}), 400
  
  user_id = int(get_jwt_identity())
  conn = connect_db()
  
  row = conn.execute(
    "SELECT title, description, completed FROM tasks "
    "WHERE id = ? AND user_id = ?",
    (task_id, user_id)
  ).fetchone()
  
  if row is None:
    conn.close()
    return jsonify({"message": "Tarefa não encontrada"}), 404
  
  title = data.get("title", row["title"])
  description = data.get("description", row["description"])
  completed = data.get("completed", bool(row["completed"]))
  
  if not isinstance(title, str) or not title.strip():
        conn.close()
        return jsonify({"error": "Título não pode ficar vazio"}), 400
  if description is not None and not isinstance(description, str):
        conn.close()
        return jsonify({"error": "Descrição deve ser texto"}), 400
  if not isinstance(completed, bool):
        conn.close()
        return jsonify({"error": "completed deve ser true ou false"}), 400
      
  title = title.strip()
  conn.execute(
    "UPDATE tasks SET title = ?, description = ?, completed = ? "
    "WHERE id = ? AND user_id = ?",
    (title, description, completed, task_id, user_id)
  )
  conn.commit()
  conn.close()
  
  return jsonify({
    "message": "Tarefa atualizada",
    "task": {
      "id": task_id,
      "user_id": user_id,
      "title": title,
      "description": description,
      "completed": completed
    }
  }), 200
  
  
  
#DELETE
@app.route("/tasks/<int:task_id>", methods=["DELETE"])
@jwt_required()
def delete_task(task_id):
  user_id = int(get_jwt_identity())
  conn = connect_db()
  cursor = conn.execute(
    "DELETE FROM tasks WHERE id = ? AND user_id = ?",
    (task_id, user_id)
  )
  deleted_count = cursor.rowcount
  conn.commit()
  conn.close()
  
  if deleted_count == 0: 
    return jsonify({ "error": "Tarefa não encontrada"}), 404
  
  return jsonify({ "message": "Tarefa finalizada"}), 200
  
  
#Rotas de usuarios
#Cadastro
@app.route("/auth/register", methods=["POST"])
def create_user():
  data = request.get_json(silent=True)
  if not isinstance(data, dict):
    return jsonify({"error": "Envie um objeto JSON válido"}), 400

  name = data.get("name")
  email = data.get("email")
  password = (
    data.get("password")
  )
  
  if not name or not email or not password:
    return jsonify({ "error": "Dados incompletos"}), 400
  
  #Geração de hash para senhas
  password_hash = generate_password_hash(password)
  
  conn = connect_db()
  try:
    cursor = conn.cursor()
    cursor.execute(
      "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
      (name, email, password_hash),
    )
    conn.commit()
    user_id = cursor.lastrowid
    return (
      jsonify({
        "id": user_id,
        "name": name,
        "email": email,
        "message": "Usuário criado com sucesso"
      }), 201
    )
  except sqlite3.IntegrityError:
    return jsonify({"error": "E-mail já cadastrado"}), 409
  finally:
    conn.close()
    
#Login
@app.route("/auth/login", methods=["POST"])
def login_user():
  data = request.get_json(silent=True)
  if not isinstance(data, dict):
    return jsonify({"error": "Envie um objeto JSON válido"}), 400

  email = data.get("email")  
  password = data.get("password")

  
  if not email or not password:
    return jsonify({ "error": "Informe email e senha"}), 400
  
  conn = connect_db()
  cursor = conn.cursor()
  cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
  user = cursor.fetchone()
  conn.close()
  
  if not user or not check_password_hash(user["password_hash"], password):
    return jsonify({ "error": "E-mail ou senha inválidos"}), 401
  
  access_token = create_access_token(identity=str(user["id"]))
  
  return (
    jsonify(
      {
        "message": "Login realizado",
        "user": {
          "id": user["id"],
          "name": user["name"],
          "email": user["email"],
          "access_token": access_token
        }
      }
    ), 200
  )
  
  
if __name__ == "__main__":
  app.run(debug=True)