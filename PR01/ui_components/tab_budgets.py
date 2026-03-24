import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, simpledialog, filedialog
from web_scraper import buscar_produtos_site
from database import get_all_products_from_cache, save_product_to_cache
from datetime import datetime
import os
import sys
import io
import requests
import threading
import locale
import re
import unicodedata

# --- TEXTOS PADRÃO ---
TXT_INSTALACAO = "Mão de obra para instalação  - não Inclusa. Solicite conosco contato de técnico qualificado com garantia de Fábrica"
TXT_COMPONENTES = "Componentes necessários, (conexões, tubulação, registros,) de acordo com a demanda - não incluso no orçamento."
TXT_VALIDADE = "Validade do Orçamento: 15 Dias de acordo com o Estoque."

# --- VERIFICAÇÃO DE BIBLIOTECAS ---
try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import Table, TableStyle, Paragraph, Image as PlatypusImage
    from pypdf import PdfReader, PdfWriter
    from reportlab.lib.enums import TA_RIGHT
except ImportError:
    messagebox.showerror("Erro Crítico", "Bibliotecas faltando.\nExecute: pip install reportlab pypdf pillow requests beautifulsoup4")

# --- LOCALE ---
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except:
    try: locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252')
    except: pass

class BudgetPDFGenerator:
    def __init__(self, base_pdf_path, output_path):
        self.base_pdf_path = base_pdf_path
        self.output_path = output_path
        
        base_dir = os.path.dirname(base_pdf_path)
        self.base2_path = os.path.join(base_dir, "OrçamentoBase2.pdf")
        self.final_path = os.path.join(base_dir, "OrçamentoBaseFinal.pdf")
        
        self.packet = io.BytesIO()
        self.c = canvas.Canvas(self.packet, pagesize=A4)
        self.width, self.height = A4 

    def parse_currency(self, value_str):
        if isinstance(value_str, (int, float)): return float(value_str)
        if not value_str: return 0.0
        clean = re.sub(r'[^\d.,]', '', str(value_str))
        if not clean: return 0.0
        if "," in clean: clean = clean.replace(".", "").replace(",", ".")
        try: return float(clean)
        except: return 0.0

    def format_currency(self, value):
        try: return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        except: return "R$ 0,00"

    def fetch_image_for_table(self, url, width=45, height=45):
        if not url or url == 'None': return None
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, stream=True, timeout=4)
            if response.status_code == 200:
                img = PlatypusImage(io.BytesIO(response.content), width=width, height=height)
                return img
        except: pass 
        return None

    def draw_page_content(self, canvas_obj, products_slice, page_type, budget_data, totals=None):
        start_y_pos = 700
        
        # CABEÇALHO
        if page_type in ['SINGLE', 'LAST']:
            data_txt = datetime.now().strftime("%d de %B de %Y")
            canvas_obj.setFillColor(colors.black)
            canvas_obj.setFont("Helvetica", 8)
            canvas_obj.drawRightString(215, 177, data_txt) 

        if page_type in ['SINGLE', 'FIRST']:
            canvas_obj.setFillColor(colors.black)
            canvas_obj.setFont("Helvetica-Bold", 12)
            cli = unicodedata.normalize("NFC", f" {budget_data.get('customer', '')}")
            canvas_obj.drawString(116, 741, cli)

        # TABELA
        col_widths = [50, 205, 40, 35, 80, 90]
        
        styles = getSampleStyleSheet()
        style_desc = ParagraphStyle('Desc', parent=styles['Normal'], fontSize=8, leading=10)
        
        # Estilo para o Total Geral (Rodapé da tabela)
        style_total_right = ParagraphStyle(
            'TotalRight', 
            parent=styles['Normal'], 
            fontSize=8, 
            leading=10, 
            alignment=TA_RIGHT
        )
        
        headers = ['Produto', 'Descrição', 'Cód.', 'Qtd', 'À Vista', 'Total a Prazo']
        table_data = [headers]
        
        # Lista para armazenar comandos extras de estilo (para o SPAN dos manuais)
        extra_tbl_cmds = []

        for prod in products_slice:
            img_obj = self.fetch_image_for_table(prod.get("image_url"))
            
            safe_name = unicodedata.normalize("NFC", prod.get('name', ''))
            safe_link = unicodedata.normalize("NFC", prod.get('link', ''))
            safe_cod = unicodedata.normalize("NFC", str(prod.get('cod', '') or ''))
            
            # Se tiver link, mostra em azul, senão (item manual) só o nome
            if safe_link:
                desc_html = f"<b>{safe_name}</b><br/><font color='blue' size=7>{safe_link}</font>"
            else:
                desc_html = f"<b>{safe_name}</b>"

            p_desc = Paragraph(desc_html, style_desc)
            
            try: qtd = int(prod.get("qty", 1))
            except: qtd = 1
            
            # 1. Valor à Vista
            val_vista_unit = self.parse_currency(prod.get("price_cash", 0))
            val_vista_total = val_vista_unit * qtd
            p_vista_str = self.format_currency(val_vista_total)
            
            # 2. Valor a Prazo (TOTAL INTEGRAL DA LINHA)
            raw_prazo = str(prod.get('price_install', ''))
            raw_prazo = unicodedata.normalize("NFC", raw_prazo)
            
            p_final = ""
            
            # Tenta extrair o valor da parcela (ex: de "10x R$ 50,00")
            match_val = re.search(r'R\$\s*([\d.,]+)', raw_prazo)
            if match_val:
                val_parcela_unit = self.parse_currency(match_val.group(1))
                
                # Detecta número de parcelas (padrão 10)
                match_x = re.search(r'(\d+)[xX]', raw_prazo)
                num_parc = int(match_x.group(1)) if match_x else 10
                
                # CÁLCULO: (Valor Parcela * Num Parcelas * Qtd)
                val_total_prazo_line = val_parcela_unit * num_parc * qtd
                
                # Exibe o valor total limpo
                p_final = self.format_currency(val_total_prazo_line)
                
            elif val_vista_total > 0:
                 # Fallback: Se não tem prazo definido, calcula +15% sobre o vista total
                 v_prazo_calc = val_vista_total * 1.15
                 p_final = self.format_currency(v_prazo_calc)
            
            # LÓGICA DE MESCLAGEM (SPAN) PARA ITENS SEM FOTO (MANUAIS/SERVIÇOS)
            # Verifica se não tem objeto de imagem E se a URL original é vazia/None
            is_manual_or_service = (img_obj is None) and (not prod.get("image_url"))
            
            row_idx = len(table_data) # Índice da linha atual na tabela (considerando o header)

            if is_manual_or_service:
                # Se for manual: Coloca a descrição na Coluna 0 e deixa a Coluna 1 vazia
                # O SPAN vai cobrir a Coluna 1
                row = [p_desc, '', safe_cod, str(qtd), p_vista_str, p_final]
                # Adiciona comando de mesclagem: Coluna 0 até Coluna 1 na linha atual
                extra_tbl_cmds.append(('SPAN', (0, row_idx), (1, row_idx)))
            else:
                # Normal: Imagem na Col 0, Descrição na Col 1
                row = [img_obj if img_obj else "", p_desc, safe_cod, str(qtd), p_vista_str, p_final]

            table_data.append(row)

        # TOTAL GERAL (RODAPÉ DA TABELA)
        if page_type in ['SINGLE', 'LAST'] and totals:
            val_total_prazo = totals['prazo']
            val_parcela_mensal = val_total_prazo / 10
            
            str_total_prazo = self.format_currency(val_total_prazo)
            str_parcela_mensal = self.format_currency(val_parcela_mensal)
            
            html_total_prazo = f"<b>{str_total_prazo}</b><br/><font size=7>10x de {str_parcela_mensal}</font>"
            p_total_prazo = Paragraph(html_total_prazo, style_total_right)

            row_total = [
                '', '', '', 'TOTAL:', 
                self.format_currency(totals['vista']), 
                p_total_prazo
            ]
            table_data.append(row_total)

        # Estilo Base
        last_row = len(table_data) - 1
        tbl_cmds = [
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 9),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            ('VALIGN', (0,0), (-1,0), 'MIDDLE'),
            ('FONTSIZE', (0,1), (-1,-1), 8),
            ('VALIGN', (0,1), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,1), (0,-1), 'CENTER'),
            ('ALIGN', (1,1), (1,-1), 'CENTER'),
            ('ALIGN', (2,1), (2,-1), 'CENTER'),
            ('ALIGN', (3,1), (-1,-1), 'CENTER'),
            ('ALIGN', (4,1), (-1,-1), 'CENTER'),
            ('GRID', (0,0), (-1,-2 if (page_type in ['SINGLE', 'LAST'] and totals) else -1), 0.5, colors.black),
            ('BOX', (0,0), (-1,-1), 1, colors.black),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ]
        
        # Adiciona os comandos de SPAN dos itens manuais
        tbl_cmds.extend(extra_tbl_cmds)
        
        if page_type in ['SINGLE', 'LAST'] and totals:
            tbl_cmds.append(('BACKGROUND', (3, last_row), (-1, last_row), colors.lightgrey))
            tbl_cmds.append(('FONTNAME', (3, last_row), (-1, last_row), 'Helvetica-Bold'))
            tbl_cmds.append(('FONTSIZE', (3, last_row), (-1, last_row), 8))
            tbl_cmds.append(('ALIGN', (3, last_row), (3, last_row), 'RIGHT'))
            tbl_cmds.append(('GRID', (3, last_row), (-1, last_row), 0.5, colors.black))
            tbl_cmds.append(('VALIGN', (5, last_row), (5, last_row), 'MIDDLE'))

        t = Table(table_data, colWidths=col_widths)
        t.setStyle(TableStyle(tbl_cmds))
        w, h = t.wrapOn(canvas_obj, 500, 600)
        
        t.drawOn(canvas_obj, 48, start_y_pos - h)

        # RODAPÉ PÁGINA
        if page_type in ['SINGLE', 'LAST']:
            y_pos = start_y_pos - h - 30
            
            canvas_obj.setFont("Helvetica-Bold", 10)
            canvas_obj.drawString(48, y_pos, "Observações:")
            
            obs_list = budget_data.get("observations", [])
            if isinstance(obs_list, str): obs_list = [obs_list]
            
            if not any("Validade" in str(o) for o in obs_list):
                obs_list.append(TXT_VALIDADE)

            canvas_obj.setFont("Helvetica", 9)
            for obs in obs_list:
                y_pos -= 15
                safe_obs = unicodedata.normalize("NFC", str(obs))
                canvas_obj.drawString(48, y_pos, f"- {safe_obs}")

            signature = unicodedata.normalize("NFC", budget_data.get("signature", ""))
            canvas_obj.setFont("Helvetica", 10)
            canvas_obj.line(200, 150, 400, 150)
            canvas_obj.drawCentredString(300, 135, signature)

    def calculate_totals(self, products):
        t_vista = 0.0
        t_prazo = 0.0
        for p in products:
            try: q = int(p.get("qty", 1))
            except: q = 1
            
            v_vista = self.parse_currency(p.get("price_cash", 0))
            
            raw_prazo = str(p.get('price_install', ''))
            v_prazo_unit = 0.0
            
            match_val = re.search(r'R\$\s*([\d.,]+)', raw_prazo)
            if match_val:
                val_p = self.parse_currency(match_val.group(1))
                match_q = re.search(r'(\d{1,2})\s*[xX]', raw_prazo)
                n = int(match_q.group(1)) if match_q else 10
                v_prazo_unit = val_p * n
            else:
                if v_vista > 0: v_prazo_unit = v_vista * 1.15
            
            t_vista += v_vista * q
            t_prazo += v_prazo_unit * q
        return {'vista': t_vista, 'prazo': t_prazo}

    def generate(self, data):
        products = data.get("products", [])
        total_items = len(products)
        totals = self.calculate_totals(products)
        
        LIMIT_SINGLE = 7
        LIMIT_FULL_PAGE = 11
        LIMIT_LAST_PAGE = 7

        output = PdfWriter()

        try:
            if total_items <= LIMIT_SINGLE:
                packet = io.BytesIO()
                c = canvas.Canvas(packet, pagesize=A4)
                self.draw_page_content(c, products, 'SINGLE', data, totals)
                c.save()
                packet.seek(0)
                new_pdf = PdfReader(packet)
                if os.path.exists(self.base_pdf_path):
                    base = PdfReader(open(self.base_pdf_path, "rb"))
                    output.add_page(base.pages[0])
                    output.pages[0].merge_page(new_pdf.pages[0])
                else: output.add_page(new_pdf.pages[0])

            else:
                path_pg1 = self.base2_path if os.path.exists(self.base2_path) else self.base_pdf_path
                path_mid = self.base2_path if os.path.exists(self.base2_path) else self.base_pdf_path
                path_end = self.final_path if os.path.exists(self.final_path) else self.base_pdf_path

                current_idx = 0
                page_num = 1
                
                while (total_items - current_idx) > LIMIT_LAST_PAGE:
                    packet = io.BytesIO()
                    c = canvas.Canvas(packet, pagesize=A4)
                    chunk = products[current_idx : current_idx + LIMIT_FULL_PAGE]
                    
                    p_type = 'FIRST' if page_num == 1 else 'MIDDLE'
                    self.draw_page_content(c, chunk, p_type, data, None)
                    c.save()
                    packet.seek(0)
                    
                    new_pdf = PdfReader(packet)
                    template_path = path_pg1 if page_num == 1 else path_mid
                    
                    if os.path.exists(template_path):
                        base = PdfReader(open(template_path, "rb"))
                        output.add_page(base.pages[0])
                        output.pages[-1].merge_page(new_pdf.pages[0])
                    else: output.add_page(new_pdf.pages[0])
                        
                    current_idx += len(chunk)
                    page_num += 1

                packet = io.BytesIO()
                c = canvas.Canvas(packet, pagesize=A4)
                chunk = products[current_idx:]
                self.draw_page_content(c, chunk, 'LAST', data, totals)
                c.save()
                packet.seek(0)
                new_pdf = PdfReader(packet)
                if os.path.exists(path_end):
                    base = PdfReader(open(path_end, "rb"))
                    output.add_page(base.pages[0])
                    output.pages[-1].merge_page(new_pdf.pages[0])
                else: output.add_page(new_pdf.pages[0])

            with open(self.output_path, "wb") as f: output.write(f)
            return True, f"Gerado: {self.output_path}"

        except PermissionError: return False, "PDF aberto. Feche e tente novamente."
        except Exception as e: return False, str(e)

