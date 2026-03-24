import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import pymysql
from database import get_db_connection
from collections import Counter
from datetime import datetime
from tkinter import messagebox

def create_reports_tab(parent_frame):
    page_frame = ttk.Frame(parent_frame)
    
    header_frame = ttk.Frame(page_frame)
    header_frame.pack(fill=X, pady=(0, 20), anchor="w")
    
    ttk.Label(header_frame, text="Relatório de Vendas por Produto", font=("Calibri", 24, "bold")).pack(side=LEFT, anchor="w")
    
    filter_frame = ttk.Frame(header_frame)
    filter_frame.pack(side=RIGHT)
    
    ttk.Label(filter_frame, text="Filtrar por Mês/Ano:").pack(side=LEFT, padx=(10, 5))
    
    mes_var = ttk.StringVar(value=datetime.now().strftime("%m"))
    ano_var = ttk.StringVar(value=datetime.now().strftime("%Y"))
    
    mes_combo = ttk.Combobox(filter_frame, textvariable=mes_var, values=[f"{i:02d}" for i in range(1, 13)], width=5, state="readonly")
    mes_combo.pack(side=LEFT)
    ano_combo = ttk.Combobox(filter_frame, textvariable=ano_var, values=[str(i) for i in range(2022, 2031)], width=7, state="readonly")
    ano_combo.pack(side=LEFT, padx=5)
    
    table_card = ttk.LabelFrame(page_frame, text=" Vendas no Período Selecionado ", padding=15)
    table_card.pack(fill=BOTH, expand=YES)
    
    cols = ("id_produto", "nome_produto", "vendas_total")
    tree = ttk.Treeview(table_card, columns=cols, show="headings", height=15)
    tree.heading("id_produto", text="ID do Produto")
    tree.heading("nome_produto", text="Nome do Produto")
    tree.heading("vendas_total", text="Quantidade Vendida")
    tree.column("id_produto", width=120, anchor=CENTER)
    tree.column("vendas_total", width=150, anchor=CENTER)
    tree.pack(fill=BOTH, expand=YES)

    def carregar_relatorio():
        for item in tree.get_children():
            tree.delete(item)

        conn = get_db_connection()
        if not conn: return

        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("SELECT id, nome FROM produtos_cadastrados")
                produtos_map = {str(row['id']).strip(): row['nome'] for row in cursor.fetchall()}
                mes = mes_var.get()
                ano = ano_var.get()
                query_compras = "SELECT id_produtos FROM compras_detalhadas WHERE MONTH(data_compra) = %s AND YEAR(data_compra) = %s"
                cursor.execute(query_compras, (mes, ano))
                compras = cursor.fetchall()
                
                if not compras:
                    messagebox.showinfo("Sem Dados", f"Nenhuma venda encontrada para {mes}/{ano}.", parent=page_frame)
                    return

                todos_ids_vendidos = []
                for compra in compras:
                    if compra['id_produtos']:
                        ids = [pid.strip() for pid in str(compra['id_produtos']).split(',') if pid.strip()]
                        todos_ids_vendidos.extend(ids)
                
                contagem_vendas = Counter(todos_ids_vendidos)
                if not contagem_vendas:
                    messagebox.showinfo("Sem Dados", f"Vendas encontradas para {mes}/{ano}, mas sem IDs de produto associados.", parent=page_frame)
                    return
                for produto_id, quantidade in sorted(contagem_vendas.items(), key=lambda item: item[1], reverse=True):
                    nome_produto = produtos_map.get(produto_id, f"Produto Desconhecido (ID: {produto_id})")
                    tree.insert("", END, values=(produto_id, nome_produto, quantidade))
        
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar relatório: {e}", parent=page_frame)
        finally:
            if conn:
                conn.close()

    refresh_button = ttk.Button(filter_frame, text="🔎 Gerar Relatório", command=carregar_relatorio, bootstyle="Outline")
    refresh_button.pack(side=LEFT, padx=5)
    
    def on_tab_show():
        pass

    page_frame.refresh_data = on_tab_show
    return page_frame