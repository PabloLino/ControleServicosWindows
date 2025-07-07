import customtkinter as ctk
from tkinter import messagebox
import controle
import os
import sys

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        if getattr(sys, 'frozen', False):
            icon_path = os.path.join(sys._MEIPASS, "rclone-05.ico")
        else:
            icon_path = os.path.join(os.path.dirname(__file__), "rclone-05.ico")
        self.iconbitmap(icon_path)
        self.title("Controlador Rclone")
        self.geometry("500x300")
        self.resizable(False, False)
        self.configure(fg_color="#22272f")

        self.frame = ctk.CTkFrame(self, corner_radius=16, fg_color="#262b36")
        self.frame.pack(expand=True, fill="both", padx=16, pady=16)

        ctk.CTkLabel(
            self.frame, text="Selecione o Serviço Para Ser Monitorado",
            font=ctk.CTkFont(size=18, weight="bold"), fg_color="transparent"
        ).grid(row=0, column=0, columnspan=2, pady=(6, 14))

        self.servicos, aviso = controle.listar_servicos()
        if aviso:
            messagebox.showwarning("Aviso", aviso)


        self.display_to_name = {svc['DisplayName']: svc['Name'] for svc in self.servicos}
        self.display_names = sorted(self.display_to_name.keys(), key=lambda x: x.lower())

        ctk.CTkLabel(self.frame, text="Selecione o Serviço:", font=("Segoe UI", 13)).grid(row=1, column=0, pady=5, sticky="e")
        self.combo_servico = ctk.CTkComboBox(self.frame, width=255, font=("Segoe UI", 12),
                                             values=self.display_names, state="readonly")
        self.combo_servico.grid(row=1, column=1, padx=8, pady=5, sticky="w")

        ctk.CTkLabel(self.frame, text="Início do intervalo (hora:min):", font=("Segoe UI", 12)).grid(row=2, column=0, pady=2, sticky="e")
        self.hora_ini = ctk.CTkComboBox(self.frame, width=70, font=("Segoe UI", 12),
                                        values=[f"{h:02d}" for h in range(24)], state="readonly")
        self.hora_ini.set("08")
        self.hora_ini.grid(row=2, column=1, sticky="w", padx=(8,0), pady=2)
        self.min_ini = ctk.CTkComboBox(self.frame, width=60, font=("Segoe UI", 12),
                                       values=[f"{m:02d}" for m in range(0, 60, 5)], state="readonly")
        self.min_ini.set("00")
        self.min_ini.grid(row=2, column=1, sticky="w", padx=(90,0), pady=2)

        ctk.CTkLabel(self.frame, text="Fim do intervalo (hora:min):", font=("Segoe UI", 12)).grid(row=3, column=0, pady=2, sticky="e")
        self.hora_fim = ctk.CTkComboBox(self.frame, width=70, font=("Segoe UI", 12),
                                        values=[f"{h:02d}" for h in range(24)], state="readonly")
        self.hora_fim.set("18")
        self.hora_fim.grid(row=3, column=1, sticky="w", padx=(8,0), pady=2)
        self.min_fim = ctk.CTkComboBox(self.frame, width=60, font=("Segoe UI", 12),
                                       values=[f"{m:02d}" for m in range(0, 60, 5)], state="readonly")
        self.min_fim.set("00")
        self.min_fim.grid(row=3, column=1, sticky="w", padx=(90,0), pady=2)

        self.btn_agendar = ctk.CTkButton(
            self.frame, text="Agendar Serviço", width=150, font=("Segoe UI", 13, "bold"),
            command=self.on_submit, fg_color="#0078d7", hover_color="#005ea6"
        )
        self.btn_agendar.grid(row=4, column=0, columnspan=2, pady=(18, 4), padx=4)
        
        self.frame.grid_columnconfigure(0, weight=0)
        self.frame.grid_columnconfigure(1, weight=1)

    def on_submit(self):
        display = self.combo_servico.get()
        try:
            name = self.display_to_name[display]
        except KeyError:
            messagebox.showerror("Erro", "Selecione um serviço válido.")
            return

        try:
            hora_ini = int(self.hora_ini.get())
            min_ini = int(self.min_ini.get())
            hora_fim = int(self.hora_fim.get())
            min_fim = int(self.min_fim.get())
            if (hora_ini, min_ini) == (hora_fim, min_fim):
                raise ValueError("O intervalo não pode ser nulo (horários iguais).")
        except Exception as e:
            messagebox.showerror("Erro", f"Verifique os horários: {e}")
            return

        try:
            msg = controle.agendar_tarefa(name, hora_ini, min_ini, hora_fim, min_fim)
            messagebox.showinfo("Sucesso", msg)
        except Exception as e:
            messagebox.showerror("Erro ao agendar", str(e))

if __name__ == "__main__":
    app = App()
    app.mainloop()
