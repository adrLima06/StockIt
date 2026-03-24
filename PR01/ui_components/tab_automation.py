import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledText
import subprocess
import os
import threading
import queue
import sys
from datetime import datetime
from tkinter import messagebox

# Tenta importar psutil, se não tiver, roda sem os gráficos
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False

automation_process = None
log_queue = queue.Queue()

def create_automation_tab(parent_frame):
    # Layout Principal
    page_frame = ttk.Frame(parent_frame, padding=15)
    
    # Grid Layout: Coluna 0 (Logs) - Coluna 1 (Status/Controle)
    page_frame.columnconfigure(0, weight=3) # Logs ocupam mais espaço
    page_frame.columnconfigure(1, weight=1)
    page_frame.rowconfigure(0, weight=1)

    # --- COLUNA ESQUERDA: LOGS ---
    log_frame = ttk.LabelFrame(page_frame, text=" Monitoramento em Tempo Real ", padding=10, bootstyle="info")
    log_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
    
    # ScrolledText para logs
    log_text = ScrolledText(log_frame, padding=10, hbar=False, autohide=True)
    log_text.pack(fill=BOTH, expand=YES)
    
    # Estilizando o log (aparência de terminal)
    log_text.text.configure(
        state="disabled", 
        font=('Consolas', 10),
        background="#1e1e1e", 
        foreground="#00ff00" # Verde terminal
    )

    # --- COLUNA DIREITA: CONTROLES ---
    side_panel = ttk.Frame(page_frame)
    side_panel.grid(row=0, column=1, sticky="nsew")
    side_panel.columnconfigure(0, weight=1)

    # 1. Card de Tempo
    time_card = ttk.LabelFrame(side_panel, text=" Sistema ", padding=15, bootstyle="secondary")
    time_card.pack(fill=X, pady=(0, 15))
    
    time_label = ttk.Label(time_card, text="--:--:--", font=("Segoe UI", 26, "bold"), anchor=CENTER)
    time_label.pack(fill=X)
    date_label = ttk.Label(time_card, text="...", font=("Segoe UI", 10), anchor=CENTER, bootstyle="secondary")
    date_label.pack(fill=X, pady=(5, 0))

    # 2. Card de Status
    status_card = ttk.LabelFrame(side_panel, text=" Status do Serviço ", padding=15, bootstyle="primary")
    status_card.pack(fill=X, pady=(0, 15))
    
    status_indicator = ttk.Label(status_card, text="● PARADO", font=("Segoe UI", 14, "bold"), bootstyle="danger", anchor=CENTER)
    status_indicator.pack(fill=X, pady=10)

    btn_start = ttk.Button(status_card, text="▶ INICIAR SERVIÇO", bootstyle="success", command=lambda: start_automation())
    btn_start.pack(fill=X, pady=5)
    
    btn_stop = ttk.Button(status_card, text="■ PARAR SERVIÇO", bootstyle="danger", command=lambda: stop_automation(), state="disabled")
    btn_stop.pack(fill=X, pady=5)

    # 3. Card de Performance (Só aparece se tiver psutil)
    if HAS_PSUTIL:
        perf_card = ttk.LabelFrame(side_panel, text=" Performance ", padding=15, bootstyle="warning")
        perf_card.pack(fill=X, pady=(0, 15))
        
        ttk.Label(perf_card, text="Uso de CPU", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        cpu_bar = ttk.Progressbar(perf_card, length=100, bootstyle="warning-striped")
        cpu_bar.pack(fill=X, pady=(5, 15))
        
        ttk.Label(perf_card, text="Uso de Memória", font=("Segoe UI", 9, "bold")).pack(anchor="w")
        mem_bar = ttk.Progressbar(perf_card, length=100, bootstyle="info-striped")
        mem_bar.pack(fill=X, pady=(5, 5))

    # --- FUNÇÕES ---
    def update_log_display():
        """Lê a fila de logs e atualiza a tela sem travar a UI"""
        try:
            while not log_queue.empty():
                msg = log_queue.get_nowait()
                log_text.text.configure(state="normal")
                log_text.insert(END, msg)
                log_text.see(END) # Auto-scroll
                log_text.text.configure(state="disabled")
        except: pass
        page_frame.after(100, update_log_display)

    def reader_thread(process_stdout):
        """Thread separada para ler o output do processo"""
        for line in iter(process_stdout.readline, ''):
            log_queue.put(line)
        process_stdout.close()

    def update_ui_state():
        global automation_process
        is_running = automation_process and automation_process.poll() is None
        
        if is_running:
            status_indicator.config(text="● EM EXECUÇÃO", bootstyle="success")
            btn_start.config(state="disabled")
            btn_stop.config(state="normal")
        else:
            status_indicator.config(text="● PARADO", bootstyle="danger")
            btn_start.config(state="normal")
            btn_stop.config(state="disabled")
        
        # Atualiza relógio
        now = datetime.now()
        time_label.config(text=now.strftime("%H:%M:%S"))
        date_label.config(text=now.strftime("%A, %d/%m/%Y").title())

        # Atualiza Stats
        if HAS_PSUTIL:
            try:
                cpu_bar['value'] = psutil.cpu_percent()
                mem_bar['value'] = psutil.virtual_memory().percent
            except: pass
            
        page_frame.after(1000, update_ui_state)

    def start_automation():
        global automation_process
        if automation_process and automation_process.poll() is None:
            return
        
        # Limpa log
        log_text.text.configure(state="normal")
        log_text.delete('1.0', END)
        log_text.insert('1.0', ">>> Inicializando sistema de automação...\n")
        log_text.text.configure(state="disabled")
        
        try:
            # Detecta como rodar (se é .exe ou .py)
            if getattr(sys, 'frozen', False):
                cmd = [sys.executable, "--run-automation"]
            else:
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # Sobe para APP-2.00
                main_script = os.path.join(base_dir, 'main_app.py')
                cmd = [sys.executable, "-u", main_script, "--run-automation"]
            
            log_queue.put(f"Executando: {' '.join(cmd)}\n")
            
            # Cria processo sem janela (CREATE_NO_WINDOW) para não pipocar terminal
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
            automation_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                startupinfo=startupinfo,
                encoding='utf-8', 
                errors='replace'
            )
            
            # Inicia thread de leitura
            t = threading.Thread(target=reader_thread, args=(automation_process.stdout,))
            t.daemon = True
            t.start()
            
        except Exception as e:
            messagebox.showerror("Erro Crítico", f"Falha ao iniciar processo:\n{e}")

    def stop_automation():
        global automation_process
        if automation_process:
            automation_process.terminate()
            log_queue.put("\n>>> Processo encerrado pelo usuário.\n")

    # Inicialização
    update_ui_state()
    update_log_display()
    
    return page_frame