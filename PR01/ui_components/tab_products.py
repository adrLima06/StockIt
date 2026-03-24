import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from database import get_db_connection
import pymysql

def create_products_tab(parent_frame):
    page_frame = ttk.Frame(parent_frame)
    ttk.Label(page_frame, text="Gestão de Produtos", font=("Calibri", 24, "bold")).pack(anchor="w", pady=(0, 20))

    main_pane = ttk.PanedWindow(page_frame, orient=HORIZONTAL)
    main_pane.pack(fill=BOTH, expand=YES)

    form_pane = ttk.Frame(main_pane)
    main_pane.add(form_pane, weight=1)
    form_card = ttk.LabelFrame(form_pane, text=" Detalhes do Produto ", padding=20)
    form_card.pack(fill=BOTH, expand=YES)

    ttk.Label(form_card, text="ID do Produto (código único):").pack(fill=X, pady=(0, 2), anchor='w')
    id_entry = ttk.Entry(form_card)
    id_entry.pack(fill=X, pady=(0, 10))
    ttk.Label(form_card, text="Nome do Produto:").pack(fill=X, pady=(0, 2), anchor='w')
    nome_entry = ttk.Entry(form_card)
    nome_entry.pack(fill=X, pady=(0, 10))
    ttk.Label(form_card, text="Marca:").pack(fill=X, pady=(0, 2), anchor='w')
    marca_entry = ttk.Entry(form_card)
    marca_entry.pack(fill=X, pady=(0, 20))
    
    table_pane = ttk.Frame(main_pane)
    main_pane.add(table_pane, weight=2)
    table_card = ttk.LabelFrame(table_pane, text=" Produtos Cadastrados ", padding=15)
    table_card.pack(fill=BOTH, expand=YES, padx=10)
    
    cols = ("id", "nome", "marca")
    tree = ttk.Treeview(table_card, columns=cols, show="headings", height=15)
    for col in cols: tree.heading(col, text=col.title())
    tree.column("id", width=100, anchor=CENTER)
    tree.pack(fill=BOTH, expand=YES)

    def clear_form(keep_id=False):
        if not keep_id: id_entry.delete(0, END)
        nome_entry.delete(0, END); marca_entry.delete(0, END); tree.selection_remove(tree.selection())
    def refresh_table():
        for item in tree.get_children(): tree.delete(item)
        conn = get_db_connection()
        if not conn: return
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("SELECT id, nome, marca FROM produtos_cadastrados ORDER BY nome ASC")
                for row in cursor.fetchall():
                    values = [str(row.get(col, '')) for col in cols]
                    tree.insert("", END, values=values)
        except Exception as e:
            messagebox.showerror("Erro de Banco de Dados", f"Não foi possível carregar os produtos: {e}")
        finally:
             if conn: conn.close()

    def on_product_select(event):
        if not tree.selection(): return
        item = tree.item(tree.selection()[0], "values")
        clear_form(); id_entry.insert(0, item[0]); nome_entry.insert(0, item[1]); marca_entry.insert(0, item[2])

    def save_product():
        prod_id = id_entry.get().strip()
        prod_nome = nome_entry.get().strip()
        if not prod_id or not prod_nome:
            messagebox.showwarning("Campos Obrigatórios", "ID e Nome do Produto são obrigatórios.")
            return

        conn = get_db_connection()
        if not conn: return
        try:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO produtos_cadastrados (id, nome, marca) VALUES (%s, %s, %s)", (prod_id, prod_nome, marca_entry.get().strip()))
            conn.commit(); messagebox.showinfo("Sucesso", "Produto cadastrado!"); clear_form(); refresh_table()
        except Exception as e: conn.rollback(); messagebox.showerror("Erro", f"O ID do produto já existe?\n{e}")
        finally: conn.close()

    def update_product():
        prod_id = id_entry.get().strip()
        if not prod_id:
            messagebox.showwarning("Seleção Necessária", "Selecione um produto da lista ou insira um ID para atualizar.")
            return

        conn = get_db_connection()
        if not conn: return
        try:
            with conn.cursor() as cursor:
                cursor.execute("UPDATE produtos_cadastrados SET nome=%s, marca=%s WHERE id=%s", (nome_entry.get().strip(), marca_entry.get().strip(), prod_id))
                if cursor.rowcount == 0:
                    messagebox.showwarning("Aviso", "Nenhum produto com este ID foi encontrado para atualizar.")
                else:
                    conn.commit(); messagebox.showinfo("Sucesso", "Produto atualizado!"); clear_form(); refresh_table()
        except Exception as e: conn.rollback(); messagebox.showerror("Erro", f"Falha ao atualizar: {e}")
        finally: conn.close()

    def delete_product():
        prod_id = id_entry.get().strip()
        if not prod_id:
            messagebox.showwarning("Seleção Necessária", "Selecione um produto da lista para deletar.")
            return
        if not messagebox.askyesno("Confirmar", f"Tem certeza que deseja deletar o produto ID {prod_id}?"): return
        
        conn = get_db_connection()
        if not conn: return
        try:
            with conn.cursor() as cursor: 
                cursor.execute("DELETE FROM produtos_cadastrados WHERE id = %s", (prod_id,))
                if cursor.rowcount == 0:
                    messagebox.showwarning("Aviso", "Nenhum produto com este ID foi encontrado para deletar.")
                else:
                    conn.commit(); messagebox.showinfo("Sucesso", "Produto deletado!"); clear_form(); refresh_table()
        except Exception as e: conn.rollback(); messagebox.showerror("Erro", f"Falha ao deletar: {e}")
        finally: conn.close()

    action_frame = ttk.Frame(form_card)
    action_frame.pack(fill=X, pady=(20, 0), side=BOTTOM)
    action_frame.columnconfigure((0, 1), weight=1)

    ttk.Button(action_frame, text="💾 Salvar", command=save_product, bootstyle="Warm").grid(row=0, column=0, sticky="ew", padx=(0, 5), pady=2)
    ttk.Button(action_frame, text="🔄 Atualizar por ID", command=update_product, bootstyle="Primary").grid(row=0, column=1, sticky="ew", padx=(5, 0), pady=2)
    ttk.Button(action_frame, text="🗑️ Deletar por ID", command=delete_product, bootstyle="DANGER").grid(row=1, column=0, sticky="ew", padx=(0, 5), pady=2)
    ttk.Button(action_frame, text="✨ Limpar", command=lambda: clear_form(False), bootstyle="Outline").grid(row=1, column=1, sticky="ew", padx=(5, 0), pady=2)

    tree.bind("<<TreeviewSelect>>", on_product_select)
    refresh_table()
    return page_frame