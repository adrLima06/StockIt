import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
import webbrowser
from database import get_db_connection
import pymysql
from datetime import datetime
from database import get_db_connection, obter_grupos_cadastrados

def create_leads_tab(parent_frame):
    page_frame = ttk.Frame(parent_frame)
    ttk.Label(page_frame, text="Gestão de Leads", font=("Calibri", 24, "bold")).pack(anchor="w", pady=(0, 20))
    main_pane = ttk.PanedWindow(page_frame, orient=HORIZONTAL)
    main_pane.pack(fill=BOTH, expand=YES)
    form_pane = ttk.Frame(main_pane)
    main_pane.add(form_pane, weight=1)
    form_card = ttk.LabelFrame(form_pane, text=" Informações do Lead ", padding=20)
    form_card.pack(fill=BOTH, expand=YES)
    grupos_dinamicos = obter_grupos_cadastrados()
    entries = {}
    
    ttk.Label(form_card, text="Nome:").pack(fill=X, pady=(0, 2), anchor='w')
    entries['nome'] = ttk.Entry(form_card)
    entries['nome'].pack(fill=X, pady=(0, 10))

    ttk.Label(form_card, text="Telefone:").pack(fill=X, pady=(0, 2), anchor='w')
    entries['telefone'] = ttk.Entry(form_card)
    entries['telefone'].pack(fill=X, pady=(0, 10))

    # Trecho modificado na função create_leads_tab:
    ttk.Label(form_card, text="Grupo de Interesse:").pack(fill=X, pady=(0, 2), anchor='w')
    # Removido state="readonly"
    entries['grupo'] = ttk.Combobox(form_card, values=["AQUECEDORES", "AQUEC SOLAR", "ENERGIA SOLAR", "OUTROS", "CURSOS"])
    entries['grupo'].pack(fill=X, pady=(0, 10))
    entries['grupo'].set("OUTROS")

    ttk.Label(form_card, text="Data de Cadastro (DD/MM/AAAA):").pack(fill=X, pady=(0, 2), anchor='w')
    entries['data_cadastro'] = ttk.Entry(form_card)
    entries['data_cadastro'].pack(fill=X, pady=(0, 20))
    

    table_pane = ttk.Frame(main_pane)
    main_pane.add(table_pane, weight=2)
    table_card = ttk.LabelFrame(table_pane, text=" Leads Cadastrados ", padding=15)
    table_card.pack(fill=BOTH, expand=YES, padx=10)

    cols = ("id", "nome", "telefone", "grupo", "data_cadastro")
    tree = ttk.Treeview(table_card, columns=cols, show="headings", height=15)
    for col in cols: tree.heading(col, text=col.replace("_", " ").title())
    tree.column("id", width=50, anchor=CENTER); tree.column("nome", width=200); tree.column("data_cadastro", anchor=CENTER)
    tree.pack(fill=BOTH, expand=YES)
    
    def setup_placeholder(entry, text):
        entry.insert(0, text)
        entry.config(bootstyle="secondary")
        def on_focus_in(event):
            if entry.get() == text:
                entry.delete(0, "end")
                entry.config(bootstyle="primary")
        def on_focus_out(event):
            if not entry.get():
                entry.config(bootstyle="secondary")
                entry.insert(0, text)
        entry.bind("<FocusIn>", on_focus_in)
        entry.bind("<FocusOut>", on_focus_out)
        
    setup_placeholder(entries['telefone'], "Ex: 5554999998888")

    def formatar_data_entry(event):
        entry = event.widget
        numeros = ''.join(filter(str.isdigit, entry.get()))[:8]
        novo_texto = f"{numeros[:2]}/{numeros[2:4]}/{numeros[4:]}" if len(numeros) > 4 else f"{numeros[:2]}/{numeros[2:]}" if len(numeros) > 2 else numeros
        entry.delete(0, END); entry.insert(0, novo_texto); entry.icursor(END)
    entries['data_cadastro'].bind("<KeyRelease>", formatar_data_entry)

    selected_id = None
    
    def clear_form():
        nonlocal selected_id
        selected_id = None
        for key, widget in entries.items():
            if isinstance(widget, ttk.Combobox): widget.set('')
            else: widget.delete(0, END)
        entries['grupo'].set("OUTROS")
        tree.selection_remove(tree.selection())
        setup_placeholder(entries['telefone'], "Ex: 5554999998888")

    def refresh_table():
        for item in tree.get_children(): tree.delete(item)
        conn = get_db_connection()
        if not conn: return
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("SELECT id, nome, telefone, grupo, DATE_FORMAT(data_cadastro, '%d/%m/%Y') AS data_cadastro FROM leads ORDER BY id DESC")
                for row in cursor.fetchall(): tree.insert("", END, values=list(row.values()))
        finally: conn.close()

    def on_lead_select(event):
        nonlocal selected_id
        if not tree.selection(): return
        
        item_values = tree.item(tree.selection()[0], "values")
        selected_id = item_values[0]
        
        clear_form()
        selected_id = item_values[0] 

        entries['nome'].insert(0, item_values[1])
        if entries['telefone'].get() == "Ex: 5554999998888": entries['telefone'].delete(0, END); entries['telefone'].config(bootstyle="primary")
        entries['telefone'].insert(0, item_values[2])
        entries['grupo'].set(item_values[3])
        entries['data_cadastro'].insert(0, item_values[4])


    def formatar_telefone(telefone_str):
        if telefone_str == "Ex: 5554999998888": return ""
        numeros = ''.join(filter(str.isdigit, telefone_str))
        return '55' + numeros if numeros and not numeros.startswith('55') else numeros

    def save_lead():
        nome = entries['nome'].get().strip()
        telefone = formatar_telefone(entries['telefone'].get())
        data_str = entries['data_cadastro'].get().strip()
        
        if not nome or not telefone:
            messagebox.showwarning("Campos Obrigatórios", "Nome e Telefone são obrigatórios.")
            return

        conn = get_db_connection()
        if not conn: return
        try:
            with conn.cursor() as cursor:
                if data_str:
                    data_cadastro = datetime.strptime(data_str, '%d/%m/%Y').strftime('%Y-%m-%d')
                    query = "INSERT INTO leads (nome, telefone, grupo, data_cadastro) VALUES (%s, %s, %s, %s)"
                    params = (nome, telefone, entries['grupo'].get(), data_cadastro)
                else:
                    query = "INSERT INTO leads (nome, telefone, grupo, data_cadastro) VALUES (%s, %s, %s, CURDATE())"
                    params = (nome, telefone, entries['grupo'].get())
                
                cursor.execute(query, params)
            conn.commit()
            messagebox.showinfo("Sucesso", "Lead cadastrado!")
            clear_form()
            refresh_table()
        except ValueError:
            messagebox.showwarning("Formato Inválido", "A data deve estar no formato DD/MM/AAAA.")
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Erro", f"Falha ao cadastrar: {e}")
        finally:
            conn.close()

    def update_lead():
        nonlocal selected_id
        if not selected_id:
            messagebox.showwarning("Aviso", "Selecione um lead para atualizar.")
            return

        nome = entries['nome'].get().strip()
        telefone = formatar_telefone(entries['telefone'].get())
        data_str = entries['data_cadastro'].get().strip()

        if not nome or not telefone or not data_str:
            messagebox.showwarning("Campos Obrigatórios", "Nome, Telefone e Data são obrigatórios para atualizar.")
            return
            
        try:
            data_cadastro = datetime.strptime(data_str, '%d/%m/%Y').strftime('%Y-%m-%d')
        except ValueError:
            messagebox.showwarning("Formato Inválido", "A data deve estar no formato DD/MM/AAAA.")
            return

        conn = get_db_connection()
        if not conn: return
        try:
            with conn.cursor() as cursor:
                cursor.execute("UPDATE leads SET nome = %s, telefone = %s, grupo = %s, data_cadastro = %s WHERE id = %s", 
                               (nome, telefone, entries['grupo'].get(), data_cadastro, selected_id))
            conn.commit()
            messagebox.showinfo("Sucesso", "Lead atualizado!")
            clear_form()
            refresh_table()
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Erro", f"Falha ao atualizar: {e}")
        finally:
            conn.close()

    def delete_lead():
        nonlocal selected_id
        if not selected_id:
            messagebox.showwarning("Aviso", "Selecione um lead para deletar.")
            return
        if not messagebox.askyesno("Confirmar", "Tem certeza que deseja deletar o lead selecionado?"):
            return
        
        conn = get_db_connection()
        if not conn: return
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM leads WHERE id = %s", (selected_id,))
            conn.commit()
            messagebox.showinfo("Sucesso", "Lead deletado!")
            clear_form()
            refresh_table()
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Erro", f"Falha ao deletar: {e}")
        finally:
            conn.close()
    
    def open_whatsapp():
        if not tree.selection():
            messagebox.showwarning("Aviso", "Selecione um lead para contatar.")
            return
        telefone_contato = tree.item(tree.selection()[0], 'values')[2]
        webbrowser.open(f"https://wa.me/{telefone_contato}")

    action_frame = ttk.Frame(form_card)
    action_frame.pack(fill=X, pady=(20, 0), side=BOTTOM)
    action_frame.columnconfigure((0, 1), weight=1)
    
    ttk.Button(action_frame, text="💾 Salvar Novo", command=save_lead, bootstyle="Warm").grid(row=0, column=0, sticky="ew", padx=(0, 5), pady=2)
    ttk.Button(action_frame, text="🔄 Atualizar Selecionado", command=update_lead, bootstyle="Primary").grid(row=0, column=1, sticky="ew", padx=(5, 0), pady=2)
    ttk.Button(action_frame, text="🗑️ Deletar", command=delete_lead, bootstyle="DANGER").grid(row=1, column=0, sticky="ew", padx=(0, 5), pady=2)
    ttk.Button(action_frame, text="✨ Limpar Formulário", command=clear_form, bootstyle="Outline").grid(row=1, column=1, sticky="ew", padx=(5, 0), pady=2)
    ttk.Button(action_frame, text="💬 Abrir WhatsApp", command=open_whatsapp, bootstyle="Success-Outline").grid(row=2, column=0, columnspan=2, sticky="ew", pady=(15, 0))
    
    tree.bind("<<TreeviewSelect>>", on_lead_select)
    refresh_table()
    return page_frame