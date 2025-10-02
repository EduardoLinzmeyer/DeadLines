import pyodbc
import threading
import os
from dotenv import load_dotenv
from pathlib import Path
import bcrypt
from contextlib import contextmanager


BASEDIR = Path(__file__).resolve().parent
DOTENV_PATH = BASEDIR / '.env'

load_dotenv(DOTENV_PATH)

DB_CONECTADO = False
_thread_local = threading.local()

SQL_SERVER_CONFIG = {
    'server': os.getenv("DB_SERVER"),
    'database': os.getenv("DB_NAME"),
    'username': os.getenv("DB_USER"),
    'password': os.getenv("DB_PASSWORD"),
    'driver': os.getenv("DB_DRIVER"),
    'timeout': int(os.getenv("DB_TIMEOUT", 30))
}

@contextmanager
def obter_cursor():
    conn = getattr(_thread_local, "connection", None)
    if not conn:
        conn = pyodbc.connect(
            f"DRIVER={{{SQL_SERVER_CONFIG['driver']}}};"
            f"SERVER={SQL_SERVER_CONFIG['server']};"
            f"DATABASE={SQL_SERVER_CONFIG['database']};"
            f"UID={SQL_SERVER_CONFIG['username']};"
            f"PWD={SQL_SERVER_CONFIG['password']};"
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
            f"Connection Timeout={SQL_SERVER_CONFIG['timeout']};"
        )
        _thread_local.connection = conn

    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()

    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()


"""Cria conexão com o SQL Server Azure"""
def obter_conexao_sql_server():
    try:
        conn_str = (
            f"DRIVER={{{SQL_SERVER_CONFIG['driver']}}};"
            f"SERVER={SQL_SERVER_CONFIG['server']};"
            f"DATABASE={SQL_SERVER_CONFIG['database']};"
            f"UID={SQL_SERVER_CONFIG['username']};"
            f"PWD={SQL_SERVER_CONFIG['password']};"
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
            f"Connection Timeout={SQL_SERVER_CONFIG['timeout']};"
        )
        return pyodbc.connect(conn_str)

    except pyodbc.InterfaceError as ie:
        print(f"Erro de interface ODBC: {ie}")
        return None
    except pyodbc.OperationalError as oe:
        print(f"Erro operacional: {oe}")
        return None
    except pyodbc.Error as e:
        print(f"Erro ODBC: {e}")
        return None
    except Exception as e:
        print(f"Erro geral ao conectar com o SQL Server: {e}")
        return None


"""Obtém conexão com a thread atual"""
def obter_conexao():
    try:
        if not hasattr(_thread_local, 'connection') or _thread_local.connection is None:
            _thread_local.connection = obter_conexao_sql_server()
        return _thread_local.connection

    except Exception as e:
        print(f"Erro ao obter conexão: {e}")
        return obter_conexao_sql_server()


"""Fecha a conexão da thread atual"""
def fechar_conexao():
    try:
        if hasattr(_thread_local, 'connection') and _thread_local.connection:
            _thread_local.connection.close()
            _thread_local.connection = None

    except Exception as e:
        print(f"Erro ao fechar a conexão: {e}")


"""Retorna status da conexão"""
def db_esta_conectado():
    return DB_CONECTADO


"""Fecha todas as conexões abertas"""
def fechar_db():
    fechar_conexao()


