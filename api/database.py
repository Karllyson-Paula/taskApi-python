import sqlite3

def connect_db():
  conn = sqlite3.connect("tasks.db")
  conn.execute("PRAGMA foreign_keys = ON")
  conn.row_factory = sqlite3.Row
  return conn

def create_table():
  conn = connect_db()
  conn.execute(""" 
              CREATE TABLE IF NOT EXISTS users (
                              id INTEGER PRIMARY KEY AUTOINCREMENT,
                              name TEXT NOT NULL,
                              email VARCHAR(100) UNIQUE NOT NULL,
                              password_hash TEXT NOT NULL
                              )
               """
               )
  
  conn.execute(
    """
                   CREATE TABLE IF NOT EXISTS tasks (
                                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                                   user_id INTEGER NOT NULL,
                                   title TEXT NOT NULL,
                                   description TEXT,
                                   completed BOOLEAN DEFAULT FALSE,
                                   FOREIGN KEY (user_id) REFERENCES users (id)
                                 )
                   """
  )
  
  conn.commit()
  conn.close()