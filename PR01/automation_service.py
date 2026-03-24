import time
import pymysql
import pywhatkit as kit
import pyautogui
import pygetwindow as gw
from datetime import datetime, timedelta, date
import os
import traceback
from database import get_db_connection
pyautogui.FAILSAFE = False
def log(message):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] [AUTO] {message}")
def registrar_envio(cursor, entity_id, entity_type, dias_key):
    try:
        final_key = dias_key
        if entity_type == 'ANIVERSARIO':
             final_key = int(f"{datetime.now().year}{dias_key}")
        
        cursor.execute("INSERT INTO mensagens_enviadas (entity_id, entity_type, dias_key, data_envio) VALUES (%s, %s, %s, %s)", 
                       (entity_id, entity_type, final_key, datetime.now()))
    except: pass
def mensagem_ja_enviada(cursor, entity_id, entity_type, dias_key):
    try:
        final_key = dias_key
        if entity_type == 'ANIVERSARIO':
             final_key = int(f"{datetime.now().year}{dias_key}")
        cursor.execute("SELECT COUNT(*) as c FROM mensagens_enviadas WHERE entity_id=%s AND entity_type=%s AND dias_key=%s", (entity_id, entity_type, final_key))
        return cursor.fetchone()['c'] > 0
    except: return True
def formatar_telefone_br(telefone):
    if not telefone: return None
    nums = ''.join(filter(str.isdigit, str(telefone)))
    if len(nums) < 10: return None
    if not nums.startswith('55') or len(nums) <= 11: nums = '55' + nums
    return f"+{nums}"
def enviar_mensagem_com_seguranca(telefone, mensagem, caminho_imagem=None, skip_event=None):
    try:
        fone_fmt = formatar_telefone_br(telefone)
        if not fone_fmt: return False
        
        log(f"Enviando para {fone_fmt}...")
        if caminho_imagem and os.path.exists(caminho_imagem):
            kit.sendwhats_image(fone_fmt, caminho_imagem, caption=mensagem, wait_time=20, tab_close=False)
        else:
            kit.sendwhatmsg_instantly(fone_fmt, mensagem, wait_time=15, tab_close=False)
        for _ in range(5):
            if skip_event and skip_event.is_set():
                log("Envio pulado pelo usuário.")
                return False
            time.sleep(1)
        try:
            win = gw.getWindowsWithTitle('WhatsApp')
            if win: win[0].activate()
        except: pass
        pyautogui.press("enter")
        time.sleep(3)
        pyautogui.hotkey('ctrl', 'w')
        return True
    except Exception as e:
        log(f"Erro envio: {e}")
        return False
def calcular_data_alvo(data_base, dias_apos, eh_aniversario=False):
    if not data_base: return None
    hoje = datetime.now().date()
    if isinstance(data_base, str):
        try: data_base = datetime.strptime(data_base, '%Y-%m-%d').date()
        except: 
            try: data_base = datetime.strptime(data_base, '%d/%m/%Y').date()
            except: return None
    if eh_aniversario:
        try: 
            data_alvo = date(hoje.year, data_base.month, data_base.day)
        except ValueError: 
            data_alvo = date(hoje.year, 3, 1)
    else:
        if isinstance(data_base, datetime): data_base = data_base.date()
        data_alvo = data_base + timedelta(days=dias_apos)
    ds = data_alvo.weekday()
    if ds == 5: data_alvo += timedelta(days=2)
    elif ds == 6: data_alvo += timedelta(days=1)
    return data_alvo
def processar_regras():
    conn = get_db_connection()
    if not conn: return
    hoje = datetime.now().date()
    limite_passado = hoje - timedelta(days=3)
    try:
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute("SELECT * FROM automacao_mensagens")
            regras = cursor.fetchall()
            if not regras: return
            cursor.execute("SELECT id, nome, telefone, grupo, data_cadastro as dt FROM leads")
            leads = cursor.fetchall()
            cursor.execute("SELECT id, nome, telefone, grupo, data_compra as dt FROM compras_detalhadas")
            compras = cursor.fetchall()
            cursor.execute("SELECT id, nome, whatsapp as telefone, grupo, data_cadastro, data_nascimento FROM clientes")
            clientes = cursor.fetchall()
            for r in regras:
                tipo, grupo, dias, msg, img = r['tipo_entidade'], r['grupo'], r['dias_apos'], r['texto_mensagem'], r['caminho_imagem']
                lista, eh_niver = [], False
                if tipo == 'LEAD': 
                    lista = [x for x in leads if x['grupo']==grupo]
                elif tipo == 'COMPRA': 
                    lista = [x for x in compras if x['grupo']==grupo]
                elif tipo == 'CLIENTE_CAD': 
                    lista = [x for x in clientes if x['grupo']==grupo]
                    for c in lista: c['dt'] = c['data_cadastro']
                elif tipo == 'ANIVERSARIO':
                    lista = [x for x in clientes if x['grupo']==grupo]
                    for c in lista: c['dt'] = c['data_nascimento']
                    eh_niver = True
                for p in lista:
                    if not p.get('dt'): continue
                    alvo = calcular_data_alvo(p['dt'], dias, eh_niver)
                    if alvo and (limite_passado <= alvo <= hoje):
                        if mensagem_ja_enviada(cursor, p['id'], tipo, dias): continue
                        nome = p['nome'].split()[0] if p['nome'] else "Cliente"
                        msg_final = msg.replace("{nome}", nome)
                        log(f"Processando pendência de {alvo}: {nome}")
                        if enviar_mensagem_com_seguranca(p['telefone'], msg_final, img):
                            registrar_envio(cursor, p['id'], tipo, dias)
                            conn.commit()
    except Exception as e: log(f"Erro Loop: {e}")
    finally: conn.close()
def main_loop():
    log("Serviço Iniciado (Modo Diário).")
    while True:
        now = datetime.now()
        if now.weekday() < 5 and 8 <= now.hour < 19:
            processar_regras()
            time.sleep(900)
        else: 
            time.sleep(3600)
if __name__ == "__main__": main_loop()