"""Inicializa o BD - Verifica conexão e cria tabelas se necessário"""
def inicializar_db():
    global DB_CONECTADO
    try:
        with obter_cursor() as cursor:
            # Teste simples
            cursor.execute("SELECT @@VERSION")
            cursor.fetchone()

        # Verifica se a tabela de usuários <usuarios> existe
        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='usuarios' AND xtype='U')
            CREATE TABLE usuarios (
                id INT PRIMARY KEY IDENTITY(1,1),
                username NVARCHAR(50) UNIQUE NOT NULL,
                password NVARCHAR(255) NOT NULL,
                nome_completo NVARCHAR(100) NOT NULL,
                nivel_acesso_id INT NOT NULL DEFAULT 2,
                tema_preferido NVARCHAR(10) DEFAULT 'claro',
                ativo BIT DEFAULT 1,
                data_criacao DATETIME DEFAULT GETDATE(),
                FOREIGN KEY (nivel_acesso_id) REFERENCES niveis_acesso(id)
            )
        """)

        # Verifica se a coluna 'nivel_acesso' já existe
        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='niveis_acesso' AND xtype='U')
            CREATE TABLE niveis_acesso (
                id INT PRIMARY KEY IDENTITY(1,1),
                nome NVARCHAR(50) UNIQUE NOT NULL
            )
        """)

        # Inserir níveis iniciais se não existirem
        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM niveis_acesso WHERE nome='Administrador')
            INSERT INTO niveis_acesso (nome) VALUES ('Administrador')
        """)

        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM niveis_acesso WHERE nome='Usuário')
            INSERT INTO niveis_acesso (nome) VALUES ('Usuário')
        """)

        # Atualiza coluna usuarios.nivel_acesso_id
        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sys.columns 
        WHERE object_id = OBJECT_ID('usuarios') 
            AND name='nivel_acesso_id')
        ALTER TABLE usuarios ADD nivel_acesso_id INT DEFAULT 2  -- 2 = Usuário comum
        """)

        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sys.foreign_keys 
                                WHERE parent_object_id = OBJECT_ID('usuarios') 
                                AND referenced_object_id = OBJECT_ID('niveis_acesso'))
            ALTER TABLE usuarios
            ADD CONSTRAINT FK_Usuarios_NiveisAcesso FOREIGN KEY (nivel_acesso_id)
            REFERENCES niveis_acesso(id)
        """)

        # Verificar se a tabela de tarefas <tasks> existe
        cursor.execute("""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='tasks' AND xtype='U')
            CREATE TABLE tasks (
                id INT PRIMARY KEY IDENTITY(1,1),
                content NVARCHAR(500) NOT NULL,
                due_date DATETIME NOT NULL,
                usuario_id INT,
                data_criacao DATETIME DEFAULT GETDATE(),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        """)

        DB_CONECTADO = True
        return True

    except Exception as e:
        print(f"Erro ao inicializar DB: {e}")
        DB_CONECTADO = False
        return False


"""Verifica as credenciais no SQL Server"""
def verificar_login(username, password):
    try:
        with obter_cursor() as cursor:
            cursor.execute("""
                    SELECT 
                        u.id, 
                        u.username, 
                        u.nome_completo, 
                        u.tema_preferido, 
                        u.ativo, 
                        u.nivel_acesso_id, 
                        n.nome, 
                        u.password
                    FROM usuarios u
                    JOIN niveis_acesso n ON u.nivel_acesso_id = n.id
                    WHERE u.username = ? AND u.ativo = 1
                """, (username,))
            user = cursor.fetchone()
            if user and bcrypt.checkpw(password.encode('utf-8'), user[7].encode('utf-8')):   # Converte a senha STRING em bytes
                return {
                    "id": user[0],
                    "username": user[1],
                    "nome_completo": user[2],
                    "tema_preferido": user[3],
                    "ativo": user[4],
                    "nivel_acesso_id": user[5],
                    "nivel_acesso_nome": user[6]
                }
        return None

    except Exception as e:
        print(f"Erro ao verificar login: {e}")
        return None


"""Operações de Gerenciamento de Usuários"""
def criar_usuario(username, password, nome_completo, nivel_acesso_id=2, ativo=True):
    try:
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        hashed_str = hashed.decode('utf-8') # Salva como STRING
        with obter_cursor() as cursor:
            cursor.execute("""
                INSERT INTO usuarios (username, password, nome_completo, nivel_acesso_id, ativo)
                VALUES (?, ?, ?, ?, ?)
                """, (username, hashed_str, nome_completo, nivel_acesso_id, ativo)
            )
        return True

    except pyodbc.IntegrityError:
        print("Erro: Usuário já existe")
        return False
    except Exception as e:
        print(f"Erro ao criar usuário: {e}")
        return False


def obter_usuarios():
    try:
        with obter_cursor() as cursor:
            cursor.execute("""
                SELECT u.id, 
                    u.username, 
                    u.nome_completo, 
                    n.nome AS nivel_acesso, 
                    u.ativo
                FROM usuarios u
                JOIN niveis_acesso n ON u.nivel_acesso_id = n.id
                ORDER BY u.id ASC
            """)
            return [
                {
                    "id": row[0],
                    "username": row[1],
                    "nome_completo": row[2],
                    "nivel_acesso": row[3],
                    "ativo": row[4]
                } for row in cursor.fetchall()
            ]

    except Exception as e:
        print(f"Erro ao obter usuários: {e}")
        return []


def obter_usuario_por_id(user_id):
    try:
        with obter_cursor() as cursor:
            cursor.execute("""
                SELECT u.id, 
                    u.username, 
                    u.nome_completo, 
                    n.nome AS nivel_acesso, 
                    u.ativo
                FROM usuarios u
                JOIN niveis_acesso n ON u.nivel_acesso_id = n.id
                WHERE u.id = ?
                """, (user_id,)
            )
            row = cursor.fetchone()
            if row:
                return {
                    "id": row[0],
                    "username": row[1],
                    "nome_completo": row[2],
                    "nivel_acesso": row[3],
                    "ativo": row[4]
                }
            return None

    except Exception as e:
        print(f"Erro ao obter usuário por id: {e}")
        return None


