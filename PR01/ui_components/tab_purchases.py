import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from database import get_db_connection, remover_lead_por_telefone # Importada a nova função
from datetime import datetime, date
import pymysql

def create_purchases_tab(parent_frame):
    page_frame = ttk.Frame(parent_frame)
    
    # --- CABEÇALHO ---
    header_frame = ttk.Frame(page_frame)
    header_frame.pack(fill=X, pady=(0, 20))
    ttk.Label(header_frame, text="Gestão de Compras", font=("Calibri", 24, "bold"), bootstyle="inverse-secondary").pack(side=LEFT)
    ttk.Label(header_frame, text="Histórico de vendas e pós-venda", font=("Calibri", 12), bootstyle="secondary").pack(side=LEFT, padx=15)

    main_pane = ttk.PanedWindow(page_frame, orient=HORIZONTAL)
    main_pane.pack(fill=BOTH, expand=YES)

    # --- LADO ESQUERDO: FORMULÁRIO ---
    form_pane = ttk.Frame(main_pane)
    main_pane.add(form_pane, weight=2)

    form_card = ttk.LabelFrame(form_pane, text=" Detalhes da Venda ", padding=15, bootstyle="info")
    form_card.pack(fill=BOTH, expand=YES, padx=(0, 10))
    
    form_canvas = ttk.Canvas(form_card, highlightthickness=0)
    scrollbar = ttk.Scrollbar(form_card, orient="vertical", command=form_canvas.yview)
    scrollable_frame = ttk.Frame(form_canvas)
    scrollable_frame.bind("<Configure>", lambda e: form_canvas.configure(scrollregion=form_canvas.bbox("all")))
    form_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    form_canvas.configure(yscrollcommand=scrollbar.set)
    form_canvas.pack(side=LEFT, fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    entries = {}
    campos = [("Nome do Comprador", "nome"), ("CPF/CNPJ", "cpfcnpj"), ("Endereço", "endereco"), ("CEP", "cep"), ("Bairro", "bairro"), ("Telefone/Whats", "telefone"), ("Grupo/Categoria", "grupo"), ("NFe", "nfe"), ("ID Produtos", "id_produtos"), ("Data da Compra", "data_compra"), ("Valor Total (R$)", "preco"), ("Forma Pagamento", "forma_pagamento")]
    
    for i, (label_text, key) in enumerate(campos):
        ttk.Label(scrollable_frame, text=label_text, font=("Calibri", 10, "bold")).grid(row=i, column=0, sticky='w', pady=(8, 2))
        if key == "grupo": 
            # Removido state="readonly" para permitir digitação de novos grupos
            entries[key] = ttk.Combobox(scrollable_frame, values=["AQUECEDORES", "AQUEC SOLAR", "ENERGIA SOLAR", "CURSOS", "OUTROS"])
        elif key == "forma_pagamento": 
            entries[key] = ttk.Combobox(scrollable_frame, values=["À Vista", "Parcelado", "Financiamento", "Cartão"], state="readonly")
        else: 
            entries[key] = ttk.Entry(scrollable_frame)
        entries[key].grid(row=i, column=1, sticky='ew', pady=(0, 8), padx=(10,0))
    scrollable_frame.columnconfigure(1, weight=1)

    def formatar_data_entry(event):
        entry = event.widget
        if not entry.get(): return
        numeros = ''.join(filter(str.isdigit, entry.get()))[:8]
        novo_texto = numeros
        if len(numeros) >= 2: novo_texto = f"{numeros[:2]}/{numeros[2:]}"
        if len(numeros) >= 4: novo_texto = f"{numeros[:2]}/{numeros[2:4]}/{numeros[4:]}"
        if entry.get() != novo_texto: entry.delete(0, END); entry.insert(0, novo_texto); entry.icursor(END)
    entries['data_compra'].bind("<KeyRelease>", formatar_data_entry)

    action_frame = ttk.Frame(scrollable_frame)
    action_frame.grid(row=len(campos) + 1, column=0, columnspan=2, pady=(20, 10), sticky='ew')
    action_frame.columnconfigure((0, 1), weight=1)

    ttk.Button(action_frame, text="💾 Registrar", bootstyle="success", command=lambda: save_purchase()).grid(row=0, column=0, sticky='ew', padx=(0,5), pady=(0, 5))
    ttk.Button(action_frame, text="🔄 Atualizar", bootstyle="info", command=lambda: update_purchase()).grid(row=0, column=1, sticky='ew', padx=(5,0), pady=(0, 5))
    ttk.Button(action_frame, text="🗑️ Remover", bootstyle="danger-outline", command=lambda: delete_purchase()).grid(row=1, column=0, sticky='ew', padx=(0,5), pady=5)
    ttk.Button(action_frame, text="✨ Limpar", bootstyle="secondary-outline", command=lambda: clear_form()).grid(row=1, column=1, sticky='ew', padx=(5,0), pady=5)
    
    table_pane = ttk.Frame(main_pane)
    main_pane.add(table_pane, weight=3)
    
    search_card = ttk.LabelFrame(table_pane, text=" Filtros ", padding=10)
    search_card.pack(fill=X, pady=(0, 15))
    search_card.columnconfigure((0, 1), weight=1); search_card.columnconfigure(2, weight=0)
    
    search_nome_entry = ttk.Entry(search_card); search_nome_entry.grid(row=0, column=0, sticky='ew', padx=(0,5))
    search_nfe_entry = ttk.Entry(search_card); search_nfe_entry.grid(row=0, column=1, sticky='ew', padx=5)
    ttk.Button(search_card, text="Buscar", bootstyle="primary", width=10, command=lambda: perform_search()).grid(row=0, column=2, padx=5)
    
    table_card = ttk.LabelFrame(table_pane, text=" Histórico ", padding=10)
    table_card.pack(fill=BOTH, expand=YES)
    
    cols = ("id", "nome", "telefone", "grupo", "nfe", "data_compra")
    tree = ttk.Treeview(table_card, columns=cols, show="headings", height=15, bootstyle="info")
    for col in cols: tree.heading(col, text=col.upper())
    tree.column("id", width=40, anchor=CENTER); tree.column("nome", width=200); tree.column("data_compra", width=100, anchor=CENTER)
    tree.pack(fill=BOTH, expand=YES)
    
    selected_id = None
    
    def clear_form():
        nonlocal selected_id; selected_id = None
        for widget in entries.values(): 
            if isinstance(widget, ttk.Entry): widget.delete(0, END)
            else: widget.set('')
        try: tree.selection_remove(tree.selection())
        except: pass

    def refresh_table(query=None, params=None):
        for item in tree.get_children(): tree.delete(item)
        final_query = query or f"SELECT {', '.join(cols)} FROM compras_detalhadas ORDER BY data_compra DESC"
        conn = get_db_connection()
        if not conn: return
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(final_query, params)
                for row in cursor.fetchall():
                    values = []
                    for col in cols:
                        val = row.get(col)
                        if val is None: values.append('')
                        elif isinstance(val, (datetime, date)): values.append(val.strftime('%d/%m/%Y'))
                        else: values.append(str(val))
                    tree.insert("", END, values=values)
        finally: conn.close()

    def on_purchase_select(event):
        nonlocal selected_id
        if not tree.selection(): return
        try: selected_id = tree.item(tree.selection()[0], "values")[0]
        except: return
        conn = get_db_connection()
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("SELECT * FROM compras_detalhadas WHERE id = %s", (selected_id,))
                data = cursor.fetchone()
                if not data: return
                for key, widget in entries.items():
                    val = data.get(key)
                    if key=='data_compra' and isinstance(val, (date, datetime)): val = val.strftime('%d/%m/%Y')
                    if val is None: val = ''
                    if isinstance(widget, ttk.Entry): widget.delete(0, END); widget.insert(0, str(val))
                    else: widget.set(str(val))
        finally: conn.close()
    
    def get_data_from_form():
        data = {key: widget.get().strip() for key, widget in entries.items()}
        if not data['nome']: messagebox.showwarning("Aviso", "Nome Obrigatório"); return None
        try: data['data_compra'] = datetime.strptime(data['data_compra'], '%d/%m/%Y').strftime('%Y-%m-%d')
        except: messagebox.showwarning("Erro", "Data inválida"); return None
        try: p = data['preco'].replace(',', '.'); data['preco'] = float(p) if p else 0.0
        except: data['preco'] = 0.0
        return data

    def save_purchase():
        d = get_data_from_form()
        if not d: return
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO compras_detalhadas (nome, cpfcnpj, endereco, cep, bairro, telefone, grupo, nfe, id_produtos, data_compra, preco, forma_pagamento) VALUES (%(nome)s, %(cpfcnpj)s, %(endereco)s, %(cep)s, %(bairro)s, %(telefone)s, %(grupo)s, %(nfe)s, %(id_produtos)s, %(data_compra)s, %(preco)s, %(forma_pagamento)s)", d)
            conn.commit()
            
            # LÓGICA DE LIMPEZA DE LEADS: Se comprou, não é mais apenas um Lead
            try:
                remover_lead_por_telefone(d['telefone'])
            except Exception as e:
                print(f"Aviso: Não foi possível remover lead: {e}")
                
            messagebox.showinfo("Sucesso", "Registrado com sucesso e lead removido (se existia)!")
            clear_form(); refresh_table()
        except Exception as e: messagebox.showerror("Erro", str(e))
        finally: conn.close()

    def update_purchase():
        if not selected_id: return
        d = get_data_from_form(); d['id'] = selected_id
        if not d: return
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("UPDATE compras_detalhadas SET nome=%(nome)s, cpfcnpj=%(cpfcnpj)s, endereco=%(endereco)s, cep=%(cep)s, bairro=%(bairro)s, telefone=%(telefone)s, grupo=%(grupo)s, nfe=%(nfe)s, id_produtos=%(id_produtos)s, data_compra=%(data_compra)s, preco=%(preco)s, forma_pagamento=%(forma_pagamento)s WHERE id=%(id)s", d)
            conn.commit(); messagebox.showinfo("Sucesso", "Atualizado!"); clear_form(); refresh_table()
        except Exception as e: messagebox.showerror("Erro", str(e))
        finally: conn.close()

    def delete_purchase():
        if not selected_id or not messagebox.askyesno("Confirmar", "Deletar?"): return
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor: cursor.execute("DELETE FROM compras_detalhadas WHERE id=%s", (selected_id,))
            conn.commit(); clear_form(); refresh_table()
        finally: conn.close()
    
    def perform_search():
        n, nf = search_nome_entry.get().strip(), search_nfe_entry.get().strip()
        q, p = f"SELECT {', '.join(cols)} FROM compras_detalhadas WHERE 1=1", []
        if n: q += " AND nome LIKE %s"; p.append(f"%{n}%")
        if nf: q += " AND nfe LIKE %s"; p.append(f"%{nf}%")
        refresh_table(q + " ORDER BY data_compra DESC", tuple(p))
    
    tree.bind("<<TreeviewSelect>>", on_purchase_select)
    refresh_table() 
    return page_frame