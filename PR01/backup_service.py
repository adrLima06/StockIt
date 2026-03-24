import subprocess
import os
from datetime import datetime
from tkinter import messagebox
from config import DB_CONFIG, MYSQLDUMP_PATH, find_mysqldump

def create_backup():
    print("Iniciando o processo de backup automático...")
    mysqldump_exe = MYSQLDUMP_PATH
    if not os.path.exists(mysqldump_exe):
        print(f"AVISO: Caminho para mysqldump em config.py ('{mysqldump_exe}') não encontrado.")
        mysqldump_exe = find_mysqldump()
        if mysqldump_exe:
            print(f"INFO: mysqldump encontrado em: '{mysqldump_exe}'")
        else:
            messagebox.showerror(
                "Backup Falhou",
                "O executável 'mysqldump.exe' não foi encontrado.\n\n"
                "Por favor, verifique se o MySQL Server está instalado e "
                "configure o caminho correto para 'MYSQLDUMP_PATH' no arquivo 'config.py'."
            )
            print("ERRO: mysqldump.exe não encontrado. Backup cancelado.")
            return False
    backup_dir = os.path.join(os.path.abspath("."), "backups")
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        print(f"Diretório de backups criado em: {backup_dir}")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_file = os.path.join(backup_dir, f"backup_{DB_CONFIG['database']}_{timestamp}.sql")
    command = [
        mysqldump_exe,
        f"--host={DB_CONFIG['host']}",
        f"--user={DB_CONFIG['user']}",
        f"--password={DB_CONFIG['password']}",
        DB_CONFIG['database'],
    ]

    try:
        with open(backup_file, 'w', encoding='utf-8') as f:
            process = subprocess.run(
                command,
                stdout=f,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                check=True
            )
        messagebox.showinfo(
            "Backup Realizado",
            f"Backup do banco de dados concluído com sucesso!\n\nSalvo em: {backup_file}"
        )
        print(f"SUCESSO: Backup criado em {backup_file}")
        return True
    except subprocess.CalledProcessError as e:
        error_message = (
            f"Ocorreu um erro ao executar o mysqldump:\n\n"
            f"Erro: {e.stderr.strip()}\n\n"
            "Verifique as credenciais do banco de dados em 'config.py' e se o usuário tem as permissões necessárias."
        )
        messagebox.showerror("Erro no Backup", error_message)
        print(f"ERRO: {error_message}")
        return False
    except Exception as e:
        messagebox.showerror("Erro Inesperado no Backup", f"Ocorreu um erro inesperado: {e}")
        print(f"ERRO INESPERADO: {e}")
        return False