def atualizar_usuario(user_id, username=None, password=None, nome_completo=None, nivel_acesso_id=None, ativo=None):
    try:
        updates = []
        params = []
        if username:
            updates.append("username = ?")
            params.append(username)
        if nome_completo:
            updates.append("nome_completo = ?")
            params.append(nome_completo)
        if nivel_acesso_id:
            updates.append("nivel_acesso_id = ?")
            params.append(nivel_acesso_id)
        if ativo is not None:
            updates.append("ativo = ?")
            params.append(ativo)
        if password:
            updates.append("password = ?")
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            params.append(hashed)

        if not updates:
            return False

        query = f"UPDATE usuarios SET {', '.join(updates)} WHERE id = ?"
        params.append(user_id)

        with obter_cursor() as cursor:
            cursor.execute(query, tuple(params))
        return True

    except Exception as e:
        print(f"Erro ao atualizar usuário: {e}")
        return False


def deletar_usuario(user_id):
    try:
        with obter_cursor() as cursor:
            cursor.execute("DELETE FROM usuarios WHERE id = ?", (user_id,))
        return True

    except Exception as e:
        print(f"Erro ao deletar usuário: {e}")
        return False


"""Verifica o tema escolhido pelo usuário"""
def obter_tema_preferido(user_id):
    try:
        with obter_cursor() as cursor:
            cursor.execute("SELECT tema_preferido FROM usuarios WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            return row[0] if row else "claro"

    except Exception as e:
        print(f"Erro ao obter tema: {e}")
        return "claro"


"""Atualiza o tema escolhido pelo usuário"""
def atualizar_preferencia_tema(user_id, tema):
    try:
        with obter_cursor() as cursor:
            cursor.execute("UPDATE usuarios SET tema_preferido = ? WHERE id = ?", (tema, user_id))
        return True

    except Exception as e:
        print(f"Erro ao atualizar tema: {e}")
        return False


"""Operações com tasks vinculadas ao usuário"""
def obter_tarefas_por_usuario_id(user_id):
    try:
        with obter_cursor() as cursor:
            cursor.execute("""
                SELECT id, 
                    content, 
                    due_date 
                FROM tasks WHERE usuario_id = ? 
                ORDER BY due_date ASC
                """, (user_id,)
            )
            return cursor.fetchall()

    except Exception as e:
        print(f"Erro ao obter tarefas: {e}")
        return []


def obter_tarefa(content, due_date, user_id):
    try:
        with obter_cursor() as cursor:
            cursor.execute("""
                INSERT INTO tasks (content, due_date, usuario_id)
                VALUES (?,?,?)
                """, (content, due_date, user_id)
            )

        conn.commit()
        return True

    except Exception as e:
        print(f"Erro ao inserir tarefa: {e}")
        return False


def obter_tarefa_por_id(task_id, user_id):
    try:
        with obter_cursor() as cursor:
            cursor.execute("""
                SELECT id, content, due_date FROM tasks
                WHERE id = ?
                AND usuario_id = ?
                """, (task_id, user_id)
            )

        return cursor.fetchone()

    except Exception as e:
        print(f"Erro ao buscar tarefa por ID: {e}")
        return None


def criar_tarefa(content, due_date, user_id):
    try:
        with obter_cursor() as cursor:
            cursor.execute("""
                INSERT INTO tasks (content, due_date, usuario_id) VALUES (?, ?, ?)
                """, (content, due_date, user_id)
            )
        return True

    except Exception as e:
        print(f"Erro ao criar tarefa: {e}")
        return False


def alterar_tarefa(task_id, content, due_date, user_id):
    try:
        with obter_cursor() as cursor:
            cursor.execute("""
                UPDATE tasks SET content = ?, due_date = ? WHERE id = ? AND usuario_id = ?
                """, (content, due_date, task_id, user_id)
            )
        return True

    except Exception as e:
        print(f"Erro ao alterar tarefa: {e}")
        return False


def deletar_tarefa(task_id, user_id):
    try:
        with obter_cursor() as cursor:
            cursor.execute("DELETE FROM tasks WHERE id = ? AND usuario_id = ?", (task_id, user_id))
        return True

    except Exception as e:
        print(f"Erro ao deletar tarefa: {e}")
        return False
