# gui/dialogs.py
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from app.database import get_connection


class ProdutoDialog:
    """Diálogo para cadastro/edição de produtos"""
    
    def __init__(self, parent, produto_id=None, callback=None):
        self.parent = parent
        self.produto_id = produto_id
        self.callback = callback
        
        self.janela = tk.Toplevel(parent)
        self.janela.title("Novo Produto" if not produto_id else "Editar Produto")
        self.janela.geometry("400x400")
        self.janela.transient(parent)
        self.janela.grab_set()
        
        self.criar_widgets()
        self.carregar_dados()
    
    def criar_widgets(self):
        """Cria os widgets do diálogo"""
        # Frame principal
        main_frame = ttk.Frame(self.janela, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Nome do Produto
        ttk.Label(main_frame, text="Nome do Produto*:").grid(
            row=0, column=0, sticky='w', pady=(0, 5))
        self.entry_nome = ttk.Entry(main_frame, width=40)
        self.entry_nome.grid(row=0, column=1, pady=(0, 5), padx=(5, 0))
        
        # Categoria
        ttk.Label(main_frame, text="Categoria:").grid(
            row=1, column=0, sticky='w', pady=5)
        self.combo_categoria = ttk.Combobox(main_frame, width=37)
        self.combo_categoria.grid(row=1, column=1, pady=5, padx=(5, 0))
        
        # Marca
        ttk.Label(main_frame, text="Marca (opcional):").grid(
            row=2, column=0, sticky='w', pady=5)
        self.entry_marca = ttk.Entry(main_frame, width=40)
        self.entry_marca.grid(row=2, column=1, pady=5, padx=(5, 0))
        
        # Unidade de Medida
        ttk.Label(main_frame, text="Unidade de Medida:").grid(
            row=3, column=0, sticky='w', pady=5)
        self.combo_unidade = ttk.Combobox(main_frame, 
                                         values=["un", "kg", "g", "L", "ml", "cx"], 
                                         width=10)
        self.combo_unidade.set("un")
        self.combo_unidade.grid(row=3, column=1, sticky='w', pady=5, padx=(5, 0))
        
        # Quantidade da Medida (NOVO)
        ttk.Label(main_frame, text="Quantidade Medida:").grid(
            row=4, column=0, sticky='w', pady=5)
        self.entry_qnt_medida = ttk.Entry(main_frame, width=20)
        self.entry_qnt_medida.grid(row=4, column=1, sticky='w', pady=5, padx=(5, 0))
        ttk.Label(main_frame, text="ex: 500g, 1L, 12un").grid(
            row=4, column=1, sticky='e', pady=5, padx=(5, 0))
        
        # Frame para botões
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=20)
        
        ttk.Button(button_frame, text="Salvar", 
                  command=self.salvar_produto).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Cancelar", 
                  command=self.janela.destroy).pack(side='left', padx=5)
    
    def carregar_dados(self):
        """Carrega categorias e dados do produto (se edição)"""
        conn = get_connection()
        cursor = conn.cursor()
        
        # Carregar categorias
        cursor.execute("SELECT nome FROM categorias ORDER BY nome")
        categorias = [row[0] for row in cursor.fetchall()]
        self.combo_categoria['values'] = categorias
        
        # Se for edição, carregar dados do produto
        if self.produto_id:
            cursor.execute('''
            SELECT p.nome, c.nome, p.marca, p.unidade_medida, p.qnt_medida
            FROM produtos p
            LEFT JOIN categorias c ON p.categoria_id = c.id
            WHERE p.id = ?
            ''', (self.produto_id,))
            
            produto = cursor.fetchone()
            if produto:
                self.entry_nome.insert(0, produto[0] or "")
                self.combo_categoria.set(produto[1] or "")
                self.entry_marca.insert(0, produto[2] or "")
                self.combo_unidade.set(produto[3] or "un")
                self.entry_qnt_medida.insert(0, produto[4] or "")
        
        conn.close()
    
    def salvar_produto(self):
        """Salva o produto no banco de dados"""
        nome = self.entry_nome.get().strip()
        categoria = self.combo_categoria.get().strip()
        
        if not nome:
            messagebox.showerror("Erro", "Informe o nome do produto!")
            return
        
        conn = get_connection()
        cursor = conn.cursor()
        
        # Obter ID da categoria
        categoria_id = None
        if categoria:
            cursor.execute("SELECT id FROM categorias WHERE nome = ?", (categoria,))
            result = cursor.fetchone()
            if result:
                categoria_id = result[0]
        
        # Preparar dados
        marca = self.entry_marca.get().strip() or None
        unidade = self.combo_unidade.get()
        qnt_medida = self.entry_qnt_medida.get().strip() or None
        
        try:
            if self.produto_id:
                # Atualizar produto existente
                cursor.execute('''
                UPDATE produtos 
                SET nome = ?, categoria_id = ?, marca = ?, 
                    unidade_medida = ?, qnt_medida = ?
                WHERE id = ?
                ''', (nome, categoria_id, marca, unidade, qnt_medida, self.produto_id))
            else:
                # Inserir novo produto
                cursor.execute('''
                INSERT INTO produtos (nome, categoria_id, marca, unidade_medida, qnt_medida)
                VALUES (?, ?, ?, ?, ?)
                ''', (nome, categoria_id, marca, unidade, qnt_medida))
            
            conn.commit()
            messagebox.showinfo("Sucesso", 
                "Produto atualizado com sucesso!" if self.produto_id 
                else "Produto cadastrado com sucesso!")
            
            if self.callback:
                self.callback()
            
            self.janela.destroy()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")
        finally:
            conn.close()