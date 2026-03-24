import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import messagebox
from database import get_db_connection
from datetime import datetime, date, timedelta
import pymysql
import os
import subprocess

def create_manual_sender_tab(parent):
    container = ttk.Frame(parent, padding=20)
    
    class ManualSenderApp:
        def __init__(self, master):
            self.master = master
            self.current_index = 0
            self.pendencias = []
            self.modo_broadcast = False
            
            self.setup_ui()
            self.load_data()
            
        def setup_ui(self):
            # --- HEADER ---
            self.header_frame = ttk.Frame(self.master)
            self.header_frame.pack(fill=X, pady=(0, 20))
            
            self.lbl_titulo = ttk.Label(self.header_frame, text="Envio Manual (Fila de Hoje)", font=("Segoe UI", 20, "bold"))
            self.lbl_titulo.pack(side=LEFT)
            
            self.btn_broadcast = ttk.Button(self.header_frame, text="📣 Modo Broadcast", bootstyle="warning", command=self.toggle_broadcast)
            self.btn_broadcast.pack(side=RIGHT, padx=(10, 0))

            self.btn_refresh = ttk.Button(self.header_frame, text="🔄 Recarregar", bootstyle="primary", command=self.load_data)
            self.btn_refresh.pack(side=RIGHT, padx=(10, 0))
            
            self.lbl_contador = ttk.Label(self.header_frame, text="Carregando...", font=("Segoe UI", 12), bootstyle="secondary")
            self.lbl_contador.pack(side=RIGHT, anchor=S, padx=10)

            # --- SELETOR DE SEGMENTAÇÃO (Exclusivo Modo Broadcast) ---
            self.broadcast_frame = ttk.Frame(self.master, padding=(50, 0))
            
            ttk.Label(self.broadcast_frame, text="Segmentação:", font=("Segoe UI", 10, "bold")).pack(side=LEFT, padx=(0, 10))
            self.combo_grupo = ttk.Combobox(self.broadcast_frame, state="readonly", width=45)
            self.combo_grupo.pack(side=LEFT, fill=X, expand=YES)
            self.combo_grupo.bind("<<ComboboxSelected>>", lambda e: self.load_broadcast_group())

            # --- CARD PRINCIPAL DE EXIBIÇÃO ---
            self.card = ttk.Frame(self.master, bootstyle="secondary", padding=2)
            self.card.pack(fill=BOTH, expand=YES, padx=50, pady=10)
            
            inner_card = ttk.Frame(self.card, padding=30)
            inner_card.pack(fill=BOTH, expand=YES)

            self.fields = {
                "Nome": ttk.StringVar(),
                "Telefone": ttk.StringVar(),
                "Regra": ttk.StringVar(),
                "Imagem": ttk.StringVar()
            }
            
            self.create_copy_field(inner_card, "Nome do Cliente:", self.fields["Nome"])
            self.create_copy_field(inner_card, "WhatsApp:", self.fields["Telefone"])
            self.create_copy_field(inner_card, "Segmento/Regra:", self.fields["Regra"])
            
            # Campo de Imagem com Cópia de Pixels
            img_row = ttk.Frame(inner_card)
            img_row.pack(fill=X, pady=5)
            ttk.Label(img_row, text="Anexo (Imagem):", width=20, font=("Segoe UI", 10, "bold")).pack(side=LEFT)
            
            entry_img = ttk.Entry(img_row, textvariable=self.fields["Imagem"], state="readonly", font=("Segoe UI", 11))
            entry_img.pack(side=LEFT, fill=X, expand=YES, padx=(0, 10))
            
            btn_copy_img = ttk.Button(img_row, text="🖼️ Copiar FOTO", bootstyle="outline-info", 
                                      command=lambda: self.copy_image_to_clipboard(self.fields["Imagem"].get()))
            btn_copy_img.pack(side=RIGHT)
            
            # Campo de Mensagem (Editável no Broadcast)
            ttk.Label(inner_card, text="Mensagem:", font=("Segoe UI", 10, "bold")).pack(anchor=W, pady=(15, 5))
            msg_frame = ttk.Frame(inner_card)
            msg_frame.pack(fill=BOTH, expand=YES)
            
            self.txt_mensagem = tk.Text(msg_frame, height=6, font=("Segoe UI", 11))
            self.txt_mensagem.pack(side=LEFT, fill=BOTH, expand=YES, padx=(0, 10))
            
            btn_copy_msg = ttk.Button(msg_frame, text="📋 Copiar Texto", bootstyle="outline-primary", 
                                      command=lambda: self.copy_to_clipboard(self.txt_mensagem.get("1.0", "end-1c")))
            btn_copy_msg.pack(side=RIGHT, anchor=N)

            # --- NAVEGAÇÃO E AÇÕES ---
            self.nav_frame = ttk.Frame(self.master)
            self.nav_frame.pack(fill=X, pady=20, padx=50)
            
            self.btn_prev = ttk.Button(self.nav_frame, text="⬅️ Anterior", bootstyle="secondary", command=self.prev_item)
            self.btn_prev.pack(side=LEFT)
            
            self.btn_mark_sent = ttk.Button(self.nav_frame, text="✅ Marcar como Enviado no BD", bootstyle="success", command=self.mark_as_sent)
            self.btn_mark_sent.pack(side=LEFT, expand=YES, padx=20)
            
            self.btn_next = ttk.Button(self.nav_frame, text="Próximo ➡️", bootstyle="primary", command=self.next_item)
            self.btn_next.pack(side=RIGHT)

        def create_copy_field(self, parent, label_text, text_var):
            row = ttk.Frame(parent)
            row.pack(fill=X, pady=5)
            ttk.Label(row, text=label_text, width=20, font=("Segoe UI", 10, "bold")).pack(side=LEFT)
            entry = ttk.Entry(row, textvariable=text_var, state="readonly", font=("Segoe UI", 11))
            entry.pack(side=LEFT, fill=X, expand=YES, padx=(0, 10))
            btn_copy = ttk.Button(row, text="📋 Copiar", bootstyle="outline-primary", command=lambda: self.copy_to_clipboard(text_var.get()))
            btn_copy.pack(side=RIGHT)

        def copy_to_clipboard(self, text):
            self.master.clipboard_clear()
            self.master.clipboard_append(text)

        def copy_image_to_clipboard(self, filepath):
            if not filepath or filepath == "Nenhuma" or not os.path.exists(filepath):
                messagebox.showwarning("Aviso", "Arquivo de imagem não encontrado ou inválido.")
                return
            caminho_seguro = filepath.replace("\\", "/")
            comando_ps = f'''
            Add-Type -AssemblyName System.Windows.Forms
            try {{
                $img = [System.Drawing.Image]::FromFile('{caminho_seguro}')
                [System.Windows.Forms.Clipboard]::SetImage($img)
                $img.Dispose()
            }} catch {{
                Write-Error "Erro ao copiar imagem"
            }}
            '''
            subprocess.run(["powershell", "-NoProfile", "-Command", comando_ps], creationflags=subprocess.CREATE_NO_WINDOW)

        def toggle_broadcast(self):
            self.modo_broadcast = not self.modo_broadcast
            if self.modo_broadcast:
                self.lbl_titulo.config(text="Broadcast (Envio Manual por Segmentação)")
                self.btn_broadcast.config(text="🔙 Voltar para Fila", bootstyle="secondary")
                self.btn_refresh.pack_forget()
                self.broadcast_frame.pack(fill=X, pady=(0, 10), after=self.header_frame)
                self.btn_mark_sent.config(text="✅ Próximo (Remover da Lista)")
                self.update_segment_list()
                self.pendencias = []
                self.update_display()
            else:
                self.lbl_titulo.config(text="Envio Manual (Fila de Hoje)")
                self.btn_broadcast.config(text="📣 Modo Broadcast", bootstyle="warning")
                self.btn_refresh.pack(side=RIGHT, padx=(10, 0))
                self.broadcast_frame.pack_forget()
                self.btn_mark_sent.config(text="✅ Marcar como Enviado no BD")
                self.load_data()

        def update_segment_list(self):
            conn = get_db_connection()
            if not conn: return
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT DISTINCT tipo_entidade, grupo FROM automacao_mensagens")
                    segments = [f"{row[0]} - {row[1]}" for row in cursor.fetchall()]
                    self.combo_grupo.config(values=segments)
            finally: conn.close()

        def load_broadcast_group(self):
            selection = self.combo_grupo.get()
            if not selection: return
            tipo, grupo = selection.split(" - ")
            
            conn = get_db_connection()
            if not conn: return
            self.pendencias = []
            msg_digitada = self.txt_mensagem.get("1.0", "end-1c")
            
            try:
                with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                    if tipo == 'LEAD':
                        cursor.execute("SELECT nome, telefone FROM leads WHERE grupo=%s", (grupo,))
                    elif tipo == 'COMPRA':
                        cursor.execute("SELECT nome, telefone FROM compras_detalhadas WHERE grupo=%s", (grupo,))
                    else:
                        cursor.execute("SELECT nome, whatsapp as telefone FROM clientes WHERE grupo=%s", (grupo,))
                    
                    for p in cursor.fetchall():
                        self.pendencias.append({
                            "nome": p.get('nome', ''),
                            "telefone": p.get('telefone', ''),
                            "regra": f"BROADCAST: {selection}",
                            "mensagem": msg_digitada,
                            "imagem": "Nenhuma"
                        })
            except Exception as e:
                print(f"Erro ao carregar grupo broadcast: {e}")
            finally: conn.close()
            self.current_index = 0
            self.update_display()

        def calcular_data_alvo(self, data_base, dias_apos, eh_niver=False):
            if not data_base: return None
            hoje = datetime.now().date()
            if eh_niver:
                try: dt_alvo = date(hoje.year, data_base.month, data_base.day)
                except: dt_alvo = date(hoje.year, 3, 1)
            else:
                if isinstance(data_base, str):
                    try: data_base = datetime.strptime(data_base, '%Y-%m-%d').date()
                    except: 
                        try: data_base = datetime.strptime(data_base, '%d/%m/%Y').date()
                        except: return None
                if isinstance(data_base, datetime): data_base = data_base.date()
                dt_alvo = data_base + timedelta(days=dias_apos)
            
            ds = dt_alvo.weekday()
            if ds == 5: dt_alvo += timedelta(days=2) 
            elif ds == 6: dt_alvo += timedelta(days=1) 
            return dt_alvo

        def load_data(self):
            if self.modo_broadcast: return
            self.pendencias = []
            conn = get_db_connection()
            if not conn: return
            
            hoje = datetime.now().date()
            limite = hoje - timedelta(days=5)
            
            try:
                with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                    cursor.execute("SELECT * FROM automacao_mensagens")
                    regras = cursor.fetchall()
                    
                    cursor.execute("SELECT id, nome, telefone, grupo, data_cadastro as dt FROM leads")
                    leads = cursor.fetchall()
                    cursor.execute("SELECT id, nome, telefone, grupo, data_compra as dt FROM compras_detalhadas")
                    compras = cursor.fetchall()
                    cursor.execute("SELECT id, nome, whatsapp as telefone, grupo, data_cadastro as dt, data_nascimento FROM clientes")
                    clientes = cursor.fetchall()

                    for r in regras:
                        tipo, grupo, dias, msg, img = r['tipo_entidade'], r['grupo'], r['dias_apos'], r['texto_mensagem'], r['caminho_imagem']
                        eh_niver = (tipo == 'ANIVERSARIO')
                        
                        if tipo == 'LEAD': lista = leads
                        elif tipo == 'COMPRA': lista = compras
                        else: lista = clientes

                        for p in [x for x in lista if x.get('grupo') == grupo]:
                            dt_ref = p.get('data_nascimento' if eh_niver else 'dt')
                            alvo = self.calcular_data_alvo(dt_ref, dias, eh_niver)
                            
                            if alvo and (limite <= alvo <= hoje):
                                key = int(f"{hoje.year}{dias}") if eh_niver else dias
                                cursor.execute("SELECT COUNT(*) as c FROM mensagens_enviadas WHERE entity_id=%s AND entity_type=%s AND dias_key=%s", (p['id'], tipo, key))
                                if cursor.fetchone()['c'] == 0:
                                    status = "[⏳ HOJE]" if alvo == hoje else f"[🚨 ATRASADO {alvo.strftime('%d/%m')}]"
                                    nome_p = p.get('nome', 'Cliente').split()[0]
                                    self.pendencias.append({
                                        "dt_obj": alvo, "entity_id": p['id'], "tipo_entidade": tipo, "dias_key": key,
                                        "nome": p.get('nome', ''), "telefone": p.get('telefone', ''), "regra": f"{status} {tipo} - {grupo}",
                                        "mensagem": msg.replace("{nome}", nome_p) if msg else "", "imagem": img or "Nenhuma"
                                    })
            except Exception as e:
                print(f"Erro load_data: {e}")
            finally: conn.close()
            
            self.pendencias.sort(key=lambda x: x['dt_obj'])
            self.current_index = 0
            self.update_display()

        def update_display(self):
            total = len(self.pendencias)
            self.lbl_contador.config(text=f"Registro {self.current_index + 1} de {total}" if total > 0 else "Nenhuma pendência encontrada")
            
            if total == 0:
                self.clear_fields()
                self.btn_mark_sent.config(state="disabled")
                return
            
            self.btn_mark_sent.config(state="normal")
            item = self.pendencias[self.current_index]
            self.fields["Nome"].set(item.get("nome", ""))
            self.fields["Telefone"].set(item.get("telefone", ""))
            self.fields["Regra"].set(item.get("regra", ""))
            self.fields["Imagem"].set(item.get("imagem", "Nenhuma"))
            
            if not self.modo_broadcast:
                self.txt_mensagem.delete("1.0", "end")
                self.txt_mensagem.insert("end", item.get("mensagem", ""))
            
            self.btn_prev.config(state="normal" if self.current_index > 0 else "disabled")
            self.btn_next.config(state="normal" if self.current_index < total - 1 else "disabled")

        def mark_as_sent(self):
            if not self.pendencias: return
            
            if not self.modo_broadcast:
                item = self.pendencias[self.current_index]
                conn = get_db_connection()
                if conn:
                    try:
                        with conn.cursor() as cursor:
                            cursor.execute("""
                                INSERT INTO mensagens_enviadas (entity_id, entity_type, dias_key, data_envio) 
                                VALUES (%s, %s, %s, NOW())
                            """, (item["entity_id"], item["tipo_entidade"], item["dias_key"]))
                        conn.commit()
                    except Exception as e: print(e)
                    finally: conn.close()
            
            self.pendencias.pop(self.current_index)
            if self.current_index >= len(self.pendencias) and self.current_index > 0:
                self.current_index -= 1
            self.update_display()

        def prev_item(self):
            if self.current_index > 0:
                self.current_index -= 1
                self.update_display()

        def next_item(self):
            if self.current_index < len(self.pendencias) - 1:
                self.current_index += 1
                self.update_display()

        def clear_fields(self):
            for var in self.fields.values(): var.set("")
            self.txt_mensagem.delete("1.0", "end")

    app = ManualSenderApp(container)
    return container