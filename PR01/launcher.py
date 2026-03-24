import os
import sys
import subprocess
import time
import requests
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from threading import Thread
from tkinter import messagebox

URL_VERSION = "https://github.com/Confortec/confortec_update/releases/latest/download/version.txt"
URL_EXE = "https://github.com/Confortec/confortec_update/releases/latest/download/confortec_system.exe"

MAIN_APP_NAME = "confortec_system.exe"
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TXT_PATH = os.path.join(BASE_DIR, "version.txt")
EXE_PATH = os.path.join(BASE_DIR, MAIN_APP_NAME)
TEMP_PATH = os.path.join(BASE_DIR, "new_version.tmp")

class LauncherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Confortec Launcher")
        self.root.geometry("450x300")
        self.root.overrideredirect(True)
        ws = self.root.winfo_screenwidth()
        hs = self.root.winfo_screenheight()
        x = (ws/2) - (450/2)
        y = (hs/2) - (300/2)
        self.root.geometry('+%d+%d' % (x, y))
        main_frame = ttk.Frame(root, padding=20)
        main_frame.pack(fill=BOTH, expand=YES)
        ttk.Label(main_frame, text="CONFORTEC", font=("Segoe UI", 24, "bold"), bootstyle="success").pack(pady=(10,5))
        self.lbl_info = ttk.Label(main_frame, text="Conectando ao GitHub...", font=("Segoe UI", 10))
        self.lbl_info.pack(pady=5)
        self.lbl_status = ttk.Label(main_frame, text="Aguarde...", bootstyle="secondary")
        self.lbl_status.pack(pady=10)
        self.progress = ttk.Progressbar(main_frame, length=350, mode='indeterminate', bootstyle="success-striped")
        self.progress.pack(pady=10)
        self.progress.start(10)
        Thread(target=self.start_process, daemon=True).start()

    def download_file(self, url, destination):
        response = requests.get(url, stream=True)
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024 * 1024 
        wrote = 0
        with open(destination, 'wb') as f:
            for chunk in response.iter_content(block_size):
                if chunk:
                    wrote += len(chunk)
                    f.write(chunk)
                    if total_size > 0:
                        percent = (wrote / total_size) * 100
                        self.root.after(0, lambda p=percent: self.progress.config(value=p))
                        mb_lido = wrote / (1024*1024)
                        mb_total = total_size / (1024*1024)
                        self.root.after(0, lambda t=f"Baixando: {mb_lido:.1f}MB / {mb_total:.1f}MB": self.lbl_status.config(text=t))
    def get_local_version(self):
        if os.path.exists(TXT_PATH):
            try:
                with open(TXT_PATH, "r") as f:
                    return f.read().strip()
            except: pass
        return "0.00"
    def start_process(self):
        try:
            self.lbl_status.config(text="Verificando versão...")
            local_ver = self.get_local_version()
            try:
                resp = requests.get(URL_VERSION, timeout=10)
                if resp.status_code == 200:
                    remote_ver = resp.text.strip()
                    if remote_ver > local_ver:
                        self.perform_update(remote_ver)
                    else:
                        self.launch_system()
                else:
                    self.launch_system()
            except:
                self.launch_system()
        except Exception as e:
            self.launch_system()
    def perform_update(self, new_version):
        self.root.after(0, lambda: self.progress.stop())
        self.root.after(0, lambda: self.progress.config(mode='determinate'))
        self.root.after(0, lambda: self.lbl_info.config(text=f"Nova versão {new_version} encontrada!"))
        try:
            self.download_file(URL_EXE, TEMP_PATH)
            if os.path.getsize(TEMP_PATH) < 100 * 1024:
                raise Exception("Arquivo muito pequeno.")
            self.root.after(0, lambda: self.lbl_status.config(text="Instalando atualização..."))
            time.sleep(2)
            if os.path.exists(EXE_PATH):
                os.remove(EXE_PATH)
            os.rename(TEMP_PATH, EXE_PATH)
            with open(TXT_PATH, "w") as f:
                f.write(new_version)
            messagebox.showinfo("Sucesso", f"Atualizado para versão {new_version} via GitHub!")
            self.launch_system()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha no download:\n{e}")
            if os.path.exists(TEMP_PATH):
                try: os.remove(TEMP_PATH)
                except: pass
            self.launch_system()
    def launch_system(self):
        self.root.after(0, lambda: self.lbl_status.config(text="Iniciando..."))
        time.sleep(1)
        if os.path.exists(EXE_PATH):
            subprocess.Popen([EXE_PATH], cwd=BASE_DIR)
            self.root.destroy()
            sys.exit()
        else:
            messagebox.showerror("Erro", "Sistema principal não encontrado.")
            sys.exit()
if __name__ == "__main__":
    app_root = ttk.Window(themename="litera")
    LauncherApp(app_root)
    app_root.mainloop()