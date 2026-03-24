import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, filedialog
from ttkbootstrap.scrolled import ScrolledText
import pymysql
from database import get_db_connection, obter_grupos_cadastrados
import threading
import queue
import time
from automation_service import enviar_mensagem_com_seguranca

# Variáveis Globais do Broadcast
broadcast_thread = None
broadcast_stop_event = threading.Event()
broadcast_pause_event = threading.Event()
broadcast_skip_event = threading.Event()
broadcast_progress_queue = queue.Queue()

def create_tab(parent_frame):
    page_frame = ttk.Frame(parent_frame)
    main_pane = ttk.PanedWindow(page_frame, orient=HORIZONTAL)
    main_pane.pack(fill=BOTH, expand=YES)
    
    # --- Painel Esquerdo (Formulários) ---
    form_pane = ttk.Frame(main_pane)
    main_pane.add(form_pane, weight=1)

    # 1. CARD: Editor de Regras (Automático)
    rules_card = ttk.LabelFrame(form_pane, text=" Editor de Regras (Automação/Aniversário) ", padding=10, bootstyle="primary")
    rules_card.pack(fill=X, expand=NO, padx=(0, 10), pady=10)
    
    form_fields_frame = ttk.Frame(rules_card, padding=5)
    form_fields_frame.pack(fill=BOTH, expand=YES)
    form_fields_frame.columnconfigure(1, weight=1)

    entries = {}
    labels_ref = {} 
    grupos_dinamicos = obter_grupos_cadastrados()

    campos = [
        ("Tipo de Entidade:", "tipo_entidade", "Combobox", ["LEAD", "COMPRA", "CLIENTE_CAD", "ANIVERSARIO"]), 
        ("Grupo de Interesse:", "grupo", "Combobox", grupos_dinamicos), 
        ("Enviar Após (dias):", "dias_apos", "Entry", None), 
        ("Texto da Mensagem:", "texto_mensagem", "ScrolledText", None), 
        ("Caminho da Imagem:", "caminho_imagem", "Entry", None)
    ]
              
    for i, (label_text, key, widget_type, options) in enumerate(campos):
        lbl = ttk.Label(form_fields_frame, text=label_text, font=("Segoe UI", 9, "bold"))
        lbl.grid(row=i*2, column=0, columnspan=2, sticky='w', pady=(5,2))
        labels_ref[key] = lbl
        
        if widget_type == "Entry": 
            entries[key] = ttk.Entry(form_fields_frame)
            if key == "dias_apos": entries[key].insert(0, "0")
        elif widget_type == "Combobox": 
            st_val = "readonly" if key == "tipo_entidade" else None
            entries[key] = ttk.Combobox(form_fields_frame, values=options, state=st_val)
        elif widget_type == "ScrolledText": 
            entries[key] = ScrolledText(form_fields_frame, height=4, autohide=True)
            
        entries[key].grid(row=i*2+1, column=0, columnspan=2, sticky='ew')

    def on_type_change(event):
        tipo = entries['tipo_entidade'].get()
        if tipo == "ANIVERSARIO":
            labels_ref['dias_apos'].config(text="Dias de Antecedência (0 = No dia):")
            entries['dias_apos'].delete(0, END); entries['dias_apos'].insert(0, "0")
        else:
            labels_ref['dias_apos'].config(text="Enviar Após (dias):")
    entries['tipo_entidade'].bind("<<ComboboxSelected>>", on_type_change)

    def select_rule_image():
        filepath = filedialog.askopenfilename(title="Selecionar Imagem", filetypes=[("Imagens", "*.png *.jpg *.jpeg")])
        if filepath:
            entries['caminho_imagem'].delete(0, END)
            entries['caminho_imagem'].insert(0, filepath)
    
    ttk.Button(form_fields_frame, text="📁", command=select_rule_image, bootstyle="secondary-outline", width=4).grid(row=9, column=1, sticky='e')

    action_frame = ttk.Frame(form_fields_frame)
    action_frame.grid(row=10, column=0, columnspan=2, sticky='ew', pady=10)
    action_frame.columnconfigure((0,1,2,3), weight=1)
    
    save_button = ttk.Button(action_frame, text="💾 Salvar", bootstyle="success")
    save_button.grid(row=0, column=0, sticky='ew', padx=2)
    delete_button = ttk.Button(action_frame, text="🗑️ Apagar", bootstyle="danger")
    delete_button.grid(row=0, column=1, sticky='ew', padx=2)
    clear_button = ttk.Button(action_frame, text="✨ Limpar", bootstyle="secondary")
    clear_button.grid(row=0, column=2, sticky='ew', padx=2)

    # 2. CARD: Broadcast (Atualizado para Múltiplos Grupos)
    broadcast_card = ttk.LabelFrame(form_pane, text=" Envio em Massa (Broadcast) ", padding=10, bootstyle="warning")
    broadcast_card.pack(fill=X, expand=NO, padx=(0, 10), pady=10)
    
    broadcast_frame = ttk.Frame(broadcast_card, padding=5)
    broadcast_frame.pack(fill=BOTH, expand=YES)
    broadcast_frame.columnconfigure(0, weight=1)

    ttk.Label(broadcast_frame, text="Público Alvo (Selecione um ou mais):", font=("Segoe UI", 9, "bold")).grid(row=0, column=0, columnspan=2, sticky='w')

    # Container para os Checkbuttons dos Grupos
    groups_scroll = ttk.Frame(broadcast_frame, height=100)
    groups_scroll.grid(row=1, column=0, columnspan=2, sticky='ew', pady=(0,5))
    
    selected_vars = {} # Dicionário para guardar as variáveis dos grupos

    def carregar_checkbuttons_grupos():
        for widget in groups_scroll.winfo_children():
            widget.destroy()
        selected_vars.clear()
        
        # Opções Especiais
        for especial in ["TODOS OS CLIENTES", "TODOS OS LEADS"]:
            var = ttk.BooleanVar()
            cb = ttk.Checkbutton(groups_scroll, text=especial, variable=var, bootstyle="round-toggle")
            cb.pack(side=TOP, anchor='w', padx=5)
            selected_vars[especial] = var

        ttk.Separator(groups_scroll, orient=HORIZONTAL).pack(fill=X, pady=5)

        # Grupos Reais do Banco
        for g in obter_grupos_cadastrados():
            var = ttk.BooleanVar()
            cb = ttk.Checkbutton(groups_scroll, text=f"Grupo: {g}", variable=var)
            cb.pack(side=TOP, anchor='w', padx=5)
            selected_vars[g] = var

    carregar_checkbuttons_grupos()
    
    ttk.Label(broadcast_frame, text="Mensagem do Broadcast:", font=("Segoe UI", 9, "bold")).grid(row=2, column=0, columnspan=2, sticky='w')
    broadcast_text = ScrolledText(broadcast_frame, height=4, autohide=True)
    broadcast_text.grid(row=3, column=0, columnspan=2, sticky='ew', pady=(0,5))
    
    broadcast_img_var = ttk.StringVar()
    ttk.Entry(broadcast_frame, textvariable=broadcast_img_var).grid(row=4, column=0, sticky='ew')
    
    def select_broadcast_image():
        filepath = filedialog.askopenfilename(filetypes=[("Imagens", "*.png *.jpg *.jpeg")])
        if filepath: broadcast_img_var.set(filepath)
    
    ttk.Button(broadcast_frame, text="📁", command=select_broadcast_image, bootstyle="secondary-outline", width=4).grid(row=4, column=1, sticky='e', padx=(5,0))
    
    status_label = ttk.Label(broadcast_frame, text="Status: Aguardando", bootstyle="inverse-secondary")
    status_label.grid(row=6, column=0, columnspan=2, sticky='ew', pady=(10, 2))
    
    progress_bar = ttk.Progressbar(broadcast_frame, length=200, bootstyle="warning-striped")
    progress_bar.grid(row=7, column=0, columnspan=2, sticky='ew', pady=(0, 10))

    btn_control_frame = ttk.Frame(broadcast_frame)
    btn_control_frame.grid(row=8, column=0, columnspan=2, sticky='ew')
    btn_control_frame.columnconfigure((0, 1, 2), weight=1)

    start_button = ttk.Button(btn_control_frame, text="🚀 ENVIAR", bootstyle="danger")
    start_button.grid(row=0, column=0, sticky='ew', padx=2)
    
    pause_button = ttk.Button(btn_control_frame, text="⏸️ Pausar", bootstyle="info", state=DISABLED)
    pause_button.grid(row=0, column=1, sticky='ew', padx=2)

    skip_button = ttk.Button(btn_control_frame, text="⏩ Pular 1", bootstyle="warning", state=DISABLED)
    skip_button.grid(row=0, column=2, sticky='ew', padx=2)

    def refresh_all_groups():
        novos = obter_grupos_cadastrados()
        entries['grupo']['values'] = novos
        carregar_checkbuttons_grupos()

    refresh_btn = ttk.Button(action_frame, text="🔄", command=refresh_all_groups, bootstyle="outline-secondary", width=3)
    refresh_btn.grid(row=0, column=3, sticky='ew', padx=2)

    # --- Painel Direito (Tabela de Regras) ---
    table_pane = ttk.Frame(main_pane)
    main_pane.add(table_pane, weight=2)
    
    table_card = ttk.LabelFrame(table_pane, text=" Regras Ativas ", padding=10)
    table_card.pack(fill=BOTH, expand=YES, pady=10)
    
    cols = ("id", "tipo", "grupo", "dias"); tree = ttk.Treeview(table_card, columns=cols, show="headings")
    tree.heading("id", text="ID"); tree.column("id", width=30)
    tree.heading("tipo", text="Tipo"); tree.column("tipo", width=80)
    tree.heading("grupo", text="Grupo"); tree.column("grupo", width=120)
    tree.heading("dias", text="Dias"); tree.column("dias", width=50, anchor=CENTER)
    tree.pack(fill=BOTH, expand=YES)

    # --- LÓGICA DO SISTEMA ---
    selected_rule_id = None
    
    def refresh_table():
        nonlocal selected_rule_id; selected_rule_id = None
        for item in tree.get_children(): tree.delete(item)
        conn = get_db_connection()
        if not conn: return
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, tipo_entidade, grupo, dias_apos FROM automacao_mensagens ORDER BY tipo_entidade, grupo")
                for row in cursor.fetchall(): tree.insert("", END, values=row)
        finally: conn.close()
    
    def clear_form():
        nonlocal selected_rule_id; selected_rule_id = None
        for key, widget in entries.items():
            if isinstance(widget, ScrolledText): widget.delete('1.0', END)
            else: 
                if isinstance(widget, ttk.Combobox): widget.set('')
                else: widget.delete(0, END)
        entries['dias_apos'].insert(0, "0")
        tree.selection_remove(tree.selection())

    def on_rule_select(event):
        nonlocal selected_rule_id
        if not tree.selection(): return
        selected_rule_id = tree.item(tree.selection()[0], "values")[0]
        conn = get_db_connection()
        if not conn: return
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("SELECT * FROM automacao_mensagens WHERE id = %s", (selected_rule_id,))
                data = cursor.fetchone()
                if not data: return
                clear_form(); selected_rule_id = data['id']
                entries['tipo_entidade'].set(data['tipo_entidade'])
                entries['grupo'].set(data['grupo'])
                entries['dias_apos'].delete(0, END); entries['dias_apos'].insert(0, str(data['dias_apos']))
                entries['caminho_imagem'].delete(0, END); entries['caminho_imagem'].insert(0, data['caminho_imagem'] or "")
                entries['texto_mensagem'].delete('1.0', END); entries['texto_mensagem'].insert('1.0', data['texto_mensagem'])
                on_type_change(None)
        finally: conn.close()

    def save_rule():
        d = {k: w.get('1.0', 'end-1c').strip() if isinstance(w, ScrolledText) else w.get().strip() for k, w in entries.items()}
        if not all([d['tipo_entidade'], d['grupo'], d['dias_apos'], d['texto_mensagem']]):
            messagebox.showwarning("Aviso", "Preencha os campos obrigatórios."); return
        
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                if selected_rule_id:
                    cursor.execute("UPDATE automacao_mensagens SET tipo_entidade=%s, grupo=%s, dias_apos=%s, texto_mensagem=%s, caminho_imagem=%s WHERE id=%s", 
                                   (d['tipo_entidade'], d['grupo'], d['dias_apos'], d['texto_mensagem'], d['caminho_imagem'], selected_rule_id))
                else:
                    cursor.execute("INSERT INTO automacao_mensagens (tipo_entidade, grupo, dias_apos, texto_mensagem, caminho_imagem) VALUES (%s, %s, %s, %s, %s)",
                                   (d['tipo_entidade'], d['grupo'], d['dias_apos'], d['texto_mensagem'], d['caminho_imagem']))
            conn.commit(); messagebox.showinfo("Sucesso", "Regra salva!"); clear_form(); refresh_table(); refresh_all_groups()
        except Exception as e: messagebox.showerror("Erro", str(e))
        finally: conn.close()

    def delete_rule():
        if not selected_rule_id: return
        if not messagebox.askyesno("Confirmar", "Deletar regra?"): return
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor: cursor.execute("DELETE FROM automacao_mensagens WHERE id=%s", (selected_rule_id,))
            conn.commit(); clear_form(); refresh_table(); refresh_all_groups()
        finally: conn.close()

    # --- LÓGICA DO BROADCAST (WORKER) ---
    def update_broadcast_ui():
        try:
            while True:
                total, sent = broadcast_progress_queue.get(timeout=0.1)
                if total is None:
                    status_label.config(text="Status: Concluído", bootstyle="success")
                    progress_bar.stop(); progress_bar.config(value=100)
                    start_button.config(state=NORMAL); pause_button.config(state=DISABLED); skip_button.config(state=DISABLED)
                    break
                status_label.config(text=f"Enviando... ({sent}/{total})", bootstyle="warning")
                if total > 0: progress_bar.config(value=(sent/total)*100)
        except queue.Empty: pass
        if broadcast_thread and broadcast_thread.is_alive():
            page_frame.after(100, update_broadcast_ui)

    def worker_broadcast():
        broadcast_stop_event.clear(); broadcast_pause_event.clear(); broadcast_skip_event.clear()
        
        # Coleta grupos marcados
        grupos_selecionados = [nome for nome, var in selected_vars.items() if var.get()]
        if not grupos_selecionados:
            messagebox.showwarning("Aviso", "Selecione ao menos um grupo ou categoria.")
            broadcast_progress_queue.put((None, 0))
            return

        msg = broadcast_text.get('1.0', 'end-1c').strip()
        img = broadcast_img_var.get().strip()
        if not msg and not img: return

        conn = get_db_connection()
        telefones = set()
        try:
            with conn.cursor() as cursor:
                for item in grupos_selecionados:
                    if item == "TODOS OS CLIENTES":
                        cursor.execute("SELECT whatsapp FROM clientes UNION SELECT telefone FROM compras_detalhadas")
                    elif item == "TODOS OS LEADS":
                        cursor.execute("SELECT telefone FROM leads")
                    else:
                        # Busca por grupo específico em todas as tabelas
                        cursor.execute("SELECT whatsapp FROM clientes WHERE grupo=%s UNION SELECT telefone FROM compras_detalhadas WHERE grupo=%s UNION SELECT telefone FROM leads WHERE grupo=%s", (item, item, item))
                    
                    for row in cursor.fetchall():
                        if row[0]: telefones.add(row[0])
        finally: conn.close()

        lista = list(telefones)
        total = len(lista)
        broadcast_progress_queue.put((total, 0))
        
        for i, fone in enumerate(lista, 1):
            if broadcast_stop_event.is_set(): break
            if broadcast_pause_event.is_set():
                status_label.config(text="Status: PAUSADO", bootstyle="info")
                broadcast_pause_event.wait()
            if broadcast_skip_event.is_set():
                broadcast_skip_event.clear()
                continue
            enviar_mensagem_com_seguranca(fone, msg, img, broadcast_skip_event)
            broadcast_progress_queue.put((total, i))
            time.sleep(1) 

        broadcast_progress_queue.put((None, total))
        messagebox.showinfo("Fim", f"Broadcast Finalizado. {total} contatos processados.")

    def start_broadcast():
        global broadcast_thread
        if broadcast_thread and broadcast_thread.is_alive(): return
        start_button.config(state=DISABLED); pause_button.config(state=NORMAL); skip_button.config(state=NORMAL)
        broadcast_thread = threading.Thread(target=worker_broadcast, daemon=True)
        broadcast_thread.start()
        update_broadcast_ui()

    def pause_broadcast():
        if broadcast_pause_event.is_set(): broadcast_pause_event.clear(); pause_button.config(text="⏸️ Pausar")
        else: broadcast_pause_event.set(); pause_button.config(text="▶️ Continuar")

    def skip_broadcast():
        broadcast_skip_event.set()

    # Bindings Finais
    save_button.config(command=save_rule); delete_button.config(command=delete_rule); clear_button.config(command=clear_form)
    tree.bind("<<TreeviewSelect>>", on_rule_select)
    start_button.config(command=start_broadcast); pause_button.config(command=pause_broadcast); skip_button.config(command=skip_broadcast)
    
    refresh_table()
    return page_frame