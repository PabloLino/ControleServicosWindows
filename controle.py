import subprocess
import json
import os

PREFIXO = "CntrlRClone_"

def listar_servicos():
    """
    Retorna lista de serviços do Windows com 'extradigital' no nome ou display,
    no formato: ([{...}], aviso)
    """
    try:
        cmd = [
            "powershell",
            "-Command",
            "[Console]::OutputEncoding = [System.Text.Encoding]::UTF8; "
            "Get-WmiObject -Class Win32_Service | Select-Object Name,DisplayName | ConvertTo-Json"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if result.returncode != 0 or not result.stdout:
            return [], "Falha ao buscar serviços. Tente rodar como administrador."
        servicos_json = json.loads(result.stdout)
        if isinstance(servicos_json, dict):
            servicos_json = [servicos_json]
        servicos = []
        for svc in servicos_json:
            display = svc.get("DisplayName", "").strip()
            name = svc.get("Name", "").strip()
            if "extradigital" in display.lower() or "extradigital" in name.lower():
                servicos.append({'DisplayName': display, 'Name': name})
        if not servicos:
            return [], "Nenhum serviço 'extradigital' foi encontrado"
        return servicos, None
    except Exception as e:
        return [], f"Tente rodar como administrador.\n\nDetalhe: {e}"

def agendar_tarefa(service_name, hora_ini, min_ini, hora_fim, min_fim):
    intervalo = 2
    ini_str = f"{hora_ini:02d}:{min_ini:02d}"
    fim_str = f"{hora_fim:02d}:{min_fim:02d}"

    task_parar = f"{PREFIXO}Parar_{service_name.replace(' ', '_')}"
    task_iniciar = f"{PREFIXO}Iniciar_{service_name.replace(' ', '_')}"
    task_monitorar_parar1 = f"{PREFIXO}Monitorar_Parada1_{service_name.replace(' ', '_')}"
    task_monitorar_parar2 = f"{PREFIXO}Monitorar_Parada2_{service_name.replace(' ', '_')}"
    task_monitorar_IniciarDia1 = f"{PREFIXO}Monitorar_InicioDia1_{service_name.replace(' ', '_')}"
    task_monitorar_IniciarDia2 = f"{PREFIXO}Monitorar_InicioDia2_{service_name.replace(' ', '_')}"
    task_start_wknd = f"{PREFIXO}StartFds_{service_name.replace(' ', '_')}"

    quoted_name = service_name

    comandos = [
        f'schtasks /create /f /tn "{task_parar}" /tr "cmd.exe /c net stop \\"{quoted_name}\\"" /sc weekly /d MON,TUE,WED,THU,FRI /st {ini_str}',
        f'schtasks /create /f /tn "{task_iniciar}" /tr "cmd.exe /c net start \\"{quoted_name}\\"" /sc weekly /d MON,TUE,WED,THU,FRI /st {fim_str}',
        *( [
            f'schtasks /create /f /tn "{task_monitorar_parar1}" /tr "cmd.exe /c net stop \\"{quoted_name}\\"" /sc minute /mo {intervalo} /st {ini_str} /et {fim_str}'
        ] if hora_ini < hora_fim or (hora_ini == hora_fim and min_ini < min_fim) else [
            f'schtasks /create /f /tn "{task_monitorar_parar1}" /tr "cmd.exe /c net stop \\"{quoted_name}\\"" /sc minute /mo {intervalo} /st {ini_str} /et 23:59',
            f'schtasks /create /f /tn "{task_monitorar_parar2}" /tr "cmd.exe /c net stop \\"{quoted_name}\\"" /sc minute /mo {intervalo} /st 00:00 /et {fim_str}',
        ] ),
        f'schtasks /create /f /tn "{task_monitorar_IniciarDia1}" /tr "cmd.exe /c net start \\"{quoted_name}\\"" /sc minute /mo {intervalo} /st {fim_str} /et 23:59',
        f'schtasks /create /f /tn "{task_monitorar_IniciarDia2}" /tr "cmd.exe /c net start \\"{quoted_name}\\"" /sc minute /mo {intervalo} /st 00:00 /et {ini_str}',
        f'schtasks /create /f /tn "{task_start_wknd}" /tr "cmd.exe /c net start \\"{quoted_name}\\"" /sc weekly /d SAT,SUN /st 00:01',
    ]

    try:
        for cmd in comandos:
            subprocess.check_call(cmd, shell=True)
        return (
            "Agendamento criado com sucesso!\n\n"
            f"Segunda a sexta:\n  Inativo de {ini_str} até {fim_str}.\n"
            f"Sábado e Domingo:\n  Serviço sempre ATIVO (será iniciado automaticamente às 00:01)."
        )
    except Exception as e:
        raise Exception(f"Falha ao criar tarefas agendadas: {e}")
