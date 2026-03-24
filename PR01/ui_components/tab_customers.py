import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from database import get_db_connection
from datetime import datetime, date
import pymysql

def create_customers_tab(parent_frame):
    page_frame = ttk.Frame(parent_frame)
    
    # Cabeçalho
    header = ttk.Frame(page_frame)
    header.pack(fill=X, pady=(0, 20))
    ttk.Label(header, text="Cadastro de Clientes", font=("Calibri", 24, "bold"), bootstyle="inverse-primary").pack(side=LEFT)
    ttk.Label(header, text="Base de dados para relacionamento", font=("Calibri", 12)).pack(side=LEFT, padx=20)

    # Layout Principal
    main_split = ttk.PanedWindow(page_frame, orient=HORIZONTAL)
    main_split.pack(fill=BOTH, expand=YES)

    # --- LADO ESQUERDO: FORMULÁRIO ---
    left_panel = ttk.Frame(main_split)
    main_split.add(left_panel, weight=1)

    form_frame = ttk.LabelFrame(left_panel, text=" Dados do Cliente ", padding=20, bootstyle="primary")
    form_frame.pack(fill=BOTH, expand=YES, padx=(0, 10))

    entries = {}
    
    def create_field(parent, label, key, row):
        ttk.Label(parent, text=label, font=("Calibri", 11)).grid(row=row, column=0, sticky='w', pady=(10, 2))
        entry = ttk.Entry(parent)
        entry.grid(row=row, column=1, sticky='ew', pady=(0, 5), padx=(10, 0))
        entries[key] = entry
        return entry

    create_field(form_frame, "Nome Completo:", "nome", 0)
    create_field(form_frame, "E-mail:", "email", 1)
    create_field(form_frame, "CPF:", "cpf", 2)
    create_field(form_frame, "WhatsApp (apenas números):", "whatsapp", 3)
    
    # Campo Grupo (NOVO)
    ttk.Label(form_frame, text="Grupo / Categoria:", font=("Calibri", 11)).grid(row=4, column=0, sticky='w', pady=(10, 2))
    entries['grupo'] = ttk.Combobox(form_frame, values=["CLIENTES", "AQUECEDORES", "AQUEC SOLAR", "ENERGIA SOLAR", "CURSOS", "OUTROS"])
    entries['grupo'].grid(row=4, column=1, sticky='ew', pady=(0, 5), padx=(10, 0))
    entries['grupo'].set("CLIENTES") # Padrão

    # Campo Data Nascimento
    ttk.Label(form_frame, text="Data de Nascimento (DD/MM/AAAA):", font=("Calibri", 11)).grid(row=5, column=0, sticky='w', pady=(10, 2))
    entries['data_nascimento'] = ttk.Entry(form_frame)
    entries['data_nascimento'].grid(row=5, column=1, sticky='ew', pady=(0, 5), padx=(10, 0))

    def format_date(event):
        e = event.widget
        if not e.get(): return
        txt = ''.join(filter(str.isdigit, e.get()))[:8]
        fmt = txt
        if len(txt) >= 2: fmt = f"{txt[:2]}/{txt[2:]}"
        if len(txt) >= 4: fmt = f"{txt[:2]}/{txt[2:4]}/{txt[4:]}"
        if e.get() != fmt: e.delete(0, END); e.insert(0, fmt); e.icursor(END)
    entries['data_nascimento'].bind('<KeyRelease>', format_date)

    ttk.Label(form_frame, text="NFes Vinculadas:", font=("Calibri", 11)).grid(row=6, column=0, sticky='w', pady=(10, 2))
    entries['nfes'] = ttk.Entry(form_frame)
    entries['nfes'].grid(row=6, column=1, sticky='ew', pady=(0, 5), padx=(10, 0))

    form_frame.columnconfigure(1, weight=1)

    # Botões
    btn_frame = ttk.Frame(form_frame)
    btn_frame.grid(row=7, column=0, columnspan=2, pady=30, sticky='ew')
    btn_frame.columnconfigure((0, 1), weight=1)

    ttk.Button(btn_frame, text="Cadastrar Cliente", bootstyle="success", command=lambda: save_customer()).grid(row=0, column=0, sticky='ew', padx=5)
    ttk.Button(btn_frame, text="Salvar Alterações", bootstyle="warning", command=lambda: update_customer()).grid(row=0, column=1, sticky='ew', padx=5)
    ttk.Button(btn_frame, text="Limpar / Novo", bootstyle="secondary-outline", command=lambda: clear_form()).grid(row=1, column=0, columnspan=2, sticky='ew', padx=5, pady=10)

    # --- LADO DIREITO: TABELA ---
    right_panel = ttk.Frame(main_split)
    main_split.add(right_panel, weight=2)

    list_frame = ttk.LabelFrame(right_panel, text=" Lista de Clientes ", padding=10)
    list_frame.pack(fill=BOTH, expand=YES)

    cols = ("id", "nome", "whatsapp", "grupo", "data_nascimento")
    tree = ttk.Treeview(list_frame, columns=cols, show="headings", height=20, bootstyle="primary")
    
    tree.heading("id", text="ID"); tree.column("id", width=30, anchor=CENTER)
    tree.heading("nome", text="Nome"); tree.column("nome", width=180)
    tree.heading("whatsapp", text="WhatsApp"); tree.column("whatsapp", width=100)
    tree.heading("grupo", text="Grupo"); tree.column("grupo", width=100)
    tree.heading("data_nascimento", text="Nascimento"); tree.column("data_nascimento", width=90, anchor=CENTER)
    
    tree.pack(fill=BOTH, expand=YES)

    selected_id = None

    def refresh_list():
        for i in tree.get_children(): tree.delete(i)
        conn = get_db_connection()
        if not conn: return
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, nome, whatsapp, grupo, data_nascimento FROM clientes ORDER BY nome ASC")
                for row in cursor.fetchall():
                    dt = row[4]
                    dt_str = ""
                    if isinstance(dt, (datetime, date)): dt_str = dt.strftime("%d/%m/%Y")
                    elif isinstance(dt, str): 
                        try: dt_str = datetime.strptime(dt, "%Y-%m-%d").strftime("%d/%m/%Y")
                        except: dt_str = dt
                    tree.insert("", END, values=(row[0], row[1], row[2], row[3], dt_str))
        except: pass
        finally: conn.close()

    def get_form_data():
        data = {k: v.get().strip() for k, v in entries.items()}
        if not data['nome']: messagebox.showwarning("Aviso", "Nome Obrigatório"); return None
        if data['data_nascimento']:
            try: dt = datetime.strptime(data['data_nascimento'], "%d/%m/%Y"); data['data_nascimento'] = dt.strftime("%Y-%m-%d")
            except: messagebox.showerror("Erro", "Data inválida"); return None
        else: data['data_nascimento'] = None
        if data['whatsapp']:
            nums = ''.join(filter(str.isdigit, data['whatsapp']))
            if not nums.startswith('55') and len(nums) >= 10: nums = '55' + nums
            data['whatsapp'] = nums
        return data

    def save_customer():
        d = get_form_data()
        if not d: return
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO clientes (nome, email, cpf, whatsapp, grupo, data_nascimento, nfes_vinculadas, data_cadastro) VALUES (%s, %s, %s, %s, %s, %s, %s, CURDATE())", 
                               (d['nome'], d['email'], d['cpf'], d['whatsapp'], d['grupo'], d['data_nascimento'], d['nfes']))
            conn.commit(); messagebox.showinfo("Sucesso", "Cadastrado!"); clear_form(); refresh_list()
        except Exception as e: messagebox.showerror("Erro", str(e))
        finally: conn.close()

    def update_customer():
        if not selected_id: return
        d = get_form_data()
        if not d: return
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("UPDATE clientes SET nome=%s, email=%s, cpf=%s, whatsapp=%s, grupo=%s, data_nascimento=%s, nfes_vinculadas=%s WHERE id=%s", 
                               (d['nome'], d['email'], d['cpf'], d['whatsapp'], d['grupo'], d['data_nascimento'], d['nfes'], selected_id))
            conn.commit(); messagebox.showinfo("Sucesso", "Atualizado!"); clear_form(); refresh_list()
        except Exception as e: messagebox.showerror("Erro", str(e))
        finally: conn.close()

    def on_select(event):
        nonlocal selected_id
        if not tree.selection(): return
        item = tree.item(tree.selection()[0], "values")
        selected_id = item[0]
        conn = get_db_connection()
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("SELECT * FROM clientes WHERE id=%s", (selected_id,))
                row = cursor.fetchone()
                if row:
                    entries['nome'].delete(0, END); entries['nome'].insert(0, row['nome'])
                    entries['email'].delete(0, END); entries['email'].insert(0, row['email'] or "")
                    entries['cpf'].delete(0, END); entries['cpf'].insert(0, row['cpf'] or "")
                    entries['whatsapp'].delete(0, END); entries['whatsapp'].insert(0, row['whatsapp'] or "")
                    entries['grupo'].set(row['grupo'] if row['grupo'] else "CLIENTES")
                    entries['nfes'].delete(0, END); entries['nfes'].insert(0, row['nfes_vinculadas'] or "")
                    if row['data_nascimento']:
                        if isinstance(row['data_nascimento'], str): 
                             try: dt_val = datetime.strptime(row['data_nascimento'], "%Y-%m-%d").strftime("%d/%m/%Y")
                             except: dt_val = row['data_nascimento']
                        elif isinstance(row['data_nascimento'], (date, datetime)): dt_val = row['data_nascimento'].strftime("%d/%m/%Y")
                        else: dt_val = ""
                        entries['data_nascimento'].delete(0, END); entries['data_nascimento'].insert(0, dt_val)
                    else: entries['data_nascimento'].delete(0, END)
        finally: conn.close()

    def clear_form():
        nonlocal selected_id; selected_id = None
        for e in entries.values(): 
            if hasattr(e, 'delete'): e.delete(0, END)
            elif hasattr(e, 'set'): e.set('CLIENTES')
        tree.selection_remove(tree.selection())

    tree.bind("<<TreeviewSelect>>", on_select)
    refresh_list()
    return page_frame