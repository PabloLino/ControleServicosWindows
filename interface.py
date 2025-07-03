import customtkinter as ctk
from tkinter import messagebox
from controle import listar_servicos, agendar_tarefa, remover_agendamentos

def iniciar_interface():
    PRIMARY_BG = "#23272F"   
    SECONDARY_BG = "#23272F" 
    BLUE = "#244B78"         
    YELLOW = "#FFC300"      
    WHITE = "#F5F6FA"
    BTN_TEXT = "#23272F"
    RED = "#e74c3c"

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    root = ctk.CTk()
    root.title("Controle de Serviços do Windows")
    root.geometry("540x375")
    root.resizable(False, False)
    root.configure(fg_color=PRIMARY_BG)

    frame = ctk.CTkFrame(root, fg_color=SECONDARY_BG, corner_radius=18)
    frame.pack(padx=24, pady=18, expand=True, fill="both")

    # Título centralizado
    title = ctk.CTkLabel(frame, text="Controle de Serviços do Windows", 
                         font=("Segoe UI Semibold", 20), text_color=YELLOW)
    title.grid(row=0, column=0, columnspan=2, pady=(7, 14), padx=0, sticky="n")

    # Labels sempre à esquerda
    label_servico = ctk.CTkLabel(frame, text="Selecione o Serviço:", font=("Segoe UI", 13), text_color=YELLOW, anchor="w")
    label_servico.grid(row=1, column=0, sticky="w", pady=3, padx=(8,4))
    try:
        servicos_disponiveis = listar_servicos()
    except Exception as e:
        messagebox.showerror("Erro", str(e))
        servicos_disponiveis = []
    combo_servico = ctk.CTkComboBox(frame, values=servicos_disponiveis, width=262, font=("Segoe UI", 13),
                                    fg_color=WHITE, border_color=BLUE, text_color=PRIMARY_BG, dropdown_fg_color=WHITE,
                                    dropdown_text_color=PRIMARY_BG)
    combo_servico.grid(row=1, column=1, padx=2, pady=3, sticky="ew")

    hint = ctk.CTkLabel(frame, text="Defina o intervalo em que o serviço ficará INATIVO:",
                        font=("Segoe UI", 12, "bold"), text_color=YELLOW, anchor="w")
    hint.grid(row=2, column=0, columnspan=2, pady=(11,7), padx=(8,0), sticky="w")

    # INÍCIO
    ini_lbl = ctk.CTkLabel(frame, text="Início (hora:min):", font=("Segoe UI", 12), text_color=YELLOW, anchor="w")
    ini_lbl.grid(row=3, column=0, sticky="w", pady=2, padx=(8,4))
    ini_frame = ctk.CTkFrame(frame, fg_color="transparent")
    ini_frame.grid(row=3, column=1, sticky="ew", pady=2)
    combo_hora_ini = ctk.CTkComboBox(ini_frame, values=[f"{h:02d}" for h in range(24)],
                                     width=62, font=("Segoe UI", 12), fg_color=WHITE, border_color=BLUE,
                                     text_color=BTN_TEXT)
    combo_min_ini = ctk.CTkComboBox(ini_frame, values=[f"{m:02d}" for m in range(0,60,5)],
                                    width=62, font=("Segoe UI", 12), fg_color=WHITE, border_color=BLUE,
                                    text_color=BTN_TEXT)
    combo_hora_ini.set("08")
    combo_min_ini.set("00")
    combo_hora_ini.pack(side="left")
    ctk.CTkLabel(ini_frame, text=":", font=("Segoe UI", 12, "bold"), text_color=YELLOW, fg_color="transparent").pack(side="left", padx=1)
    combo_min_ini.pack(side="left")

    # FIM
    fim_lbl = ctk.CTkLabel(frame, text="Fim (hora:min):", font=("Segoe UI", 12), text_color=YELLOW, anchor="w")
    fim_lbl.grid(row=4, column=0, sticky="w", pady=2, padx=(8,4))
    fim_frame = ctk.CTkFrame(frame, fg_color="transparent")
    fim_frame.grid(row=4, column=1, sticky="ew", pady=2)
    combo_hora_fim = ctk.CTkComboBox(fim_frame, values=[f"{h:02d}" for h in range(24)],
                                     width=62, font=("Segoe UI", 12), fg_color=WHITE, border_color=BLUE,
                                     text_color=BTN_TEXT)
    combo_min_fim = ctk.CTkComboBox(fim_frame, values=[f"{m:02d}" for m in range(0,60,5)],
                                    width=62, font=("Segoe UI", 12), fg_color=WHITE, border_color=BLUE,
                                    text_color=BTN_TEXT)
    combo_hora_fim.set("18")
    combo_min_fim.set("00")
    combo_hora_fim.pack(side="left")
    ctk.CTkLabel(fim_frame, text=":", font=("Segoe UI", 12, "bold"), text_color=YELLOW, fg_color="transparent").pack(side="left", padx=1)
    combo_min_fim.pack(side="left")

    # Botões centralizados
    def on_submit():
        service = combo_servico.get().strip()
        try:
            hora_ini = int(combo_hora_ini.get())
            min_ini = int(combo_min_ini.get())
            hora_fim = int(combo_hora_fim.get())
            min_fim = int(combo_min_fim.get())
            if not service:
                raise ValueError("Selecione o serviço na lista.")
            if (hora_ini == hora_fim) and (min_ini == min_fim):
                raise ValueError("O intervalo não pode ser nulo (início igual ao fim)")
            msg = agendar_tarefa(service, hora_ini, min_ini, hora_fim, min_fim)
            messagebox.showinfo("Sucesso", msg)
        except Exception as e:
            messagebox.showerror("Erro", f"Verifique os dados:\n{e}")

    def on_remover():
        service = combo_servico.get().strip()
        if not service:
            messagebox.showerror("Erro", "Selecione o serviço na lista.")
            return
        if messagebox.askyesno("Remover agendamentos", "Deseja remover todos os agendamentos criados para este serviço?"):
            try:
                msg = remover_agendamentos(service)
                messagebox.showinfo("Pronto", msg)
            except Exception as e:
                messagebox.showwarning("Atenção", str(e))

    btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
    btn_frame.grid(row=5, column=0, columnspan=2, pady=(22,4), sticky="n")
    btn_agendar = ctk.CTkButton(btn_frame, text="Agendar Serviço", fg_color=YELLOW, text_color=BTN_TEXT,
                                hover_color="#ffd600", command=on_submit, font=("Segoe UI", 12, "bold"),
                                width=160, height=36, corner_radius=8)
    btn_agendar.pack(side="left", padx=(0,10))
    btn_remover = ctk.CTkButton(btn_frame, text="Remover Agendamentos", fg_color=RED, text_color=WHITE,
                                hover_color="#b83223", command=on_remover, font=("Segoe UI", 11, "bold"),
                                width=180, height=36, corner_radius=8)
    btn_remover.pack(side="left")

    # Expandir as colunas para centralização dos campos
    frame.grid_columnconfigure(0, weight=1, minsize=140)
    frame.grid_columnconfigure(1, weight=2)

    # Centraliza janela
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')

    root.mainloop()
