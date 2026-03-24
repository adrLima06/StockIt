import io
import os
import requests
from datetime import datetime
import locale
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import black
from pypdf import PdfReader, PdfWriter

try:
    locale.setlocale(locale.LC_TIME, 'pt_BR.utf8')
    locale.setlocale(locale.LC_MONETARY, 'pt_BR.utf8')
except:
    try:
        locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil')
        locale.setlocale(locale.LC_MONETARY, 'Portuguese_Brazil')
    except:
        pass

class BudgetPDFGenerator:
    def __init__(self, base_pdf_path, output_path):
        self.base_pdf_path = base_pdf_path
        self.output_path = output_path
        self.packet = io.BytesIO()
        self.c = canvas.Canvas(self.packet, pagesize=A4)
        self.width, self.height = A4
        self.coords = {
            "date": (650, 780),           # Data no topo
            "customer_name": (120, 750),  # Nome do Cliente
            "signature": (400, 100),      # Assinatura
            
            # Produtos (Lista)
            "prod_start_y": 600,          # Altura onde começa o primeiro produto
            "prod_line_gap": 110,         # Espaço vertical entre produtos
            
            # Colunas do Produto (X)
            "col_img": 60,                # Imagem
            "col_desc": 160,              # Descrição
            "col_qty": 400,               # Quantidade
            "col_price_cash": 450,        # Valor à vista
            "col_price_inst": 520,        # Valor parcelado
            
            # Observações
            "obs_start_y": 200,           # Altura onde começam as obs
            "obs_line_gap": 15            # Espaçamento entre linhas de obs
        }
    def draw_text(self, text, x, y, font="Helvetica", size=10, color=black):
        self.c.setFillColor(color)
        self.c.setFont(font, size)
        self.c.drawString(x, y, str(text))
    def draw_multiline_text(self, text, x, y, width=200, font="Helvetica", size=9):
        text_obj = self.c.beginText(x, y)
        text_obj.setFont(font, size)
        import textwrap
        lines = textwrap.wrap(text, width=40) 
        for line in lines:
            text_obj.textLine(line)
        self.c.drawText(text_obj)
    def draw_image_from_url(self, url, x, y, width=50, height=50):
        try:
            response = requests.get(url, stream=True, timeout=5)
            if response.status_code == 200:
                img = ImageReader(io.BytesIO(response.content))
                self.c.drawImage(img, x, y, width=width, height=height, mask='auto', preserveAspectRatio=True)
            else:
                self.draw_text("[Img Erro]", x, y)
        except Exception as e:
            print(f"Erro ao baixar imagem: {e}")
            self.draw_text("[Sem Img]", x, y)
    def _parse_currency(self, value_str):
        if isinstance(value_str, (int, float)):
            return float(value_str)
        try:
            clean = clean.replace('.', '').replace(',', '.')
            return float(clean)
        except (ValueError, AttributeError):
            return 0.0
    def _format_currency(self, value):
        try:
            return locale.currency(value, grouping=True, symbol=True)
        except:
            return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    def generate_budget_pdf(self, budget_data):
        self.draw_text(budget_data.get('date', datetime.now().strftime('%d/%m/%Y')), *self.coords['date'])
        self.draw_text(budget_data.get('client_name', ''), *self.coords['customer_name'], size=12)
        products = budget_data.get('products', [])
        current_y = self.coords['prod_start_y']
        total_cash = 0.0
        total_installments = 0.0
        for prod in products:
            desc = prod.get('description', '')
            qty = prod.get('quantity', 1)
            price_cash_raw = prod.get('price_cash', 0)
            price_inst_raw = prod.get('price_installments', 0)
            img_url = prod.get('image_url', '')
            val_cash = self._parse_currency(price_cash_raw)
            val_inst = self._parse_currency(price_inst_raw)
            if val_inst == 0 and val_cash > 0:
                val_inst = val_cash
            total_cash += val_cash
            total_installments += val_inst
            if img_url:
                self.draw_image_from_url(img_url, self.coords['col_img'], current_y - 10, width=50, height=50)
            
            self.draw_multiline_text(desc, self.coords['col_desc'], current_y + 20)
            self.draw_text(str(qty), self.coords['col_qty'], current_y + 20)
            self.draw_text(str(price_cash_raw), self.coords['col_price_cash'], current_y + 20)
            self.draw_text(str(price_inst_raw), self.coords['col_price_inst'], current_y + 20)
            current_y -= self.coords['prod_line_gap']
        total_y = current_y + 40 
        self.c.setFont("Helvetica-Bold", 11)
        self.c.drawString(self.coords['col_qty'], total_y, "TOTAL")
        self.c.drawString(self.coords['col_price_cash'], total_y, self._format_currency(total_cash))
        self.c.drawString(self.coords['col_price_inst'], total_y, self._format_currency(total_installments))
        obs_text = budget_data.get('observations', '')
        if obs_text:
            obs_y = self.coords['obs_start_y']
            self.draw_multiline_text(obs_text, 120, obs_y, width=60)

        self.c.save()
        self.packet.seek(0)
        try:
            new_pdf = PdfReader(self.packet)
            base_pdf = PdfReader(self.base_pdf_path)
            output = PdfWriter()
            page = base_pdf.pages[0]
            page.merge_page(new_pdf.pages[0])
            output.add_page(page)
            with open(self.output_path, "wb") as f_out:
                output.write(f_out)
            return True, "PDF gerado com sucesso!"
        except Exception as e:
            return False, f"Erro ao mesclar/salvar PDF: {str(e)}"