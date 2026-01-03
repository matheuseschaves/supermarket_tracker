# gui/main_window.py
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, date
from pathlib import Path
import sys
import os

# Adiciona o diretório pai ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Agora importa os módulos locais
try:
    from app.database import init_db, get_connection, fazer_backup, validar_data_compra, validar_preco
    from app.utils import formatar_moeda, extrair_nome_produto, extrair_marca_produto
    from .dialogs import ProdutoDialog
    from .widgets import AutoCompleteCombobox, ValidatedEntry
except ImportError as e:
    print(f"Erro ao importar módulos: {e}")
    print(f"Diretório atual: {os.getcwd()}")
    print(f"Caminho do script: {__file__}")
    raise

class SupermercadoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Supermercado Price Tracker")
        self.root.geometry("1000x700")
        
        # Inicializar banco de dados
        init_db()
        
        # Fazer backup automático
        backup_path = fazer_backup()
        if backup_path:
            print(f"Backup criado: {backup_path}")
        
        # Configurar estilo
        self.setup_styles()
        
        # Criar interface
        self.create_widgets()
        
        # Carregar dados iniciais
        self.load_data()

        self.carregar_sugestoes_quem_pagou()
    
    def setup_styles(self):
        """Configura estilos para a interface"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar cores
        style.configure('TLabel', padding=5)
        style.configure('TButton', padding=5)
        style.configure('Treeview', rowheight=25)
    
    def create_widgets(self):
        """Cria todos os widgets da interface"""
        # Frame principal com notebook (abas)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Aba 1: Registrar Compra
        self.frame_registrar = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_registrar, text='📝 Registrar Compra')
        self.create_registrar_tab()
        
        # Aba 2: Consultar Preços
        self.frame_consultar = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_consultar, text='🔍 Consultar Preços')
        self.create_consultar_tab()
        
        # Aba 3: Estatísticas
        self.frame_estatisticas = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_estatisticas, text='📊 Estatísticas')
        self.create_estatisticas_tab()
        
        # Aba 4: Gerenciar Produtos
        self.frame_produtos = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_produtos, text='📦 Gerenciar Produtos')
        self.create_produtos_tab()
        
        # Menu
        self.create_menu()
    
    def create_menu(self):
        """Cria a barra de menu"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu Arquivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Fazer Backup", command=self.fazer_backup_manual)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.root.quit)
        
        # Menu Ajuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ajuda", menu=help_menu)
        help_menu.add_command(label="Sobre", command=self.mostrar_sobre)
    
    def criar_campos_registro(self, form_frame):
        """Cria os campos do formulário de registro"""
        # Produto
        ttk.Label(form_frame, text="Produto*:").grid(
            row=0, column=0, sticky='w', pady=5)
        self.produto_var = tk.StringVar()
        self.combo_produto = AutoCompleteCombobox(form_frame, textvariable=self.produto_var, width=30)
        self.combo_produto.grid(row=0, column=1, pady=5, padx=5)
        
        # Botão para novo produto
        ttk.Button(form_frame, text="+ Novo", command=self.novo_produto, 
                  width=10).grid(row=0, column=2, padx=5)
        
        # Supermercado
        ttk.Label(form_frame, text="Supermercado*:").grid(
            row=1, column=0, sticky='w', pady=5)
        self.supermercado_var = tk.StringVar()
        self.combo_supermercado = ttk.Combobox(form_frame, textvariable=self.supermercado_var, width=30)
        self.combo_supermercado.grid(row=1, column=1, pady=5, padx=5)
        
        # Preço
        ttk.Label(form_frame, text="Preço (R$)*:").grid(
            row=2, column=0, sticky='w', pady=5)
        self.entry_preco = ValidatedEntry(form_frame, validate_type='float', width=15)
        self.entry_preco.grid(row=2, column=1, sticky='w', pady=5, padx=5)
        
        # Quantidade
        ttk.Label(form_frame, text="Quantidade*:").grid(
            row=3, column=0, sticky='w', pady=5)
        frame_qtd = ttk.Frame(form_frame)
        frame_qtd.grid(row=3, column=1, sticky='w', pady=5)
        
        self.entry_quantidade = ValidatedEntry(frame_qtd, validate_type='float', width=10)
        self.entry_quantidade.insert(0, "1")
        self.entry_quantidade.pack(side='left', padx=5)
        
        self.unidade_var = tk.StringVar(value="un")
        ttk.Combobox(frame_qtd, textvariable=self.unidade_var, 
                     values=["un", "kg", "g", "L", "ml", "cx"], width=8).pack(side='left')
        
        # Data
        ttk.Label(form_frame, text="Data (DD/MM/AAAA)*:").grid(
            row=4, column=0, sticky='w', pady=5)
        self.entry_data = ValidatedEntry(form_frame, validate_type='date', width=15)
        self.entry_data.insert(0, date.today().strftime("%d/%m/%Y"))
        self.entry_data.grid(row=4, column=1, sticky='w', pady=5, padx=5)
        
        # Promoção
        self.promocao_var = tk.BooleanVar()
        ttk.Checkbutton(form_frame, text="Em promoção", 
                       variable=self.promocao_var).grid(row=5, column=1, sticky='w', pady=5)
        
        #Quem Pagou
        ttk.Label(form_frame,text="Quem Pagou:").grid(
            row=6, column=0, sticky='w', pady=5)
        self.quem_pagou_var = tk.StringVar()
        self.combo_quem_pagou = ttk.Combobox(
            form_frame,
            textvariable=self.quem_pagou_var,
            values=["Eu", "Nadiny", "Outro"],
            width=15
        )
        self.combo_quem_pagou.grid(row=6, column=1, sticky='w', pady=5, padx=5)
        self.combo_quem_pagou.set("Eu") #Valor padrao

        # Observações
        ttk.Label(form_frame, text="Observações:").grid(
            row=9, column=0, sticky='nw', pady=5)
        self.text_observacoes = tk.Text(form_frame, height=4, width=30)
        self.text_observacoes.grid(row=9, column=1, pady=5, padx=5, sticky='w')

    def carregar_sugestoes_quem_pagou(self):
        """Carrega sugestões de quem pagou baseado no histórico"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT DISTINCT quem_pagou 
        FROM compras 
        WHERE quem_pagou != ''
        ORDER BY quem_pagou
        ''')
        
        sugestoes = [row[0] for row in cursor.fetchall()]
        
        # Adicionar valores padrão se não existirem
        valores_padrao = ["Eu", "Parceiro(a)", "Família", "Amigo", "Outro"]
        todos_valores = list(set(sugestoes + valores_padrao))
        
        # Atualizar o combobox
        self.combo_quem_pagou['values'] = todos_valores
        
        conn.close()
    
    def criar_botoes_registro(self, form_frame):
        """Cria os botões do formulário de registro"""
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=7, column=0, columnspan=3, pady=15)
        
        ttk.Button(button_frame, text="✅ Registrar Compra", 
                  command=self.registrar_compra).pack(side='left', padx=5)
        ttk.Button(button_frame, text="🧹 Limpar", 
                  command=self.limpar_formulario).pack(side='left', padx=5)
    
    def create_registrar_tab(self):
        """Cria a aba de registro de compras"""
        # Frame para formulário
        form_frame = ttk.LabelFrame(self.frame_registrar, text="Nova Compra", padding=15)
        form_frame.pack(fill='x', padx=10, pady=10)
        
        # Criar campos
        self.criar_campos_registro(form_frame)
        
        # Criar botões
        self.criar_botoes_registro(form_frame)
        
        # Frame para últimas compras
        historico_frame = ttk.LabelFrame(self.frame_registrar, text="Últimas Compras", padding=10)
        historico_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Treeview para histórico
        columns = ('Data', 'Produto', 'Supermercado', 'Preço', 'Qtd', 'Promoção', "Quem Pagou")
        self.tree_historico = ttk.Treeview(historico_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.tree_historico.heading(col, text=col)
            self.tree_historico.column(col, width=100)
        
        self.tree_historico.pack(fill='both', expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(historico_frame, orient='vertical', command=self.tree_historico.yview)
        self.tree_historico.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
    
    def create_consultar_tab(self):
        """Cria a aba de consulta de preços"""
        # Frame de filtros
        filter_frame = ttk.LabelFrame(self.frame_consultar, text="Filtros", padding=10)
        filter_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(filter_frame, text="Produto:").grid(row=0, column=0, padx=5)
        self.consulta_produto_var = tk.StringVar()
        self.combo_consulta_produto = AutoCompleteCombobox(filter_frame, 
                                                          textvariable=self.consulta_produto_var, 
                                                          width=25)
        self.combo_consulta_produto.grid(row=0, column=1, padx=5)
        
        ttk.Label(filter_frame, text="Supermercado:").grid(row=0, column=2, padx=5)
        self.consulta_supermercado_var = tk.StringVar()
        ttk.Combobox(filter_frame, textvariable=self.consulta_supermercado_var, 
                     width=25).grid(row=0, column=3, padx=5)
        
        ttk.Button(filter_frame, text="🔍 Buscar", 
                  command=self.buscar_precos).grid(row=0, column=4, padx=10)
        ttk.Button(filter_frame, text="🧹 Limpar Filtros", 
                  command=self.limpar_filtros).grid(row=0, column=5, padx=5)
        
        # Treeview para resultados
        result_frame = ttk.Frame(self.frame_consultar)
        result_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        columns = ('Data', 'Produto', 'Supermercado', 'Preço', 'Preço/Un', 'Qtd', 'Promoção')
        self.tree_consulta = ttk.Treeview(result_frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            self.tree_consulta.heading(col, text=col)
            self.tree_consulta.column(col, width=100)
        
        self.tree_consulta.pack(side='left', fill='both', expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(result_frame, orient='vertical', command=self.tree_consulta.yview)
        self.tree_consulta.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        
        # Frame de estatísticas rápidas
        stats_frame = ttk.LabelFrame(self.frame_consultar, text="Estatísticas do Produto", padding=10)
        stats_frame.pack(fill='x', padx=10, pady=10)
        
        self.stats_text = tk.Text(stats_frame, height=4, width=80)
        self.stats_text.pack(fill='x', pady=5)
    
    def create_estatisticas_tab(self):
        """Cria a aba de estatísticas"""
        # Frame para gráficos
        graph_frame = ttk.LabelFrame(self.frame_estatisticas, text="Gráficos", padding=10)
        graph_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Área para gráfico
        self.graph_canvas = tk.Canvas(graph_frame, bg='white')
        self.graph_canvas.pack(fill='both', expand=True)
        
        # Frame para controles
        control_frame = ttk.Frame(self.frame_estatisticas)
        control_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(control_frame, text="Produto:").pack(side='left', padx=5)
        self.graph_produto_var = tk.StringVar()
        self.combo_graph_produto = AutoCompleteCombobox(control_frame, 
                                                       textvariable=self.graph_produto_var, 
                                                       width=30)
        self.combo_graph_produto.pack(side='left', padx=5)
        
        ttk.Button(control_frame, text="📈 Gerar Gráfico", 
                  command=self.gerar_grafico).pack(side='left', padx=10)
    
    def create_produtos_tab(self):
        """Cria a aba de gerenciamento de produtos"""
        # Frame para lista de produtos
        list_frame = ttk.LabelFrame(self.frame_produtos, text="Produtos Cadastrados", padding=10)
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Treeview para produtos
        columns = ('ID', 'Nome', 'Categoria', 'Marca', 'Unidade', 'Qnt Medida')
        self.tree_produtos = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.tree_produtos.heading(col, text=col)
        
        self.tree_produtos.column('ID', width=50)
        self.tree_produtos.column('Nome', width=200)
        self.tree_produtos.column('Categoria', width=120)
        self.tree_produtos.column('Marca', width=120)
        self.tree_produtos.column('Unidade', width=80)
        self.tree_produtos.column('Qnt Medida', width=100)
        
        self.tree_produtos.pack(side='left', fill='both', expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.tree_produtos.yview)
        self.tree_produtos.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        
        # Frame para botões
        button_frame = ttk.Frame(self.frame_produtos)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(button_frame, text="➕ Novo Produto", 
                  command=self.novo_produto).pack(side='left', padx=5)
        ttk.Button(button_frame, text="✏️ Editar", 
                  command=self.editar_produto).pack(side='left', padx=5)
        ttk.Button(button_frame, text="🗑️ Excluir", 
                  command=self.excluir_produto).pack(side='left', padx=5)
        ttk.Button(button_frame, text="🔄 Atualizar Lista", 
                  command=self.load_produtos).pack(side='left', padx=5)
        
        # Adicionar menu de contexto
        self.menu_contexto = tk.Menu(self.root, tearoff=0)
        self.menu_contexto.add_command(label="Editar", command=self.editar_produto)
        self.menu_contexto.add_command(label="Excluir", command=self.excluir_produto)
        self.menu_contexto.add_separator()
        self.menu_contexto.add_command(label="Ver Compras", command=self.ver_compras_produto)

        # Vincular menu de contexto à treeview
        self.tree_produtos.bind("<Button-3>", self.mostrar_menu_contexto)
        
        # Também permitir editar com duplo clique
        self.tree_produtos.bind("<Double-1>", lambda e: self.editar_produto())
    
    def load_data(self):
        """Carrega dados iniciais nos comboboxes"""
        conn = get_connection()
        cursor = conn.cursor()
        
        # Carregar produtos
        cursor.execute("SELECT nome, marca FROM produtos ORDER BY nome")
        produtos = [f"{row[0]} ({row[1]})" if row[1] else row[0] for row in cursor.fetchall()]
        self.combo_produto['values'] = produtos
        self.combo_produto.set('')
        
        # Carregar supermercados
        cursor.execute("SELECT nome FROM supermercados ORDER BY nome")
        supermercados = [row[0] for row in cursor.fetchall()]
        self.combo_supermercado['values'] = supermercados
        self.combo_supermercado.set('')
        
        # Carregar histórico recente
        self.carregar_historico()
        
        # Carregar produtos para consulta
        self.consulta_produto_var.set('')
        
        # Carregar produtos para gráfico
        self.graph_produto_var.set('')
        
        # Carregar lista de produtos
        self.load_produtos()
        
        conn.close()
    
    def carregar_historico(self):
        """Carrega as últimas compras no histórico"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT c.data_compra, p.nome, s.nome, c.preco, c.quantidade, c.promoção, c.quem_pagou
        FROM compras c
        JOIN produtos p ON c.produto_id = p.id
        JOIN supermercados s ON c.supermercado_id = s.id
        ORDER BY c.data_compra DESC
        LIMIT 20
        ''')
        
        # Limpar treeview
        for item in self.tree_historico.get_children():
            self.tree_historico.delete(item)
        
        # Adicionar novos itens
        for row in cursor.fetchall():
            data = row[0]
            produto = row[1]
            supermercado = row[2]
            preco = formatar_moeda(row[3])
            qtd = f"{row[4]} un"
            promocao = "✅" if row[5] else "❌"
            quem_pagou = row[6] if row[6] else "Não informado"
            
            self.tree_historico.insert('', 'end', 
                                      values=(data, produto, supermercado, preco, qtd, promocao, quem_pagou))
        
        conn.close()
    
    def registrar_compra(self):
        """Registra uma nova compra no banco de dados"""
        # Validar campos obrigatórios
        produto_text = self.produto_var.get()
        supermercado = self.supermercado_var.get()
        preco_text = self.entry_preco.get()
        data_text = self.entry_data.get()
        quantidade_text = self.entry_quantidade.get()
        
        if not all([produto_text, supermercado, preco_text, data_text, quantidade_text]):
            messagebox.showerror("Erro", "Preencha todos os campos obrigatórios!")
            return
        
        # Validar data (não pode ser futura)
        valido, mensagem = validar_data_compra(data_text)
        if not valido:
            messagebox.showerror("Erro", mensagem)
            return
        
        # Validar preço (deve ser > 0)
        valido, preco_val = validar_preco(preco_text)
        if not valido:
            messagebox.showerror("Erro", preco_val)
            return
        
        try:
            # Extrair nome do produto (remover marca se houver)
            if '(' in produto_text and ')' in produto_text:
                produto_nome = produto_text.split('(')[0].strip()
            else:
                produto_nome = produto_text
            
            # Converter quantidade
            quantidade = float(quantidade_text.replace(',', '.'))
            
            if quantidade <= 0:
                messagebox.showerror("Erro", "A quantidade deve ser maior que zero!")
                return
            
            conn = get_connection()
            cursor = conn.cursor()
            
            # Buscar produto pelo nome (CORREÇÃO DO BUG - buscar exatamente pelo nome)
            cursor.execute("SELECT id FROM produtos WHERE nome = ?", (produto_nome,))
            produto_id = cursor.fetchone()
            
            if not produto_id:
                # Tentar buscar ignorando espaços extras
                cursor.execute("SELECT id FROM produtos WHERE TRIM(nome) = ?", (produto_nome.strip(),))
                produto_id = cursor.fetchone()
            
            if not produto_id:
                messagebox.showerror("Erro", 
                    f"Produto '{produto_nome}' não encontrado!\n"
                    "Cadastre o produto primeiro ou verifique o nome.")
                conn.close()
                return
            
            produto_id = produto_id[0]
            
            # Buscar/inserir supermercado
            cursor.execute("SELECT id FROM supermercados WHERE nome = ?", (supermercado,))
            supermercado_id = cursor.fetchone()
            
            if not supermercado_id:
                cursor.execute("INSERT INTO supermercados (nome) VALUES (?)", (supermercado,))
                supermercado_id = cursor.lastrowid
            else:
                supermercado_id = supermercado_id[0]
            
            # Converter data
            data_obj = datetime.strptime(data_text, "%d/%m/%Y").date()
            
            # Inserir compra
            cursor.execute('''
            INSERT INTO compras (produto_id, supermercado_id, preco, quantidade, 
                               data_compra, promoção,quem_pagou, observacoes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (produto_id, supermercado_id, preco_val, quantidade, 
                  data_obj, 1 if self.promocao_var.get() else 0,self.quem_pagou_var.get(),
                  self.text_observacoes.get("1.0", "end-1c")))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("✅ Sucesso", "Compra registrada com sucesso!")
            self.limpar_formulario()
            self.carregar_historico()
            self.load_data()  # Atualizar comboboxes
            
        except ValueError as e:
            messagebox.showerror("Erro", f"Valor inválido: {str(e)}")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro: {str(e)}")
    
    def limpar_formulario(self):
        """Limpa o formulário de registro"""
        self.produto_var.set('')
        self.supermercado_var.set('')
        self.entry_preco.delete(0, 'end')
        self.entry_quantidade.delete(0, 'end')
        self.entry_quantidade.insert(0, "1")
        self.entry_data.delete(0, 'end')
        self.entry_data.insert(0, date.today().strftime("%d/%m/%Y"))
        self.promocao_var.set(False)
        self.quem_pagou_var.set("Eu")  # NOVO: resetar para valor padrão
        self.text_observacoes.delete("1.0", "end")
    
    def buscar_precos(self):
        """Busca preços com base nos filtros"""
        produto = self.consulta_produto_var.get()
        supermercado = self.consulta_supermercado_var.get()
        
        conn = get_connection()
        cursor = conn.cursor()
        
        query = '''
        SELECT c.data_compra, p.nome, s.nome, c.preco, c.quantidade, 
               c.preco/c.quantidade as preco_unitario, c.promoção, c.quem_pagou
        FROM compras c
        JOIN produtos p ON c.produto_id = p.id
        JOIN supermercados s ON c.supermercado_id = s.id
        WHERE 1=1
        '''
        params = []
        
        if produto:
            # Extrair apenas o nome do produto (remover marca)
            if '(' in produto and ')' in produto:
                produto_nome = produto.split('(')[0].strip()
            else:
                produto_nome = produto
            query += " AND p.nome LIKE ?"
            params.append(f"%{produto_nome}%")
        
        if supermercado:
            query += " AND s.nome LIKE ?"
            params.append(f"%{supermercado}%")
        
        query += " ORDER BY c.data_compra DESC"
        
        cursor.execute(query, params)
        
        # Limpar treeview
        for item in self.tree_consulta.get_children():
            self.tree_consulta.delete(item)
        
        # Adicionar resultados
        for row in cursor.fetchall():
            data = row[0]
            produto_nome = row[1]
            supermercado_nome = row[2]
            preco = formatar_moeda(row[3])
            preco_unit = formatar_moeda(row[5])
            qtd = f"{row[4]}"
            promocao = "✅" if row[6] else "❌"
            quem_pagou = row[7] if row[7] else "Não informado"
            
            self.tree_consulta.insert('', 'end', 
                                    values=(data, produto_nome, supermercado_nome, 
                                            preco, preco_unit, qtd, promocao, quem_pagou))
        
        # Calcular estatísticas
        if produto:
            self.calcular_estatisticas(produto_nome if 'produto_nome' in locals() else produto)
        
        conn.close()
    
    def calcular_estatisticas(self, produto):
        """Calcula estatísticas para um produto"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT 
            MIN(c.preco/c.quantidade) as min_preco,
            MAX(c.preco/c.quantidade) as max_preco,
            AVG(c.preco/c.quantidade) as avg_preco,
            COUNT(*) as total_compras,
            MIN(c.data_compra) as primeira_compra,
            MAX(c.data_compra) as ultima_compra
        FROM compras c
        JOIN produtos p ON c.produto_id = p.id
        WHERE p.nome LIKE ?
        ''', (f"%{produto}%",))
        
        stats = cursor.fetchone()
        
        if stats and stats[3] > 0:
            self.stats_text.delete("1.0", "end")
            self.stats_text.insert("1.0", 
                f"📊 Estatísticas para '{produto}':\n"
                f"• Total de registros: {stats[3]}\n"
                f"• Período: {stats[4]} a {stats[5]}\n"
                f"• Preço médio: {formatar_moeda(stats[2])}\n"
                f"• Menor preço: {formatar_moeda(stats[0])}\n"
                f"• Maior preço: {formatar_moeda(stats[1])}"
            )
        
        conn.close()
    
    def limpar_filtros(self):
        """Limpa os filtros de consulta"""
        self.consulta_produto_var.set('')
        self.consulta_supermercado_var.set('')
        self.stats_text.delete("1.0", "end")
        
        # Limpar treeview
        for item in self.tree_consulta.get_children():
            self.tree_consulta.delete(item)
    
    def novo_produto(self):
        """Abre janela para cadastrar novo produto"""
        ProdutoDialog(self.root, callback=self.load_data)
    
    def load_produtos(self):
        """Carrega a lista de produtos"""
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT p.id, p.nome, COALESCE(c.nome, 'Sem categoria'), 
               COALESCE(p.marca, ''), p.unidade_medida, COALESCE(p.qnt_medida, '')
        FROM produtos p
        LEFT JOIN categorias c ON p.categoria_id = c.id
        ORDER BY p.nome
        ''')
        
        # Limpar treeview
        for item in self.tree_produtos.get_children():
            self.tree_produtos.delete(item)
        
        # Adicionar produtos
        for row in cursor.fetchall():
            self.tree_produtos.insert('', 'end', values=row)
        
        conn.close()
    
    def editar_produto(self):
        """Edita o produto selecionado"""
        selecionado = self.tree_produtos.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um produto para editar!")
            return
        
        # Obter dados do produto selecionado
        item = self.tree_produtos.item(selecionado[0])
        produto_id = item['values'][0]
        
        ProdutoDialog(self.root, produto_id=produto_id, callback=self.load_data)
    
    def excluir_produto(self):
        """Exclui o produto selecionado"""
        selecionado = self.tree_produtos.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um produto para excluir!")
            return
        
        item = self.tree_produtos.item(selecionado[0])
        produto_id = item['values'][0]
        produto_nome = item['values'][1]
        
        resposta = messagebox.askyesno("Confirmar Exclusão", 
                                      f"⚠️  Deseja realmente excluir o produto:\n\n"
                                      f"'{produto_nome}'?\n\n"
                                      "Esta ação não pode ser desfeita!")
        
        if resposta:
            conn = get_connection()
            cursor = conn.cursor()
            
            try:
                # Verificar se há compras associadas
                cursor.execute("SELECT COUNT(*) FROM compras WHERE produto_id = ?", (produto_id,))
                count_compras = cursor.fetchone()[0]
                
                if count_compras > 0:
                    # Perguntar se quer excluir as compras também
                    resposta2 = messagebox.askyesno("Compras Encontradas",
                        f"⚠️  Este produto possui {count_compras} compra(s) registrada(s).\n\n"
                        "Deseja excluir o produto E TODAS as suas compras?\n"
                        "Ou apenas cancelar a exclusão?")
                    
                    if resposta2:
                        # Excluir compras primeiro, depois o produto
                        cursor.execute("DELETE FROM compras WHERE produto_id = ?", (produto_id,))
                        cursor.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
                        conn.commit()
                        messagebox.showinfo("✅ Sucesso", 
                            f"Produto '{produto_nome}' e suas {count_compras} compra(s) foram excluídos.")
                    else:
                        messagebox.showinfo("Cancelado", 
                            "Exclusão cancelada. O produto não foi removido.")
                        conn.close()
                        return
                else:
                    # Não tem compras, só excluir o produto
                    cursor.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
                    conn.commit()
                    messagebox.showinfo("✅ Sucesso", "Produto excluído com sucesso!")
                
                # Atualizar a lista
                self.load_produtos()
                self.load_data()
                
            except Exception as e:
                messagebox.showerror("❌ Erro", f"Ocorreu um erro ao excluir: {str(e)}")
            finally:
                conn.close()
    
    def mostrar_menu_contexto(self, event):
        """Mostra menu de contexto ao clicar com botão direito"""
        # Identificar item clicado
        item = self.tree_produtos.identify_row(event.y)
        if item:
            # Selecionar o item
            self.tree_produtos.selection_set(item)
            # Mostrar menu na posição do clique
            self.menu_contexto.post(event.x_root, event.y_root)
    
    def ver_compras_produto(self):
        """Mostra todas as compras do produto selecionado"""
        selecionado = self.tree_produtos.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um produto!")
            return
        
        item = self.tree_produtos.item(selecionado[0])
        produto_nome = item['values'][1]
        
        # Mudar para aba de consulta e preencher o filtro
        self.notebook.select(self.frame_consultar)
        self.consulta_produto_var.set(produto_nome)
        self.buscar_precos()
        
        # Rolar para o topo
        self.tree_consulta.yview_moveto(0)
    
    def gerar_grafico(self):
        """Gera gráfico de evolução de preços"""
        produto = self.graph_produto_var.get()
        if not produto:
            messagebox.showwarning("Aviso", "Selecione um produto!")
            return
        
        # Extrair nome do produto (remover marca)
        if '(' in produto and ')' in produto:
            produto_nome = produto.split('(')[0].strip()
        else:
            produto_nome = produto
        
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT c.data_compra, c.preco/c.quantidade as preco_unitario, s.nome
        FROM compras c
        JOIN produtos p ON c.produto_id = p.id
        JOIN supermercados s ON c.supermercado_id = s.id
        WHERE p.nome LIKE ?
        ORDER BY c.data_compra
        ''', (f"%{produto_nome}%",))
        
        dados = cursor.fetchall()
        conn.close()
        
        if not dados:
            messagebox.showinfo("Info", "Nenhum dado encontrado para este produto!")
            return
        
        # Preparar dados para o gráfico
        from datetime import datetime
        datas = [datetime.strptime(row[0], "%Y-%m-%d") for row in dados]
        precos = [row[1] for row in dados]
        supermercados = [row[2] for row in dados]
        
        # Limpar canvas anterior
        for widget in self.graph_canvas.winfo_children():
            widget.destroy()
        
        # Criar figura do matplotlib
        fig, ax = plt.subplots(figsize=(8, 4))
        
        # Agrupar por supermercado
        supermercados_unicos = list(set(supermercados))
        cores = plt.cm.Set3(range(len(supermercados_unicos)))
        
        for i, supermercado in enumerate(supermercados_unicos):
            indices = [j for j, s in enumerate(supermercados) if s == supermercado]
            datas_sm = [datas[j] for j in indices]
            precos_sm = [precos[j] for j in indices]
            
            ax.plot(datas_sm, precos_sm, 'o-', label=supermercado, 
                   color=cores[i], linewidth=2, markersize=8)
        
        ax.set_xlabel('Data')
        ax.set_ylabel('Preço Unitário (R$)')
        ax.set_title(f'Evolução de Preços: {produto_nome}')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Rotacionar labels do eixo x
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Converter para imagem tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.graph_canvas)
        canvas.draw()
        canvas.get_tk_widget().pack(fill='both', expand=True)
    
    def fazer_backup_manual(self):
        """Faz backup manual do banco de dados"""
        backup_path = fazer_backup()
        if backup_path:
            messagebox.showinfo("✅ Backup", f"Backup criado com sucesso:\n{backup_path}")
        else:
            messagebox.showerror("❌ Erro", "Não foi possível criar o backup!")
    
    def mostrar_sobre(self):
        """Mostra informações sobre o aplicativo"""
        messagebox.showinfo("Sobre", 
            "Supermercado Price Tracker v2.0\n\n"
            "Aplicativo para acompanhamento de preços de supermercado.\n\n"
            "Funcionalidades:\n"
            "• Registro de compras com preços\n"
            "• Consulta e comparação de preços\n"
            "• Estatísticas e gráficos\n"
            "• Gerenciamento de produtos\n\n"
            "Desenvolvido com Python, Tkinter e SQLite")