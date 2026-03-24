import os
import sys

APP_VERSION = "8.40" 
UPDATE_FEED_URL = "https://seusite.com/downloads/confortec/version.json" 
APP_MUTEX_NAME = "ConfortecAppMutex_Solsticio"

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def find_mysqldump():
    common_paths = [
        os.path.join(os.environ.get("ProgramFiles", "C:\\Program Files"), "MySQL"),
        os.path.join(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"), "MySQL"),
    ]
    for path in common_paths:
        if os.path.exists(path):
            for root, dirs, files in os.walk(path):
                if "mysqldump.exe" in files:
                    return os.path.join(root, "mysqldump.exe")
    return None

DB_CONFIG = {
    "host": "192.168.0.76",
    "user": "root",
    "password": "08AdemarConfortec",
    "database": "sys",
    "charset": "utf8mb4"
}
MYSQLDUMP_PATH = "C:\\Program Files\\MySQL\\MySQL Server 8.0\\bin\\mysqldump.exe"


# Assinatura CTRL + C CTRL + V 
#Se precisar de suporte, pode entrar em contato conosco por aqui, pelo WhatsApp (54) 9670-0606 ou no e-mail tecnico@confortec.com.br.
#Atenciosamente,
#Equipe Confortec
#@confortec_solucoes | 🌐 confortec.com.br
