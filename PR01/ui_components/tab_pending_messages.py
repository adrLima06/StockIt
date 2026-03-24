import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from database import get_db_connection
from datetime import datetime, date, timedelta
import pymysql

def create_pending_tab(parent_frame):
    page_frame = ttk.Frame(parent_frame, padding=15)
    
    # --- CABEÇALHO ---
    header_frame = ttk.Frame(page_frame)
    header_frame.pack(fill=X, pady=(0, 20))
    
    ttk.Label(header_frame, text="Pendências de Envio", font=("Calibri", 20, "bold")).pack(side=LEFT)
    
    # Opções
    var_show_future = ttk.BooleanVar(value=True) 
    
    frame_opts = ttk.Frame(header_frame)
    frame_opts.pack(side=RIGHT)
    
    # Botão de Rastreio Melhorado
    btn_trace = ttk.Button(frame_opts, text="🕵️ Rastrear Última Venda", bootstyle="warning", command=lambda: diagnosticar_ultima_compra())
    btn_trace.pack(side=LEFT, padx=(0, 10))
    
    ttk.Checkbutton(frame_opts, text="Mostrar Futuros", variable=var_show_future, bootstyle="round-toggle", command=lambda: carregar_pendencias()).pack(side=LEFT, padx=10)
    btn_refresh = ttk.Button(frame_opts, text="🔄 Atualizar", bootstyle="primary", command=lambda: carregar_pendencias())
    btn_refresh.pack(side=LEFT)

    # --- TABELA ---
    cols = ("data", "tipo", "cliente", "telefone", "motivo", "status")
    tree = ttk.Treeview(page_frame, columns=cols, show="headings", bootstyle="info", selectmode="browse")
    
    tree.heading("data", text="Data Envio"); tree.column("data", width=100, anchor=CENTER)
    tree.heading("tipo", text="Tipo"); tree.column("tipo", width=100, anchor=CENTER)
    tree.heading("cliente", text="Cliente"); tree.column("cliente", width=250)
    tree.heading("telefone", text="Contato"); tree.column("telefone", width=130, anchor=CENTER)
    tree.heading("motivo", text="Regra / Grupo"); tree.column("motivo", width=200)
    tree.heading("status", text="Status"); tree.column("status", width=120, anchor=CENTER)
    
    tree.pack(fill=BOTH, expand=YES)
    
    # --- LOG ---
    log_frame = ttk.LabelFrame(page_frame, text=" Diagnóstico Detalhado ", padding=5, bootstyle="secondary")
    log_frame.pack(fill=X, pady=10)
    
    lbl_log = ttk.Label(log_frame, text="Clique em 'Rastrear Última Venda' para entender o erro.", foreground="#ffffff", font=("Consolas", 10), wraplength=1000)
    lbl_log.pack(anchor="w", fill=X)

    def log_msg(msg, append=False):
        if append:
            novo_texto = lbl_log.cget("text") + "\n" + msg
            lbl_log.config(text=novo_texto)
        else:
            lbl_log.config(text=msg)
        print(f"[PENDING] {msg}")
        page_frame.update_idletasks()

    def refresh_data():
        carregar_pendencias()
    
    page_frame.refresh_data = refresh_data

    def calcular_data_alvo(data_base, dias_apos):
        if not data_base: return None
        hoje = datetime.now().date()
        
        if isinstance(data_base, str):
            try: data_base = datetime.strptime(data_base, '%Y-%m-%d').date()
            except: 
                try: data_base = datetime.strptime(data_base, '%d/%m/%Y').date()
                except: return None
        
        if isinstance(data_base, datetime): data_base = data_base.date()
        data_alvo = data_base + timedelta(days=dias_apos)
        
        ds = data_alvo.weekday()
        if ds == 5: data_alvo += timedelta(days=2)
        elif ds == 6: data_alvo += timedelta(days=1)
        
        return data_alvo

    def diagnosticar_ultima_compra():
        """Analisa a última compra e verifica TODOS os tipos de regras"""
        conn = get_db_connection()
        if not conn: return
        
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                # 1. Pega a última compra
                cursor.execute("SELECT * FROM compras_detalhadas ORDER BY id DESC LIMIT 1")
                compra = cursor.fetchone()
                
                if not compra:
                    log_msg("ERRO: Nenhuma compra encontrada no banco.")
                    return
                
                grupo_venda = compra['grupo']
                msg_final = f"=== ANÁLISE DA VENDA #{compra['id']} ===\n"
                msg_final += f"Cliente: {compra['nome']} | Grupo: '{grupo_venda}'\n"
                msg_final += "-"*40 + "\n"
                
                # 2. Busca regra correta (Tipo COMPRA)
                cursor.execute("SELECT * FROM automacao_mensagens WHERE grupo = %s AND tipo_entidade = 'COMPRA'", (grupo_venda,))
                regras_corretas = cursor.fetchall()

                if regras_corretas:
                    msg_final += f"✅ SUCESSO: Existem {len(regras_corretas)} regras do tipo COMPRA para '{grupo_venda}'.\n"
                    for r in regras_corretas:
                        dt = calcular_data_alvo(compra['data_compra'], r['dias_apos'])
                        msg_final += f"   -> Regra (+{r['dias_apos']}d): Agendado para {dt}\n"
                else:
                    msg_final += f"❌ FALHA: Nenhuma regra de 'COMPRA' encontrada para '{grupo_venda}'.\n\n"
                    
                    # 3. INVESTIGAÇÃO SHERLOCK HOLMES: Procura regras erradas
                    cursor.execute("SELECT * FROM automacao_mensagens WHERE grupo = %s", (grupo_venda,))
                    todas_regras_grupo = cursor.fetchall()
                    
                    if todas_regras_grupo:
                        msg_final += f"⚠️ ALERTA: Achei regras para '{grupo_venda}', mas o TIPO está errado:\n"
                        for r in todas_regras_grupo:
                            msg_final += f"   -> Id {r['id']} é do tipo '{r['tipo_entidade']}' (Deveria ser 'COMPRA')\n"
                        msg_final += "SOLUÇÃO: Apague essas regras e crie novas selecionando 'Tipo: Pós-Venda (Compra)'."
                    else:
                        msg_final += "⚠️ ALERTA: Não achei NENHUMA regra com esse nome de grupo.\n"
                        msg_final += "SOLUÇÃO: Verifique se o grupo da venda ('AQUEC SOLAR'?) está escrito\n"
                        msg_final += "exatamente igual ao grupo da regra (Maiúsculas, espaços, etc)."

                log_msg(msg_final)
                
        except Exception as e:
            log_msg(f"Erro no diagnóstico: {e}")
        finally:
            conn.close()

    def carregar_pendencias():
        for i in tree.get_children(): tree.delete(i)
        
        conn = get_db_connection()
        if not conn: return
            
        hoje = datetime.now().date()
        ano_atual = hoje.year
        
        mostrar_futuro = var_show_future.get()
        limite_passado = hoje - timedelta(days=5)
        limite_futuro = hoje + timedelta(days=60) if mostrar_futuro else hoje 
        
        pendencias = []

        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("SELECT * FROM automacao_mensagens")
                regras = cursor.fetchall()
                
                if not regras: return

                cursor.execute("SELECT id, nome, telefone, grupo, data_cadastro as data_ref FROM leads")
                leads = cursor.fetchall()
                cursor.execute("SELECT id, nome, telefone, grupo, data_compra as data_ref FROM compras_detalhadas")
                compras = cursor.fetchall()
                cursor.execute("SELECT id, nome, whatsapp as telefone, grupo, data_cadastro, data_nascimento FROM clientes")
                clientes = cursor.fetchall()

                for regra in regras:
                    tipo = regra['tipo_entidade']
                    grupo = regra['grupo']
                    dias = regra['dias_apos']
                    
                    lista = []
                    eh_niver = False
                    
                    if tipo == 'LEAD': lista = [x for x in leads if x['grupo'] == grupo]
                    elif tipo == 'COMPRA': lista = [x for x in compras if x['grupo'] == grupo]
                    elif tipo == 'CLIENTE_CAD':
                        lista = [x for x in clientes if x['grupo'] == grupo]
                        for c in lista: c['data_ref'] = c['data_cadastro']
                    elif tipo == 'ANIVERSARIO':
                        lista = [x for x in clientes if x['grupo'] == grupo]
                        for c in lista: c['data_ref'] = c['data_nascimento']
                        eh_niver = True

                    for p in lista:
                        if not p.get('data_ref'): continue
                        
                        dt_alvo = calcular_data_alvo(p['data_ref'], dias)
                        if eh_niver: 
                             try: dt_alvo = date(ano_atual, p['data_ref'].month, p['data_ref'].day)
                             except: dt_alvo = date(ano_atual, 3, 1)

                        if dt_alvo and (limite_passado <= dt_alvo <= limite_futuro):
                            key = int(f"{ano_atual}{dias}") if eh_niver else dias
                            cursor.execute("SELECT COUNT(*) as c FROM mensagens_enviadas WHERE entity_id=%s AND entity_type=%s AND dias_key=%s", 
                                           (p['id'], tipo, key))
                            ja_foi = cursor.fetchone()['c'] > 0
                            
                            status = "✅ Enviado" if ja_foi else ("🚨 Atrasado" if dt_alvo < hoje else ("⏳ Hoje" if dt_alvo == hoje else f"📅 {dt_alvo.strftime('%d/%m')}"))
                            cor = "info"
                            if "Atrasado" in status: cor = "danger"
                            elif "Hoje" in status: cor = "warning"
                            elif "Enviado" in status: cor = "success"

                            if not ja_foi or mostrar_futuro:
                                pendencias.append({
                                    "dt_format": dt_alvo.strftime("%d/%m/%Y"),
                                    "dt_obj": dt_alvo,
                                    "tipo": tipo,
                                    "nome": p['nome'],
                                    "tel": p['telefone'],
                                    "motivo": f"{grupo} (+{dias}d)",
                                    "status": status,
                                    "cor": cor
                                })

                pendencias.sort(key=lambda x: x['dt_obj'])
                
                for item in pendencias:
                    tree.insert("", END, values=(item['dt_format'], item['tipo'], item['nome'], item['tel'], item['motivo'], item['status']), tags=(item['cor'],))
                
                tree.tag_configure("danger", foreground="#ff4d4d")
                tree.tag_configure("warning", foreground="#ffc107")
                tree.tag_configure("info", foreground="#17a2b8")
                tree.tag_configure("success", foreground="#28a745")
                        
        except Exception as e:
            print(e)
        finally:
            conn.close()

    page_frame.after(500, carregar_pendencias)
    return page_frame