import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, filedialog, END
import os
import webbrowser 
from urllib.parse import quote
from datetime import datetime, timedelta
import sys

from .. import utils 

class CartaoView(ttk.Frame):
    def __init__(self, parent, app_controller):
        super().__init__(parent)
        self.app = app_controller 
        self.dialog_choice = None
        self.setup_ui()

    def setup_ui(self):
        main_frame = ttk.Frame(self, padding=30)
        main_frame.pack(expand=True, fill=BOTH)

        form_frame = ttk.Labelframe(main_frame, text="Gerador de Cartão Desconto", padding=20)
        form_frame.pack(expand=True, fill=X, padx=50, pady=20)

        lbl_nome = ttk.Label(form_frame, text="Nome do Cliente:", font=("Arial", 10))
        lbl_nome.grid(row=0, column=0, sticky=W, padx=10, pady=10)
        self.entry_nome = ttk.Entry(form_frame, width=50, font=("Arial", 10))
        self.entry_nome.grid(row=0, column=1, sticky=EW, padx=10, pady=10)

        lbl_tel = ttk.Label(form_frame, text="Telefone (com DDI):", font=("Arial", 10))
        lbl_tel.grid(row=1, column=0, sticky=W, padx=10, pady=10)
        self.entry_tel = ttk.Entry(form_frame, width=30, font=("Arial", 10))
        self.entry_tel.grid(row=1, column=1, sticky=W, padx=10, pady=10)
        self.entry_tel.insert(0, "+55") 
        
        self.entry_tel.bind("<KeyRelease>", self._formatar_telefone_entry)

        lbl_desconto = ttk.Label(form_frame, text="Desconto (%):", font=("Arial", 10))
        lbl_desconto.grid(row=2, column=0, sticky=W, padx=10, pady=10)
        self.spin_desconto = ttk.Spinbox(form_frame, from_=1, to=100, width=10, font=("Arial", 10))
        self.spin_desconto.grid(row=2, column=1, sticky=W, padx=10, pady=10)
        self.spin_desconto.set("15")

        lbl_codigo = ttk.Label(form_frame, text="Código (opcional):", font=("Arial", 10))
        lbl_codigo.grid(row=3, column=0, sticky=W, padx=10, pady=10)
        self.entry_codigo = ttk.Entry(form_frame, width=30, font=("Arial", 10))
        self.entry_codigo.grid(row=3, column=1, sticky=W, padx=10, pady=10)
        self.entry_codigo.insert(0, f"{datetime.now().year}BELLASARTES{self.spin_desconto.get()}")

        lbl_validade = ttk.Label(form_frame, text="Data de Validade:", font=("Arial", 10))
        lbl_validade.grid(row=4, column=0, sticky=W, padx=10, pady=10)
        self.entry_validade = ttk.Entry(form_frame, width=20, font=("Arial", 10))
        self.entry_validade.grid(row=4, column=1, sticky=W, padx=10, pady=10)
        data_futura = datetime.now() + timedelta(days=30)
        self.entry_validade.insert(0, data_futura.strftime("%d/%m/%Y"))

        form_frame.columnconfigure(1, weight=1)

        botoes_frame = ttk.Frame(main_frame)
        botoes_frame.pack(pady=20, fill=X, padx=50)

        self.btn_salvar_png = ttk.Button(
            botoes_frame,
            text="💾 Salvar como PNG",
            command=self.salvar_imagem_png, 
            bootstyle="primary" 
        )
        self.btn_salvar_png.pack(side=LEFT, expand=True, ipady=10, padx=(0, 5))

        self.btn_enviar_wpp = ttk.Button(
            botoes_frame,
            text="🚀 Compartilhar (Manual)",
            command=self.compartilhar_via_whatsapp, 
            bootstyle="success"
        )
        self.btn_enviar_wpp.pack(side=RIGHT, expand=True, ipady=10, padx=(5, 0))
        
    def _formatar_telefone_entry(self, event):
        if hasattr(event, 'keysym') and event.keysym in (
            "Left", "Right", "Up", "Down", "Home", "End", "Tab", 
            "Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R"
        ):
            return

        texto_atual = self.entry_tel.get()
        pos_cursor = self.entry_tel.index(INSERT)

        if not texto_atual.startswith("+55"):
            numeros_limpos = ''.join(filter(str.isdigit, texto_atual))
            texto_atual = "+55" + numeros_limpos
            pos_cursor = len(texto_atual) 

        numeros = ''.join(filter(str.isdigit, texto_atual[3:]))[:11]

        formatado = "+55"
        if len(numeros) > 0:
            formatado += f" ({numeros[:2]}"
        if len(numeros) > 2:
            formatado += f") {numeros[2:3]}"
        if len(numeros) > 3:
            formatado += f" {numeros[3:7]}"
        if len(numeros) > 7:
            formatado += f"-{numeros[7:11]}"

        if formatado != texto_atual:
            self.entry_tel.delete(0, END)
            self.entry_tel.insert(0, formatado)

            if len(formatado) > len(texto_atual):
                self.entry_tel.icursor(pos_cursor + (len(formatado) - len(texto_atual)))
            else:
                self.entry_tel.icursor(pos_cursor)
        
        if self.entry_tel.index(INSERT) < 3:
            self.entry_tel.icursor(3)

    def _ask_whatsapp_type(self):
        dialog = ttk.Toplevel(self.app.root)
        dialog.title("Escolha o Método")
        dialog.geometry("350x180") 
        dialog.resizable(False, False)
        dialog.transient(self.app.root)
        dialog.grab_set() 
        
        self.dialog_choice = "cancel"

        def set_choice(choice):
            self.dialog_choice = choice
            dialog.destroy()

        lbl = ttk.Label(dialog, text="Onde quer abrir a conversa?", font=("Arial", 12), padding=20)
        lbl.pack()

        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill=X, expand=True, padx=20)

        btn_web = ttk.Button(btn_frame, text="WhatsApp Web", 
                            command=lambda: set_choice("web"), bootstyle="primary")
        btn_web.pack(side=LEFT, expand=True, padx=5, ipady=8)

        btn_desk = ttk.Button(btn_frame, text="WhatsApp Desktop", 
                             command=lambda: set_choice("desktop"), bootstyle="info")
        btn_desk.pack(side=RIGHT, expand=True, padx=5, ipady=8)
        
        btn_cancel = ttk.Button(dialog, text="Cancelar", 
                                command=lambda: set_choice("cancel"), bootstyle="secondary-outline")
        btn_cancel.pack(pady=15)

        dialog.update_idletasks()
        x = self.app.root.winfo_x() + (self.app.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.app.root.winfo_y() + (self.app.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        self.app.root.wait_window(dialog)
        return self.dialog_choice

    def _validar_e_coletar_dados(self, requerer_telefone=False):
        dados = {
            "nome": self.entry_nome.get().strip(),
            "porcentagem": self.spin_desconto.get().strip(),
            "data_validade": self.entry_validade.get().strip(),
            "telefone": self.entry_tel.get().strip()
        }

        if not dados["nome"]:
            messagebox.showwarning("Campo Obrigatório", "Por favor, preencha o nome do cliente.")
            self.entry_nome.focus()
            return None

        if not dados["porcentagem"].isdigit():
            messagebox.showerror("Valor Inválido", "A porcentagem de desconto deve ser um número.")
            return None
        
        if requerer_telefone:
            numeros_tel = ''.join(filter(str.isdigit, dados["telefone"]))
            
            if not numeros_tel or len(numeros_tel) < 13:
                messagebox.showwarning("Telefone Inválido", 
                                       "Por favor, preencha um telefone celular válido no formato:\n"
                                       "+55 (XX) 9 XXXX-XXXX")
                self.entry_tel.focus()
                return None
            
        dados["porcentagem"] = int(dados["porcentagem"])
        return dados
        
    def _gerar_cartao(self, dados, output_path):
        try:
            sucesso, mensagem = utils.gerar_imagem_cartao(
                nome=dados['nome'],
                porcentagem=dados['porcentagem'],
                data_validade=dados['data_validade'],
                output_path=output_path
            )
            return sucesso, mensagem
        except Exception as e:
            messagebox.showerror("Erro Inesperado", 
                                 f"Ocorreu um erro ao tentar gerar a imagem:\n{str(e)}")
            return False, str(e)

    def salvar_imagem_png(self):
        dados = self._validar_e_coletar_dados(requerer_telefone=False) 
        if not dados:
            return

        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        nome_sugerido = f"cartao_{dados['nome'].replace(' ', '_').lower()}.png"
        
        filepath = filedialog.asksaveasfilename(
            initialdir=desktop_path, 
            initialfile=nome_sugerido,
            defaultextension=".png",
            filetypes=[("Imagens PNG", "*.png"), ("Todos os arquivos", "*.*")]
        )
        
        if not filepath:
            return 

        sucesso, mensagem = self._gerar_cartao(dados, filepath)
            
        if sucesso:
            messagebox.showinfo("Sucesso!", f"Cartão gerado e salvo com sucesso em:\n{filepath}")
            self._limpar_campos_principais()
        else:
            messagebox.showerror("Erro na Geração", 
                                 f"Não foi possível gerar o cartão PNG.\n\n"
                                 f"Detalhe: {mensagem}")

    def compartilhar_via_whatsapp(self):
        dados = self._validar_e_coletar_dados(requerer_telefone=True) 
        if not dados:
            return
            
        try:
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            nome_sugerido = f"cartao_{dados['nome'].replace(' ', '_').lower()}.png"
            
            filepath = filedialog.asksaveasfilename(
                title="Passo 1: Salve a imagem do cartão",
                initialdir=desktop_path,
                initialfile=nome_sugerido,
                defaultextension=".png",
                filetypes=[("Imagens PNG", "*.png"), ("Todos os arquivos", "*.*")]
            )
            
            if not filepath:
                return 

            sucesso, msg = self._gerar_cartao(dados, filepath)
            if not sucesso:
                messagebox.showerror("Erro na Geração", f"Não foi possível salvar o cartão em:\n{filepath}\n\nDetalhe: {msg}")
                return

            legenda_texto = (f"Olá {dados['nome']}! ✨\n"
                           f"Parabéns! Você ganhou um cartão de desconto de {dados['porcentagem']}% "
                           f"aqui na Bellas Artes Marcenaria!\n\n"
                           f"Válido até: {dados['data_validade']}")
            
            legenda_url = quote(legenda_texto)

            tipo_envio = self._ask_whatsapp_type()
            
            if tipo_envio == "cancel":
                return
            
            telefone_limpo = ''.join(filter(str.isdigit, dados["telefone"]))
            
            url = ""
            app_nome = ""
            if tipo_envio == "web":
                url = f"https://web.whatsapp.com/send?phone={telefone_limpo}&text={legenda_url}"
                app_nome = "WhatsApp Web"
            else: 
                url = f"whatsapp://send?phone={telefone_limpo}&text={legenda_url}"
                app_nome = "WhatsApp Desktop"

            webbrowser.open(url)
            
            messagebox.showinfo("Próximo Passo", 
                                f"O {app_nome} foi aberto com a mensagem!\n\n"
                                f"A imagem foi salva em:\n**{filepath}**\n\n"
                                "Por favor, clique no 'Anexar' (clipe) e selecione a imagem que acabou de salvar.")
            
            self._limpar_campos_principais()

        except Exception as e:
            messagebox.showerror("Erro Inesperado", 
                                 f"Ocorreu um erro durante o processo.\n"
                                 f"Detalhe: {str(e)}")

    def _limpar_campos_principais(self):
        self.entry_nome.delete(0, END) 
        self.entry_tel.delete(0, END)
        self.entry_tel.insert(0, "+55")
        self.entry_codigo.delete(0, END)
        self.entry_codigo.insert(0, f"{datetime.now().year}BELLASARTES{self.spin_desconto.get()}")