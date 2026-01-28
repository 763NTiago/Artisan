import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog, X, EW, W

class ConfigView(ttk.Frame):
    """ (NOVA) Aba de Configurações, incluindo a foto de capa. """
    def __init__(self, parent, controller):
        super().__init__(parent, padding=25)
        self.controller = controller

        frame_fundo = ttk.Labelframe(self, text="Foto de Capa do PDF", padding=20)
        frame_fundo.pack(fill=X, expand=True, pady=10)

        frame_fundo.columnconfigure(0, weight=1)

        ttk.Label(frame_fundo, text="Caminho da Imagem Atual:").grid(row=0, column=0, columnspan=2, sticky=W, pady=(0,5))
        
        self.lbl_caminho_fundo = ttk.Label(
            frame_fundo, 
            text=self.controller.caminho_fundo_atual, 
            bootstyle="info",
            wraplength=600 
        )
        self.lbl_caminho_fundo.grid(row=1, column=0, columnspan=2, sticky=EW, pady=5)

        btn_alterar = ttk.Button(
            frame_fundo,
            text="Alterar Imagem",
            command=self.alterar_fundo,
            bootstyle="primary"
        )
        btn_alterar.grid(row=2, column=0, sticky=EW, padx=(0,5), pady=10, ipady=4)

        btn_resetar = ttk.Button(
            frame_fundo,
            text="Restaurar Padrão",
            command=self.resetar_fundo,
            bootstyle="secondary-outline"
        )
        btn_resetar.grid(row=2, column=1, sticky=EW, padx=(5,0), pady=10, ipady=4)

    def alterar_fundo(self):
        """ Abre um diálogo para selecionar uma nova imagem de fundo. """
        filepath = filedialog.askopenfilename(
            title="Selecione a nova foto de capa",
            filetypes=[("Imagens", "*.png;*.jpg;*.jpeg"), ("Todos os arquivos", "*.*")]
        )
        if filepath:
            self.controller.atualizar_fundo_personalizado(filepath)
            self.lbl_caminho_fundo.config(text=filepath)

    def resetar_fundo(self):
        """ Restaura a imagem de fundo para o padrão (fundo.png). """
        self.controller.resetar_fundo_padrao()
        self.lbl_caminho_fundo.config(text=self.controller.caminho_fundo_padrao)