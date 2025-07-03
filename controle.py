import subprocess
import json
import re

PREFIXO = "EDBO_"

def listar_servicos():
    try:
        cmd = [
            "powershell",
            "-Command",
            "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; Get-WmiObject -Class Win32_Service | Select-Object Name,DisplayName | ConvertTo-Json"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if result.returncode != 0 or not result.stdout:
            raise Exception(result.stderr if result.stderr else "Sem saída do PowerShell")
        servicos_json = json.loads(result.stdout)
        if isinstance(servicos_json, dict):
            servicos_json = [servicos_json]
        servicos = []
        for svc in servicos_json:
            display = svc.get("DisplayName", "").strip()
            name = svc.get("Name", "").strip()
            if "backup" in display.lower() or "backup" in name.lower():
                servicos.append(f"{display} ({name})")
        servicos.sort(key=lambda x: x.lower())
        return servicos
    except Exception as e:
        raise Exception(
            f"Não foi possível listar os serviços (Display Name).\n"
            f"Tente rodar como administrador.\n\nDetalhe: {e}"
        )

def extrair_service_name(combo_value):
    match = re.match(r".*\(([^)]+)\)\s*$", combo_value)
    return match.group(1) if match else combo_value

def agendar_tarefa(service_combo, hora_ini, min_ini, hora_fim, min_fim):
    service_name = extrair_service_name(service_combo)
    intervalo = 2
    task_parar = f"{PREFIXO}Parar_" + service_name.replace(" ", "_")
    task_iniciar = f"{PREFIXO}Iniciar_" + service_name.replace(" ", "_")
    task_monitor = f"{PREFIXO}Monitorar_Parada_" + service_name.replace(" ", "_")
    task_start_wknd = f"{PREFIXO}StartFds_" + service_name.replace(" ", "_")

    comando_parar = (
        f'schtasks /create /f /tn "{task_parar}" /tr '
        f'"cmd.exe /c net stop \\"{service_name}\\"" '
        f'/sc weekly /d MON,TUE,WED,THU,FRI /st {hora_ini:02d}:{min_ini:02d}'
    )
    comando_iniciar = (
        f'schtasks /create /f /tn "{task_iniciar}" /tr '
        f'"cmd.exe /c net start \\"{service_name}\\"" '
        f'/sc weekly /d MON,TUE,WED,THU,FRI /st {hora_fim:02d}:{min_fim:02d}'
    )
    comando_monitor = (
        f'schtasks /create /f /tn "{task_monitor}" /tr '
        f'"cmd.exe /c net stop \\"{service_name}\\"" '
        f'/sc weekly /d MON,TUE,WED,THU,FRI /mo {intervalo} /st {hora_ini:02d}:{min_ini:02d} /et {hora_fim:02d}:{min_fim:02d}'
    )
    comando_start_wknd = (
        f'schtasks /create /f /tn "{task_start_wknd}" /tr '
        f'"cmd.exe /c net start \\"{service_name}\\"" '
        f'/sc weekly /d SAT,SUN /st 00:01'
    )

    try:
        remover_agendamentos(service_combo)

        subprocess.check_call(comando_parar, shell=True)
        subprocess.check_call(comando_iniciar, shell=True)
        subprocess.check_call(comando_monitor, shell=True)
        subprocess.check_call(comando_start_wknd, shell=True)

        return (
            "Agendamento criado com sucesso!\n\n"
            f"Segunda a sexta:\n  Inativo de {hora_ini:02d}:{min_ini:02d} até {hora_fim:02d}:{min_fim:02d}\n"
            f"Sábado e Domingo:\n  Serviço sempre ATIVO (será iniciado automaticamente às 00:01)"
        )
    except Exception as e:
        raise Exception(f"Falha ao criar tarefas agendadas: {e}")

def remover_agendamentos(service_combo):
    service_name = extrair_service_name(service_combo)
    task_parar = f"{PREFIXO}Parar_" + service_name.replace(" ", "_")
    task_iniciar = f"{PREFIXO}Iniciar_" + service_name.replace(" ", "_")
    task_monitor = f"{PREFIXO}Monitorar_Parada_" + service_name.replace(" ", "_")
    task_start_wknd = f"{PREFIXO}StartFds_" + service_name.replace(" ", "_")
    erros = []
    for tarefa in [task_parar, task_iniciar, task_monitor, task_start_wknd]:
        comando = f'schtasks /delete /f /tn "{tarefa}"'
        result = subprocess.run(comando, shell=True, capture_output=True, text=True, encoding="utf-16le", errors="replace")
        if result.returncode != 0 and "não existe" not in (result.stdout or "").lower() and "does not exist" not in (result.stdout or "").lower():
            erros.append(f"{tarefa}: {result.stdout or result.stderr}")
    if erros:
        raise Exception("Algumas tarefas podem não ter sido removidas:\n\n" + "\n".join(erros))
    return "Todos os agendamentos para este serviço foram removidos!"
