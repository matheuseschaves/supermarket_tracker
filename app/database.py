# app/database.py
import sqlite3
import shutil
import os
from datetime import datetime
from pathlib import Path

def init_db():
    """Inicializa o banco de dados e cria as tabelas necessárias"""
    conn = sqlite3.connect('supermercado.db')
    cursor = conn.cursor()
    
    # Tabela de supermercados
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS supermercados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        endereco TEXT,
        data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Tabela de categorias de produtos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS categorias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL UNIQUE
    )
    ''')
    
    # Tabela de produtos (COM qnt_medida)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        categoria_id INTEGER,
        marca TEXT,
        unidade_medida TEXT NOT NULL DEFAULT 'un',
        qnt_medida TEXT DEFAULT '',
        FOREIGN KEY (categoria_id) REFERENCES categorias(id)
    )
    ''')
    
    # Tabela de compras (registro de preços)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS compras (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produto_id INTEGER NOT NULL,
        supermercado_id INTEGER NOT NULL,
        preco REAL NOT NULL,
        quantidade REAL DEFAULT 1,
        data_compra DATE NOT NULL,
        promoção BOOLEAN DEFAULT 0,
        quem_pagou TEXT DEFAULT '',  -- NOVO CAMPO
        observacoes TEXT,
        FOREIGN KEY (produto_id) REFERENCES produtos(id),
        FOREIGN KEY (supermercado_id) REFERENCES supermercados(id)
    )
    ''')

    adicionar_coluna_quem_pagou()

    
    # Inserir categorias padrão
    categorias_padrao = [
        'Hortifrúti', 'Laticínios', 'Carnes', 'Padaria',
        'Limpeza', 'Higiene', 'Bebidas', 'Enlatados',
        'Grãos e Cereais', 'Congelados', 'Doces', 'Outros'
    ]
    
    for categoria in categorias_padrao:
        cursor.execute('INSERT OR IGNORE INTO categorias (nome) VALUES (?)', (categoria,))
    
    conn.commit()
    conn.close()
    
    # Verificar e adicionar coluna qnt_medida se não existir
    adicionar_coluna_qnt_medida()


def adicionar_coluna_qnt_medida():
    """Adiciona a coluna qnt_medida se não existir na tabela produtos"""
    conn = sqlite3.connect('supermercado.db')
    cursor = conn.cursor()
    
    try:
        # Verificar se a coluna qnt_medida existe
        cursor.execute("PRAGMA table_info(produtos)")
        colunas = [col[1] for col in cursor.fetchall()]
        
        if 'qnt_medida' not in colunas:
            print("Adicionando coluna 'qnt_medida' à tabela produtos...")
            cursor.execute("ALTER TABLE produtos ADD COLUMN qnt_medida TEXT DEFAULT ''")
            conn.commit()
            print("Coluna 'qnt_medida' adicionada com sucesso!")
    except Exception as e:
        print(f"Erro ao adicionar coluna: {e}")
    finally:
        conn.close()


def get_connection():
    """Retorna uma conexão com o banco de dados"""
    return sqlite3.connect('supermercado.db')


def fazer_backup():
    """Faz backup do banco de dados"""
    backup_dir = Path('backups')
    backup_dir.mkdir(exist_ok=True)
    
    data_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f'supermercado_{data_hora}.db'
    
    if Path('supermercado.db').exists():
        shutil.copy2('supermercado.db', backup_path)
        print(f"Backup criado: {backup_path}")
        return str(backup_path)
    return None


def validar_data_compra(data_str):
    """Valida se a data da compra não é futura"""
    try:
        data_compra = datetime.strptime(data_str, "%d/%m/%Y").date()
        data_atual = datetime.now().date()
        
        if data_compra > data_atual:
            return False, "A data da compra não pode ser futura!"
        return True, ""
    except ValueError:
        return False, "Data inválida! Use o formato DD/MM/AAAA"


def validar_preco(preco_str):
    """Valida se o preço é válido"""
    try:
        preco = float(preco_str.replace(',', '.'))
        if preco <= 0:
            return False, "O preço deve ser maior que zero!"
        return True, preco
    except ValueError:
        return False, "Preço inválido! Use números (ex: 5.99 ou 5,99)"


def buscar_produtos_similares(termo, limite=5):
    """Busca produtos similares ao termo digitado"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    SELECT nome, marca FROM produtos 
    WHERE nome LIKE ? OR marca LIKE ?
    ORDER BY nome
    LIMIT ?
    ''', (f'%{termo}%', f'%{termo}%', limite))
    
    resultados = cursor.fetchall()
    conn.close()
    
    # Formata resultados: "Nome (Marca)" ou apenas "Nome"
    produtos_formatados = []
    for nome, marca in resultados:
        if marca:
            produtos_formatados.append(f"{nome} ({marca})")
        else:
            produtos_formatados.append(nome)
    
    return produtos_formatados

def adicionar_coluna_quem_pagou():
    """Adiciona a coluna quem_pagou se não existir na tabela compras"""
    conn = sqlite3.connect('supermercado.db')
    cursor = conn.cursor()
    
    try:
        # Verificar se a coluna quem_pagou existe
        cursor.execute("PRAGMA table_info(compras)")
        colunas = [col[1] for col in cursor.fetchall()]
        
        if 'quem_pagou' not in colunas:
            print("Adicionando coluna 'quem_pagou' à tabela compras...")
            cursor.execute("ALTER TABLE compras ADD COLUMN quem_pagou TEXT DEFAULT ''")
            conn.commit()
            print("✅ Coluna 'quem_pagou' adicionada com sucesso!")
    except Exception as e:
        print(f"Erro ao adicionar coluna: {e}")
    finally:
        conn.close()