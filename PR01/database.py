import pymysql
from pymysql.err import OperationalError
from tkinter import messagebox
from config import DB_CONFIG
import datetime

def get_db_connection():
    try:
        conn = pymysql.connect(**DB_CONFIG)
        return conn
    except OperationalError as e:
        messagebox.showerror("Erro de Conexão", f"Não foi possível conectar ao banco de dados: {e}\n\nVerifique se o MySQL/XAMPP está rodando.")
        return None

def check_and_fix_table_schema(cursor, table_name, expected_columns_sql):
    try:
        cursor.execute(f"DESCRIBE {table_name}")
        existing_columns = [row[0] for row in cursor.fetchall()]
        if table_name == 'clientes':
            required_cols = {
                'email': 'VARCHAR(255)',
                'cpf': 'VARCHAR(20)',
                'whatsapp': 'VARCHAR(20)',
                'nfes_vinculadas': 'TEXT',
                'data_cadastro': 'DATE',
                'data_nascimento': 'DATE',
                'grupo': "VARCHAR(50) DEFAULT 'CLIENTES'"
            }
            for col, definition in required_cols.items():
                if col not in existing_columns:
                    print(f">>> Migração: Adicionando coluna '{col}' na tabela '{table_name}'...")
                    cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {col} {definition}")
        elif table_name == 'product_cache':
            required_cols = {
                'cod': 'VARCHAR(50)'
            }
            for col, definition in required_cols.items():
                if col not in existing_columns:
                    print(f">>> Migração: Adicionando coluna '{col}' na tabela '{table_name}'...")
                    cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {col} {definition}")
    except Exception as e:
        print(f"Erro ao verificar schema da tabela {table_name}: {e}")

def initialize_database():
    conn = get_db_connection()
    if not conn: return
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(255) NOT NULL,
                telefone VARCHAR(20) NOT NULL,
                grupo VARCHAR(50) NOT NULL,
                data_cadastro DATE NOT NULL,
                INDEX(data_cadastro)
            );
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS mensagens_enviadas (
                id INT AUTO_INCREMENT PRIMARY KEY,
                entity_id INT NOT NULL,
                entity_type VARCHAR(20) NOT NULL,
                dias_key INT NOT NULL,
                data_envio DATETIME NOT NULL,
                UNIQUE KEY uq_msg_sent (entity_id, entity_type, dias_key)
            );
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS produtos_cadastrados (
                id VARCHAR(50) PRIMARY KEY,
                nome VARCHAR(255) NOT NULL
            );
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS compras_detalhadas (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(255),
                cpfcnpj VARCHAR(20),
                endereco VARCHAR(255),
                cep VARCHAR(10),
                bairro VARCHAR(100),
                telefone VARCHAR(20),
                grupo VARCHAR(50),
                nfe VARCHAR(50),
                id_produtos VARCHAR(255),
                data_compra DATE,
                preco DECIMAL(10, 2),
                forma_pagamento VARCHAR(50)
            );
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(255) NOT NULL,
                email VARCHAR(255),
                cpf VARCHAR(20),
                whatsapp VARCHAR(20),
                data_nascimento DATE,
                nfes_vinculadas TEXT,
                data_cadastro DATE,
                grupo VARCHAR(50) DEFAULT 'CLIENTES'
            );
            """)
            check_and_fix_table_schema(cursor, 'clientes', None)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS automacao_mensagens (
                id INT AUTO_INCREMENT PRIMARY KEY,
                tipo_entidade VARCHAR(20) NOT NULL, 
                grupo VARCHAR(50) NOT NULL,
                dias_apos INT NOT NULL,
                texto_mensagem TEXT NOT NULL,
                caminho_imagem VARCHAR(255),
                UNIQUE KEY idx_unique_message_rule (tipo_entidade, grupo, dias_apos)
            );
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS product_cache (
                link VARCHAR(500) PRIMARY KEY,
                cod VARCHAR(50),
                nome TEXT,
                imagem_url TEXT,
                preco_vista VARCHAR(50),
                preco_prazo VARCHAR(50),
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            );
            """)
            check_and_fix_table_schema(cursor, 'product_cache', None)
        conn.commit()
        print(">>> Banco de dados verificado.")
    except Exception as e:
        messagebox.showerror("Erro de BD", f"Falha ao criar tabelas: {e}")
    finally:
        if conn: conn.close()

def remover_lead_por_telefone(telefone):
    conn = get_db_connection()
    if not conn: return
    try:
        with conn.cursor() as cursor:
            nums = ''.join(filter(str.isdigit, str(telefone)))
            cursor.execute("DELETE FROM leads WHERE telefone LIKE %s", (f"%{nums}%",))
        conn.commit()
    except Exception as e:
        print(f"Erro ao remover lead: {e}")
    finally:
        conn.close()
        
def obter_grupos_cadastrados():
    conn = get_db_connection()
    grupos = set()
    if not conn: return ["OUTROS"]
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT DISTINCT grupo FROM leads")
            for r in cursor.fetchall(): 
                if r[0]: grupos.add(r[0])
            cursor.execute("SELECT DISTINCT grupo FROM compras_detalhadas")
            for r in cursor.fetchall(): 
                if r[0]: grupos.add(r[0])
            cursor.execute("SELECT DISTINCT grupo FROM clientes")
            for r in cursor.fetchall(): 
                if r[0]: grupos.add(r[0])
    except: pass
    finally: conn.close()
    
    lista = sorted(list(grupos))
    return lista if lista else ["OUTROS"]

def get_cached_product(link):
    conn = get_db_connection()
    if not conn: return None
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT nome, imagem_url, preco_vista, preco_prazo, cod FROM product_cache WHERE link = %s", (link,))
            result = cursor.fetchone()
            if result:
                return {
                    "link": link, 
                    "nome": result[0], 
                    "imagem_url": result[1], 
                    "preco_vista": result[2], 
                    "preco_prazo": result[3],
                    "cod": result[4]
                }
    except Exception as e:
        print(f"Erro ao buscar cache: {e}")
    finally:
        conn.close()
    return None

def get_all_products_from_cache():
    conn = get_db_connection()
    if not conn: return []
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT nome, link, imagem_url, preco_vista, preco_prazo, cod FROM product_cache ORDER BY nome")
            results = cursor.fetchall()
            products = []
            for row in results:
                products.append({
                    "nome": row[0],
                    "link": row[1],
                    "imagem_url": row[2],
                    "preco_vista": row[3],
                    "preco_prazo": row[4],
                    "cod": row[5]
                })
            return products
    except Exception as e:
        print(f"Erro ao buscar todos do cache: {e}")
        return []
    finally:
        conn.close()

def save_product_to_cache(data):
    conn = get_db_connection()
    if not conn: return
    try:
        link = data.get('link', '')
        nome = data.get('nome', data.get('name', 'Sem Nome'))
        img = data.get('imagem_url', data.get('image_url', ''))
        pv = data.get('preco_vista', data.get('price_cash', '0,00'))
        pp = data.get('preco_prazo', data.get('price_install', ''))
        cod = data.get('cod', '')

        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO product_cache (link, nome, imagem_url, preco_vista, preco_prazo, cod)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                nome=%s, imagem_url=%s, preco_vista=%s, preco_prazo=%s, cod=%s
            """, (link, nome, img, pv, pp, cod, nome, img, pv, pp, cod))
        conn.commit()
    except Exception as e:
        print(f"Erro ao salvar cache: {e}")
    finally:
        conn.close()