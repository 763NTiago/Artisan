import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import END, W, EW
from .. import utils

class ClienteView(ttk.Frame):
    """ Aba de Informações do Cliente. """
    def __init__(self, parent, controller):
        super().__init__(parent, padding=15)
        self.controller = controller

        ttk.Label(self, text="Nome do Cliente:", font=("Arial", 10)).grid(
            row=0, column=0, padx=10, pady=8, sticky=W
        )
        self.entry_cliente_nome = ttk.Entry(self, width=70, font=("Arial", 10))
        self.entry_cliente_nome.grid(row=0, column=1, padx=10, pady=8, sticky=EW)

        ttk.Label(self, text="Endereço:", font=("Arial", 10)).grid(
            row=1, column=0, padx=10, pady=8, sticky=W
        )
        self.entry_cliente_endereco = ttk.Entry(self, width=70, font=("Arial", 10))
        self.entry_cliente_endereco.grid(row=1, column=1, padx=10, pady=8, sticky=EW)

        ttk.Label(self, text="CPF/CNPJ:", font=("Arial", 10)).grid(
            row=2, column=0, padx=10, pady=8, sticky=W
        )
        self.entry_cliente_cpf = ttk.Entry(self, width=30, font=("Arial", 10))
        self.entry_cliente_cpf.grid(row=2, column=1, padx=10, pady=8, sticky=W)

        ttk.Label(self, text="E-mail:", font=("Arial", 10)).grid(
            row=3, column=0, padx=10, pady=8, sticky=W
        )
        self.entry_cliente_email = ttk.Entry(self, width=50, font=("Arial", 10))
        self.entry_cliente_email.grid(row=3, column=1, padx=10, pady=8, sticky=EW)

        ttk.Label(self, text="Telefone:", font=("Arial", 10)).grid(
            row=4, column=0, padx=10, pady=8, sticky=W
        )
        self.entry_cliente_telefone = ttk.Entry(self, width=30, font=("Arial", 10))
        self.entry_cliente_telefone.grid(row=4, column=1, padx=10, pady=8, sticky=W)

        self.columnconfigure(1, weight=1)
        self.entry_cliente_cpf.bind("<FocusOut>", self.formatar_cpf_cnpj_campo)
        self.entry_cliente_telefone.bind("<FocusOut>", self.formatar_telefone_campo)

    def formatar_cpf_cnpj_campo(self, event):
        valor_atual = self.entry_cliente_cpf.get()
        if valor_atual:
            valor_formatado = utils.formatar_cpf_cnpj(valor_atual)
            self.entry_cliente_cpf.delete(0, END)
            self.entry_cliente_cpf.insert(0, valor_formatado)

    def formatar_telefone_campo(self, event):
        valor_atual = self.entry_cliente_telefone.get()
        if valor_atual:
            valor_formatado = utils.formatar_telefone(valor_atual)
            self.entry_cliente_telefone.delete(0, END)
            self.entry_cliente_telefone.insert(0, valor_formatado)

    def get_data(self):
        """ Retorna os dados do cliente em um dicionário. """
        return {
            "cliente_nome": self.entry_cliente_nome.get().strip(),
            "cliente_endereco": self.entry_cliente_endereco.get().strip(),
            "cliente_cpf": self.entry_cliente_cpf.get().strip(),
            "cliente_email": self.entry_cliente_email.get().strip(),
            "cliente_telefone": self.entry_cliente_telefone.get().strip(),
        }

    def set_data(self, data):
        """ Preenche os campos com dados (ex: ao carregar do histórico). """
        self.clear_data()
        self.entry_cliente_nome.insert(0, data.get("cliente_nome", ""))
        self.entry_cliente_endereco.insert(0, data.get("cliente_endereco", ""))
        self.entry_cliente_cpf.insert(0, data.get("cliente_cpf", ""))
        self.entry_cliente_email.insert(0, data.get("cliente_email", ""))
        self.entry_cliente_telefone.insert(0, data.get("cliente_telefone", ""))

    def clear_data(self):
        """ Limpa todos os campos de entrada. """
        self.entry_cliente_nome.delete(0, END)
        self.entry_cliente_endereco.delete(0, END)
        self.entry_cliente_cpf.delete(0, END)
        self.entry_cliente_email.delete(0, END)
        self.entry_cliente_telefone.delete(0, END)