# =============================================================================
# UI
# =============================================================================

def create_budgets_tab(parent_frame):
    page_frame = ttk.Frame(parent_frame)
    paned = ttk.PanedWindow(page_frame, orient=HORIZONTAL)
    paned.pack(fill=BOTH, expand=YES, padx=5, pady=5)
    
    left_panel = ttk.Frame(paned, padding=5); paned.add(left_panel, weight=1)
    right_panel = ttk.Frame(paned, padding=5); paned.add(right_panel, weight=2)

    # ESQUERDA
    ttk.Label(left_panel, text="1. Catálogo de Produtos", font=("Segoe UI", 11, "bold")).pack(anchor='w')
    
    fb = ttk.Frame(left_panel); fb.pack(fill=X, pady=5)
    ttk.Label(fb, text="🔍 Buscar:").pack(side=LEFT)
    entry_search_product = ttk.Entry(fb)
    entry_search_product.pack(side=LEFT, fill=X, expand=YES, padx=5)

    btn_frame = ttk.Frame(left_panel); btn_frame.pack(fill=X, pady=5)
    btn_load_cache = ttk.Button(btn_frame, text="📂 Recarregar Cache", bootstyle="secondary")
    btn_load_cache.pack(side=LEFT, fill=X, expand=YES, padx=2)
    btn_update_web = ttk.Button(btn_frame, text="🌐 Baixar Novos", bootstyle="info")
    btn_update_web.pack(side=LEFT, fill=X, expand=YES, padx=2)
    
    cols_prod = ("nome", "preco")
    tree_products = ttk.Treeview(left_panel, columns=cols_prod, show="headings", height=15)
    tree_products.heading("nome", text="Produto"); tree_products.column("nome", width=220)
    tree_products.heading("preco", text="Preço"); tree_products.column("preco", width=80)
    tree_products.pack(fill=BOTH, expand=YES, pady=5)
    
    btn_add_item = ttk.Button(left_panel, text="➡️ Adicionar Item", bootstyle="success")
    btn_add_item.pack(fill=X, pady=5)
    
    # NOVO BOTÃO PARA ITEM MANUAL/SERVIÇO
    btn_add_manual = ttk.Button(left_panel, text="➕ Adicionar Serviço / Manual", bootstyle="warning")
    btn_add_manual.pack(fill=X, pady=2)

    # DIREITA
    ttk.Label(right_panel, text="2. Montagem", font=("Segoe UI", 11, "bold")).pack(anchor='w')
    
    # Atualizado com coluna "cod" antes de Qtd
    cols_orc = ("cod", "qtd", "nome", "vista", "prazo")
    tree_budget = ttk.Treeview(right_panel, columns=cols_orc, show="headings", height=10)
    tree_budget.heading("cod", text="Cód."); tree_budget.column("cod", width=50, anchor="center")
    tree_budget.heading("qtd", text="Qtd"); tree_budget.column("qtd", width=40, anchor="center")
    tree_budget.heading("nome", text="Descrição"); tree_budget.column("nome", width=200)
    tree_budget.heading("vista", text="Unit. Vista"); tree_budget.column("vista", width=90, anchor="e")
    tree_budget.heading("prazo", text="Unit. 10x"); tree_budget.column("prazo", width=90, anchor="e")
    tree_budget.pack(fill=BOTH, expand=YES, pady=5)
    
    btn_remove_item = ttk.Button(right_panel, text="Remover Item", bootstyle="danger-outline")
    btn_remove_item.pack(anchor='e')
    
    # FINALIZAÇÃO
    frame_final_data = ttk.LabelFrame(right_panel, text=" 3. Finalização ", padding=10)
    frame_final_data.pack(fill=X, pady=10)
    
    grid = ttk.Frame(frame_final_data); grid.pack(fill=X)
    ttk.Label(grid, text="Cliente:").grid(row=0, column=0, sticky='w', padx=5)
    entry_client_name = ttk.Entry(grid)
    entry_client_name.grid(row=0, column=1, sticky='ew', padx=5)
    ttk.Label(grid, text="Assinatura:").grid(row=0, column=2, sticky='w', padx=5)
    entry_signature = ttk.Entry(grid)
    entry_signature.grid(row=0, column=3, sticky='ew', padx=5)
    grid.columnconfigure(1, weight=1); grid.columnconfigure(3, weight=1)
    
    # OBSERVAÇÕES INTELIGENTES
    obs_frame = ttk.Frame(frame_final_data)
    obs_frame.pack(fill=X, pady=(10,0))
    ttk.Label(obs_frame, text="Observações:").pack(side=LEFT, padx=5)
    
    var_inst = ttk.BooleanVar(value=False)
    var_comp = ttk.BooleanVar(value=False)
    
    text_observations = ttk.Text(frame_final_data, height=4, font=("Segoe UI", 9))
    text_observations.pack(fill=X, padx=5, pady=5)

    def toggle_obs_text(text, var):
        current_text = text_observations.get("1.0", END).strip()
        if var.get():
            if current_text:
                new_text = current_text + "\n" + text
            else:
                new_text = text
            text_observations.delete("1.0", END)
            text_observations.insert("1.0", new_text)
        else:
            new_text = current_text.replace(text, "").strip()
            new_text = re.sub(r'\n\s*\n', '\n', new_text)
            text_observations.delete("1.0", END)
            text_observations.insert("1.0", new_text)

    chk_inst = ttk.Checkbutton(obs_frame, text="Instalação", variable=var_inst, 
                               command=lambda: toggle_obs_text(TXT_INSTALACAO, var_inst))
    chk_inst.pack(side=RIGHT, padx=5)
    
    chk_comp = ttk.Checkbutton(obs_frame, text="Componentes", variable=var_comp,
                               command=lambda: toggle_obs_text(TXT_COMPONENTES, var_comp))
    chk_comp.pack(side=RIGHT, padx=5)
    
    btn_generate_pdf = ttk.Button(frame_final_data, text="📄 GERAR PDF", bootstyle="primary")
    btn_generate_pdf.pack(fill=X, pady=10)

    # LÓGICA
    local_product_cache = {} 
    current_budget_items = [] 

    def load_data_from_system():
        data = get_all_products_from_cache()
        update_product_tree(data)
        if not data:
            if messagebox.askyesno("Vazio", "Cache vazio. Baixar agora?"): download_from_web()

    def download_from_web():
        def task():
            raw = buscar_produtos_site()
            if raw:
                for p in raw:
                    save_product_to_cache({
                        'link': p.get('link',''), 'nome': p.get('nome','?'),
                        'imagem_url': p.get('imagem_url',''), 
                        'preco_vista': p.get('preco_vista','0'),
                        'preco_prazo': p.get('preco_prazo',''),
                        'cod': p.get('cod', '') 
                    })
            
            db_data = get_all_products_from_cache()

            if raw and db_data:
                map_cods = {x.get('link'): x.get('cod') for x in raw if x.get('link')}
                for prod in db_data:
                    lnk = prod.get('link')
                    if not prod.get('cod') and lnk in map_cods:
                        prod['cod'] = map_cods[lnk]
            
            return db_data

        def on_complete(updated_data):
            btn_update_web.config(state="normal", text="🌐 Baixar Novos")
            entry_search_product.delete(0, END)
            update_product_tree(updated_data)
            messagebox.showinfo("Sucesso", f"{len(updated_data)} itens!")

        btn_update_web.config(state="disabled", text="Buscando...")
        threading.Thread(target=lambda: on_complete(task()), daemon=True).start()

    def update_product_tree(data):
        tree_products.delete(*tree_products.get_children())
        local_product_cache.clear()
        for i, p in enumerate(data):
            uid = str(i)
            local_product_cache[uid] = p
            tree_products.insert("", END, iid=uid, values=(p.get('nome','?'), f"R$ {p.get('preco_vista','?')}"))

    def filter_products(event=None):
        t = entry_search_product.get().lower()
        tree_products.delete(*tree_products.get_children())
        for uid, p in local_product_cache.items():
            if t in p.get('nome','').lower():
                tree_products.insert("", END, iid=uid, values=(p.get('nome','?'), f"R$ {p.get('preco_vista','?')}"))

    def add_item():
        sel = tree_products.selection()
        if not sel: return
        p = local_product_cache[sel[0]]
        
        item = {
            "cod": p.get('cod', ''), 
            "name": p.get('nome',''), "link": p.get('link',''),
            "image_url": p.get('imagem_url',''), "qty": 1,
            "price_cash": p.get('preco_vista',''), "price_install": p.get('preco_prazo','')
        }
        current_budget_items.append(item)
        refresh_budget_tree()

    # --- FUNÇÃO PARA ADICIONAR ITEM MANUAL ---
    def add_manual_item():
        # Cria um diálogo simples para os dados
        d = ttk.Toplevel(page_frame)
        d.title("Adicionar Item Manual / Serviço")
        d.geometry("400x300")
        
        ttk.Label(d, text="Descrição / Serviço:").pack(pady=5)
        e_name = ttk.Entry(d, width=40); e_name.pack()
        e_name.focus_set()
        
        ttk.Label(d, text="Código (Opcional):").pack(pady=5)
        e_cod = ttk.Entry(d, width=20); e_cod.pack()
        
        row_vals = ttk.Frame(d); row_vals.pack(pady=5)
        ttk.Label(row_vals, text="Qtd:").pack(side=LEFT)
        e_qtd = ttk.Entry(row_vals, width=5); e_qtd.pack(side=LEFT, padx=5)
        e_qtd.insert(0, "1")
        
        ttk.Label(row_vals, text="Valor Unit. (R$):").pack(side=LEFT)
        e_price = ttk.Entry(row_vals, width=15); e_price.pack(side=LEFT, padx=5)
        
        def confirm():
            name = e_name.get().strip()
            price = e_price.get().strip()
            if not name or not price:
                messagebox.showwarning("Atenção", "Preencha Nome e Valor")
                return
            
            try: int(e_qtd.get())
            except: 
                messagebox.showwarning("Erro", "Quantidade inválida")
                return

            # Cria item manual. Link vazio e image_url None são importantes para o PDF detectar
            item = {
                "cod": e_cod.get().strip(),
                "name": name,
                "link": "",          # Sem link
                "image_url": None,   # Sem imagem (Sinaliza mesclagem no PDF)
                "qty": e_qtd.get(),
                "price_cash": price,
                "price_install": ""  # Deixa vazio para cálculo automático (15%) ou edita depois
            }
            current_budget_items.append(item)
            refresh_budget_tree()
            d.destroy()
            
        ttk.Button(d, text="Adicionar", command=confirm, bootstyle="success").pack(pady=20)

    def refresh_budget_tree():
        tree_budget.delete(*tree_budget.get_children())
        for index, item in enumerate(current_budget_items):
            tree_budget.insert("", END, iid=str(index), values=(item['cod'], item['qty'], item['name'], item['price_cash'], item['price_install']))

    def edit_budget_item(event):
        sel = tree_budget.selection()
        if not sel: return
        idx = int(sel[0]); item = current_budget_items[idx]
        
        top = ttk.Toplevel(page_frame)
        top.title("Editar"); top.geometry("450x520")
        
        ttk.Label(top, text="Cód:").pack(pady=2)
        ec = ttk.Entry(top); ec.insert(0, item.get('cod','')); ec.pack()
        ttk.Label(top, text="Qtd:").pack(pady=2)
        eq = ttk.Entry(top); eq.insert(0, item['qty']); eq.pack()
        ttk.Label(top, text="Vista:").pack(pady=2)
        ev = ttk.Entry(top); ev.insert(0, item['price_cash']); ev.pack()
        ttk.Label(top, text="Prazo:").pack(pady=2)
        ep = ttk.Entry(top); ep.insert(0, item['price_install']); ep.pack()
        ttk.Label(top, text="Img URL (Vazio para Manual):").pack(pady=2)
        ei = ttk.Entry(top); ei.insert(0, str(item['image_url']) if item['image_url'] else ""); ei.pack()
        
        def save():
            try:
                item['cod'] = ec.get()
                item['qty'] = int(eq.get())
                item['price_cash'] = ev.get()
                item['price_install'] = ep.get()
                
                # Trata imagem vazia
                img_val = ei.get().strip()
                item['image_url'] = img_val if img_val and img_val != 'None' else None
                
                refresh_budget_tree(); top.destroy()
            except: messagebox.showerror("Erro", "Qtd inválida")
        ttk.Button(top, text="Salvar", command=save, bootstyle="success").pack(pady=15)

    def execute_pdf_generation():
        if not current_budget_items: 
            messagebox.showwarning("Aviso", "Adicione produtos.")
            return
        
        base = getattr(sys, '_MEIPASS', os.path.abspath("."))
        pdf_template = os.path.join(base, "assets", "OrçamentoBase.pdf")
        
        out = filedialog.asksaveasfilename(defaultextension=".pdf", title="Salvar")
        if not out: return
        
        obs_raw = text_observations.get("1.0", END).strip()
        obs_list = obs_raw.split('\n') if obs_raw else []
        
        d = {
            "customer": entry_client_name.get(), "signature": entry_signature.get(),
            "observations": obs_list,
            "products": current_budget_items
        }
        gen = BudgetPDFGenerator(pdf_template, out)
        ok, msg = gen.generate(d)
        
        if ok: 
            messagebox.showinfo("Sucesso", msg)
            try: os.startfile(out)
            except: pass
        else: messagebox.showerror("Erro", msg)

    entry_search_product.bind("<KeyRelease>", filter_products)
    btn_load_cache.config(command=load_data_from_system)
    btn_update_web.config(command=download_from_web)
    btn_add_item.config(command=add_item)
    btn_add_manual.config(command=add_manual_item) # Configura novo botão
    btn_remove_item.config(command=lambda: [current_budget_items.pop(int(tree_budget.selection()[0])), refresh_budget_tree()] if tree_budget.selection() else None)
    tree_budget.bind("<Double-1>", edit_budget_item)
    btn_generate_pdf.config(command=execute_pdf_generation)

    page_frame.after(500, load_data_from_system)
    return page_frame