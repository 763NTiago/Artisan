import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class PerfilView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, padding=20)
        self.controller = controller
        
        main_container = ttk.Frame(self)
        main_container.pack(fill=BOTH, expand=True)
        
        content_frame = ttk.Frame(main_container)
        content_frame.place(relx=0.5, rely=0.5, anchor=CENTER)
        
        ttk.Label(content_frame, text="👤", font=("Segoe UI Emoji", 48)).pack(pady=10)
        
        ttk.Label(content_frame, text="Perfil do Usuário", 
                 font=("Arial", 24, "bold"), bootstyle="primary").pack(pady=5)
        
        ttk.Label(content_frame, text="Em breve: Gerenciamento de conta e configurações do usuário.", 
                 font=("Arial", 12), bootstyle="secondary").pack(pady=10)
        
        pb = ttk.Progressbar(content_frame, bootstyle="info-striped", length=300, mode='indeterminate')
        pb.pack(pady=20)
        pb.start(15)

    def on_focus(self):
        pass