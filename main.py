import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import re

PREFIXO = "EDBO_"

def listar_servicos():
    try:
        palavras = ['extradigital', 'backup', 'online']
        cmd = [
            "powershell",
            "-Command",
            "Get-WmiObject -Class Win32_Service | Select-Object Name,DisplayName | ConvertTo-Json"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0 or not result.stdout:
            raise Exception(result.stderr if result.stderr else "Sem saída do PowerShell")
        import json
        servicos_json = json.loads(result.stdout)
        if isinstance(servicos_json, dict):
            servicos_json = [servicos_json]
        servicos = []
        for svc in servicos_json:
            display = svc.get("DisplayName", "").strip()
            name = svc.get("Name", "").strip()
            dados = f"{display} ({name})"
            lower_display = display.lower()
            lower_name = name.lower()
            if any(p in lower_display or p in lower_name for p in palavras):
                servicos.append(dados)
        servicos.sort()
        return servicos
    except Exception as e:
        messagebox.showerror(
            "Erro",
            f"Não foi possível listar os serviços (Display Name).\n\n"
            f"Tente rodar como administrador.\n\nDetalhe: {e}"
        )
        return []

def extrair_service_name(combo_value):
    match = re.match(r".*\(([^)]+)\)\s*$", combo_value)
    return match.group(1) if match else combo_value

def agendar_tarefa(service_combo, hora_inativo_ini, hora_inativo_fim):
    service_name = extrair_service_name(service_combo)
    intervalo = 2
    task_parar = f"{PREFIXO}Parar_" + service_name.replace(" ", "_")
    task_iniciar = f"{PREFIXO}Iniciar_" + service_name.replace(" ", "_")
    task_monitor = f"{PREFIXO}Monitorar_Parada_" + service_name.replace(" ", "_")

    comando_parar = (
        f'schtasks /create /f /tn "{task_parar}" /tr '
        f'"cmd.exe /c net stop \\"{service_name}\\"" /sc daily /st {hora_inativo_ini:02d}:00'
    )
    comando_iniciar = (
        f'schtasks /create /f /tn "{task_iniciar}" /tr '
        f'"cmd.exe /c net start \\"{service_name}\\"" /sc daily /st {hora_inativo_fim:02d}:00'
    )
    comando_monitor = (
        f'schtasks /create /f /tn "{task_monitor}" /tr '
        f'"cmd.exe /c net stop \\"{service_name}\\"" '
        f'/sc minute /mo {intervalo} /st {hora_inativo_ini:02d}:00 /et {hora_inativo_fim:02d}:00'
    )

    try:
        subprocess.check_call(comando_parar, shell=True)
        subprocess.check_call(comando_iniciar, shell=True)
        subprocess.check_call(comando_monitor, shell=True)
        messagebox.showinfo(
            "Sucesso",
            f"Agendamento criado com sucesso!\n\n"
            f"Serviço INATIVO de {hora_inativo_ini:02d}:00 até {hora_inativo_fim:02d}:00\n"
            f"(Monitoramento ativo a cada {intervalo} minutos neste intervalo)"
        )
    except Exception as e:
        messagebox.showerror("Erro", f"Falha ao criar tarefas agendadas: {e}")

def remover_agendamentos(service_combo):
    service_name = extrair_service_name(service_combo)
    task_parar = f"{PREFIXO}Parar_" + service_name.replace(" ", "_")
    task_iniciar = f"{PREFIXO}Iniciar_" + service_name.replace(" ", "_")
    task_monitor = f"{PREFIXO}Monitorar_Parada_" + service_name.replace(" ", "_")
    erros = []
    for tarefa in [task_parar, task_iniciar, task_monitor]:
        comando = f'schtasks /delete /f /tn "{tarefa}"'
        result = subprocess.run(comando, shell=True, capture_output=True, text=True)
        if result.returncode != 0 and "não existe" not in result.stdout.lower() and "does not exist" not in result.stdout.lower():
            erros.append(f"{tarefa}: {result.stdout or result.stderr}")
    if erros:
        messagebox.showwarning("Atenção", f"Algumas tarefas podem não ter sido removidas:\n\n" + "\n".join(erros))
    else:
        messagebox.showinfo("Pronto", "Todos os agendamentos para este serviço foram removidos!")

def on_submit():
    service = combo_servico.get().strip()
    try:
        hora_ini = int(combo_hora_ini.get())
        hora_fim = int(combo_hora_fim.get())
        if not service:
            raise ValueError("Selecione o serviço na lista.")
        if hora_ini == hora_fim:
            raise ValueError("O intervalo não pode ser nulo (horas iguais)")
    except Exception as e:
        messagebox.showerror("Erro", f"Verifique os dados:\n{e}")
        return
    agendar_tarefa(service, hora_ini, hora_fim)

def on_remover():
    service = combo_servico.get().strip()
    if not service:
        messagebox.showerror("Erro", "Selecione o serviço na lista.")
        return
    if messagebox.askyesno("Remover agendamentos", "Deseja remover todos os agendamentos criados para este serviço?"):
        remover_agendamentos(service)

# =========INTERFACE========== #
root = tk.Tk()
root.title("Agendamento de Serviço Windows")
root.geometry("430x285")
root.resizable(False, False)

style = ttk.Style(root)
style.theme_use('clam')

frame = ttk.Frame(root, padding=16)
frame.pack(expand=True, fill='both')

lbl_titulo = tk.Label(frame, text="Agendamento Automático de Serviço", font=("Segoe UI", 12, "bold"))
lbl_titulo.grid(row=0, column=0, columnspan=2, pady=(2,14))

ttk.Label(frame, text="Selecione o Serviço:", font=("Segoe UI", 10)).grid(row=1, column=0, sticky='e', pady=3)
servicos_disponiveis = listar_servicos()
combo_servico = ttk.Combobox(frame, values=servicos_disponiveis, width=32, state="readonly", font=("Segoe UI", 10))
combo_servico.grid(row=1, column=1, padx=8, pady=3, sticky="w")

ttk.Label(frame, text="Defina o intervalo em que o serviço ficará INATIVO:", font=("Segoe UI", 9, "italic")).grid(
    row=2, column=0, columnspan=2, pady=(8,3), sticky="w")

ttk.Label(frame, text="Início do intervalo (hora):", font=("Segoe UI", 10)).grid(row=3, column=0, sticky='e', pady=2)
combo_hora_ini = ttk.Combobox(frame, values=[f"{h:02d}" for h in range(24)], width=5, state="readonly", font=("Segoe UI", 10))
combo_hora_ini.current(8)
combo_hora_ini.grid(row=3, column=1, sticky='w', padx=8, pady=2)

ttk.Label(frame, text="Fim do intervalo (hora):", font=("Segoe UI", 10)).grid(row=4, column=0, sticky='e', pady=2)
combo_hora_fim = ttk.Combobox(frame, values=[f"{h:02d}" for h in range(24)], width=5, state="readonly", font=("Segoe UI", 10))
combo_hora_fim.current(18)
combo_hora_fim.grid(row=4, column=1, sticky='w', padx=8, pady=2)

btn = tk.Button(frame, text="Agendar Serviço", command=on_submit,
                font=("Segoe UI", 10, "bold"),
                bg="#0078d7", fg="white", height=1, relief="flat", borderwidth=0,
                activebackground="#005ea6", activeforeground="white", padx=2, pady=2)
btn.grid(row=5, column=0, pady=(16,4), sticky="e", ipadx=7, ipady=2)

btn_remover = tk.Button(frame, text="Remover Todos Agendamentos", command=on_remover,
                       font=("Segoe UI", 9, "bold"),
                       bg="#e74c3c", fg="white", height=1, relief="flat", borderwidth=0,
                       activebackground="#c0392b", activeforeground="white", padx=2, pady=2)
btn_remover.grid(row=5, column=1, pady=(16,4), sticky="w", ipadx=7, ipady=2)

root.update_idletasks()
width = root.winfo_width()
height = root.winfo_height()
x = (root.winfo_screenwidth() // 2) - (width // 2)
y = (root.winfo_screenheight() // 2) - (height // 2)
root.geometry(f'{width}x{height}+{x}+{y}')

root.mainloop()
