import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, filedialog, Text, END, WORD, SOLID, TOP, BOTTOM, BOTH, X, CENTER, VERTICAL, NS, W, EW, NW, NSEW, LEFT, RIGHT
import os
import sys
import jinja2
import pdfkit
import tempfile
import webbrowser
import subprocess
import json
from datetime import datetime

from . import utils
from .model import DatabaseModel
from .views import (HomeView, OrcamentoView, 
                    ConfigView, MateriaisView, CartaoView,
                    ComissaoView, AgendaView, RecebimentosView,
                    RelatoriosView, PerfilView)

class OrcamentoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerador de Orçamentos - Artisan")
        
        window_width = 1100
        window_height = 750
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        center_x = int((screen_width / 2) - (window_width / 2))
        center_y = int((screen_height / 2) - (window_height / 2))

        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        self.root.minsize(width=1000, height=700)
        
        self.model = DatabaseModel()
        self.model.init_db() 
        self.id_orcamento_em_edicao = None
        
        self.config = utils.load_config()
        self.caminho_fundo_padrao = utils.PATH_FUNDO_PADRAO
        
        caminho_custom = self.config.get('custom_background_path')
        if caminho_custom and os.path.exists(caminho_custom):
            self.caminho_fundo_atual = caminho_custom
        else:
            self.caminho_fundo_atual = self.caminho_fundo_padrao

        self.logo_base64 = utils.load_image_base64(utils.PATH_LOGO)
        self.fundo_base64 = utils.load_image_base64(self.caminho_fundo_atual)

        if not self.logo_base64: messagebox.showwarning("Atenção", f"Logo não encontrado em '{utils.PATH_LOGO}'.")
        if not self.fundo_base64: messagebox.showwarning("Atenção", f"Imagem de fundo não encontrada em '{self.caminho_fundo_atual}'.")
        
        self.config_pdfkit = None
        if os.path.exists(utils.PATH_WK_LOCAL):
            self.config_pdfkit = pdfkit.configuration(wkhtmltopdf=utils.PATH_WK_LOCAL)
        else:
            messagebox.showerror("Erro Crítico", f"Não foi possível encontrar o 'wkhtmltopdf.exe'.\n{utils.PATH_WK_LOCAL}")

        template_loader = jinja2.FileSystemLoader(searchpath=utils.TEMPLATES_PATH)
        self.jinja_env = jinja2.Environment(loader=template_loader)
        self.template = self.jinja_env.get_template("template.html") 
        
        self.css_content = self._load_css_content()
        
        if not self.css_content:
             messagebox.showerror("Erro Crítico", f"Nenhum ficheiro CSS encontrado em '{utils.CSS_PATH}'.")
             self.css_content = ""

        self.views_map = {}
        self.create_main_layout()
        self.popular_historico() 
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _load_css_content(self):
        css_total = ""
        ficheiros_css = ["base.css", "capa.css", "conteudo.css"] 
        try:
            for ficheiro in ficheiros_css:
                caminho_completo = os.path.join(utils.CSS_PATH, ficheiro)
                if os.path.exists(caminho_completo):
                    with open(caminho_completo, "r", encoding="utf-8") as f:
                        css_total += f.read() + "\n\n"
                else:
                    messagebox.showwarning("CSS Não Encontrado", f"O ficheiro {ficheiro} não foi encontrado em {utils.CSS_PATH}")
            return css_total
        except Exception as e:
            messagebox.showerror("Erro ao Carregar CSS", f"Não foi possível ler os ficheiros CSS: {e}")
            return None

    def _load_css_cartao(self):
        try:
            caminho_completo = os.path.join(utils.CSS_PATH, "cartao.css")
            if os.path.exists(caminho_completo):
                with open(caminho_completo, "r", encoding="utf-8") as f:
                    return f.read()
            return ""
        except Exception:
            return ""

    def on_closing(self):
        if self.id_orcamento_em_edicao:
            if not messagebox.askyesno("Sair", 
                                       f"Você está a editar o Orçamento ID {self.id_orcamento_em_edicao}.\n"
                                       "As alterações não salvas serão perdidas.\n\n"
                                       "Deseja realmente sair?"):
                return 

        self.model.close()
        self.root.destroy()

    def create_main_layout(self):
        main_frame = ttk.Frame(self.root, padding=15)
        main_frame.pack(fill=BOTH, expand=True)

        title_label = ttk.Label(main_frame, text="Artisan - GERADOR DE ORÇAMENTOS",
            font=("Arial", 16, "bold"), bootstyle="inverse-danger", padding=12, anchor=CENTER)
        title_label.pack(side=TOP, fill=X, pady=(0, 10))

        self.notebook = ttk.Notebook(main_frame, bootstyle="primary")
        self.notebook.pack(side=TOP, fill=BOTH, expand=True, pady=5)
        
        self.view_home = HomeView(self.notebook, self)
        self.notebook.add(self.view_home, text="🏠 Home")
        self.views_map['home'] = self.view_home
        
        self.view_orcamento = OrcamentoView(self.notebook, self)
        self.view_cliente = self.view_orcamento.view_cliente
        self.view_itens = self.view_orcamento.view_itens
        self.view_termos = self.view_orcamento.view_termos
        self.view_historico = self.view_orcamento.view_historico
        self.view_materiais = self.view_orcamento.view_materiais
        self.view_config = self.view_orcamento.view_config
        self.notebook.add(self.view_orcamento, text="📝 Orçamentos")
        
        self.view_cartao = CartaoView(self.notebook, self)
        self.notebook.add(self.view_cartao, text="💳 Cartão Desconto")

        self.view_agenda = AgendaView(self.notebook, self)
        self.notebook.add(self.view_agenda, text="🗓️ Agenda/Projetos")
        self.views_map['agenda'] = self.view_agenda

        self.view_recebimentos = RecebimentosView(self.notebook, self)
        self.notebook.add(self.view_recebimentos, text="💸 Recebimentos")
        self.views_map['recebimentos'] = self.view_recebimentos

        self.view_comissao = ComissaoView(self.notebook, self)
        self.notebook.add(self.view_comissao, text="💰 Comissão")
        self.views_map['comissao'] = self.view_comissao
        

        self.view_relatorios = RelatoriosView(self.notebook, self)
        self.notebook.add(self.view_relatorios, text="📊 Relatórios")
        self.views_map['relatorios'] = self.view_relatorios


        self.view_perfil = PerfilView(self.notebook, self)
        self.notebook.add(self.view_perfil, text="👤 Perfil")
        self.views_map['perfil'] = self.view_perfil
        
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
    def on_tab_changed(self, event):
        try:
            nome_aba = self.notebook.tab(self.notebook.select(), "text").lower()
            
            if "orçamentos" not in nome_aba and self.id_orcamento_em_edicao:
                messagebox.showwarning("Modo de Edição Ativo", 
                                       f"Você está a editar o Orçamento ID {self.id_orcamento_em_edicao}.\n\n"
                                       "Salve ou carregue outro orçamento para sair do modo de edição.")
                self.notebook.select(self.view_orcamento)
                return

            if "home" in nome_aba:
                self.atualizar_aba('home')
            elif "agenda" in nome_aba:
                self.atualizar_aba('agenda')
            elif "recebimentos" in nome_aba:
                self.atualizar_aba('recebimentos')
            elif "comissão" in nome_aba:
                self.atualizar_aba('comissao')
            elif "perfil" in nome_aba:         
                self.atualizar_aba('perfil')    
        except Exception as e:
            print(f"Erro ao trocar de aba: {e}")

    def atualizar_aba(self, nome_aba):
        if nome_aba in self.views_map:
            view = self.views_map[nome_aba]
            if hasattr(view, 'on_focus'):
                print(f"Atualizando aba: {nome_aba}")
                view.on_focus()


    def coletar_dados(self):
        dados_cliente = self.view_cliente.get_data()
        if not dados_cliente["cliente_nome"]:
            if self.id_orcamento_em_edicao:
                if messagebox.askyesno("Atenção", "O Nome do Cliente não pode ficar vazio."):
                    self.id_orcamento_em_edicao = None
            self.notebook.select(self.view_orcamento)
            return None
            
        itens_tabela = self.view_itens.get_itens_data()
        valor_total_orcamento = self.view_itens.get_total() 
        dados_termos = self.view_termos.get_data()

        contexto = {
            "logo_base64": self.logo_base64, 
            "fundo_base64": self.fundo_base64, 
            "css_style": self.css_content, 
            "data_hoje": utils.get_data_hoje(),
            "empresa_nome": os.getenv('EMPRESA_NOME', 'Empresa Exemplo'),
            "empresa_slogan": os.getenv('EMPRESA_SLOGAN', 'Slogan da Empresa'),
            "empresa_endereco": os.getenv('EMPRESA_ENDERECO', 'Endereço Completo'),
            "empresa_telefones": os.getenv('EMPRESA_FONE', '(00) 00000-0000'),
            "empresa_instagram": os.getenv('EMPRESA_INSTA', '@empresa'),
            "empresa_cnpj": os.getenv('EMPRESA_CNPJ', '00.000.000/0001-00'),
            "cliente_nome": dados_cliente["cliente_nome"], 
            "cliente_endereco": dados_cliente["cliente_endereco"],
            "cliente_cpf": utils.formatar_cpf_cnpj(dados_cliente["cliente_cpf"]),
            "cliente_email": dados_cliente["cliente_email"],
            "cliente_telefone": utils.formatar_telefone(dados_cliente["cliente_telefone"]),
            "itens": itens_tabela, 
            "valor_total_final": utils.formatar_moeda(str(valor_total_orcamento)),
            "observacoes": dados_termos["observacoes_html"],
            "condicoes_pagamento": dados_termos["pagamento_html"]
        }
        return contexto

    def gerar_html(self):
        try:
            dados = self.coletar_dados()
            if not dados: return None, None
            if not self.logo_base64:
                messagebox.showerror("Erro", f"Logo não carregado. Verifique '{utils.PATH_LOGO}'."); return None, None
            if not self.fundo_base64:
                 messagebox.showwarning("Aviso", f"Fundo não carregado. Verifique '{self.caminho_fundo_atual}'.")
            html_renderizado = self.template.render(dados)
            return html_renderizado, dados 
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar HTML: {e}"); return None, None

    def gerar_pdf(self, html_content, output_path):
        if not self.config_pdfkit:
            messagebox.showerror("Erro PDFKit", "A configuração do 'wkhtmltopdf' não foi encontrada. Não é possível gerar o PDF."); return False
        try:
            options = {'page-size': 'A4', 'margin-top': '0mm', 'margin-right': '0mm', 'margin-bottom': '0mm', 'margin-left': '0mm',
                       'encoding': "UTF-8", 'enable-local-file-access': None, 'dpi': 300, 'no-stop-slow-scripts': None,
                       'enable-javascript': None, 'javascript-delay': 1000}
            pdfkit.from_string(html_content, output_path, options=options, configuration=self.config_pdfkit)
            return True
        except IOError as e:
            messagebox.showerror("Erro PDFKit", f"Erro de E/S ao gerar PDF: {e}\n\nVerifique se o 'wkhtmltopdf' está instalado."); return False
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado ao gerar PDF: {e}"); return False

    def preview_pdf(self):
        html, _ = self.gerar_html()
        if not html: return
        try:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
                temp_pdf_path = temp_file.name
            if self.gerar_pdf(html, temp_pdf_path):
                print(f"Abrindo preview: {temp_pdf_path}")
                if sys.platform == "win32": os.startfile(temp_pdf_path)
                else: webbrowser.open_new(f'file://{os.path.realpath(temp_pdf_path)}')
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir o PDF: {e}")

    def save_pdf_e_historico(self):
        html, dados = self.gerar_html()
        if not html or not dados: return
        
        nome_cliente = dados["cliente_nome"].replace(" ", "_") or "orcamento"
        
        if self.id_orcamento_em_edicao:
            initial_file = f"Orcamento_Artisan_ID{self.id_orcamento_em_edicao}_{nome_cliente}.pdf"
        else:
            initial_file = f"Orcamento_Artisan_{nome_cliente}.pdf"
            
        filepath = filedialog.asksaveasfilename(
            initialfile=initial_file,
            defaultextension=".pdf", filetypes=[("Documentos PDF", "*.pdf"), ("Todos os arquivos", "*.*")]
        )
        if not filepath: return 
        
        if self.gerar_pdf(html, filepath):
            messagebox.showinfo("Sucesso!", f"Orçamento salvo em:\n{filepath}")
            
            try:
                if self.id_orcamento_em_edicao is not None:
                    
                    id_para_atualizar = self.id_orcamento_em_edicao
                    
                    if messagebox.askyesno("Confirmar Atualização", 
                                            f"Você está editando o Orçamento ID {id_para_atualizar}.\n\n"
                                            "Deseja ATUALIZAR este orçamento no histórico com os novos dados?"):
                        
                        if self.model.update_orcamento(id_para_atualizar, dados):
                            messagebox.showinfo("Sucesso", f"Orçamento ID {id_para_atualizar} atualizado!")
                            self.id_orcamento_em_edicao = None
                            self.popular_historico()
                            self.atualizar_aba('home')
                        else:
                            messagebox.showerror("Erro DB", "Não foi possível ATUALIZAR o orçamento.")
                
                else:
                    if messagebox.askyesno("Histórico", "Deseja salvar este NOVO orçamento no histórico?\n\n(Isto NÃO irá criar um projeto na Agenda.)"):
                        
                        self.salvar_no_historico_novo(dados) 
            
            except Exception as e:
                messagebox.showerror("Erro DB", f"Não foi possível salvar no histórico: {e}")
                self.id_orcamento_em_edicao = None 
                
            if messagebox.askyesno("Abrir Pasta", "Deseja abrir a pasta do arquivo?"):
                try: subprocess.Popen(f'explorer /select,"{os.path.normpath(filepath)}"')
                except Exception as e: messagebox.showerror("Erro", f"Não foi possível abrir a pasta: {e}")
        
        else:
            pass
    def salvar_no_historico_novo(self, dados):
        try:
            if self.model.salvar_orcamento(dados, agenda_id=None):
                messagebox.showinfo("Sucesso", "Orçamento salvo no histórico!")
                self.popular_historico()
                self.atualizar_aba('home') 
            else:
                messagebox.showerror("Erro DB", "Não foi possível salvar o orçamento no histórico.")
                
        except Exception as e:
            messagebox.showerror("Erro DB", f"Não foi possível salvar no histórico: {e}")            

    def popular_historico(self):
        if hasattr(self, 'view_historico'):
            self.view_historico.popular_historico()

    def carregar_do_historico(self):
        orcamento_id = self.view_historico.get_selected_id()
        if not orcamento_id: return
        
        if self.id_orcamento_em_edicao:
            if not messagebox.askyesno("Aviso", 
                                       f"Você está a editar o Orçamento ID {self.id_orcamento_em_edicao}.\n"
                                       "Se carregar um novo, as alterações serão perdidas.\n\n"
                                       "Deseja cancelar a edição e carregar o ID {orcamento_id}?"):
                return
            self.id_orcamento_em_edicao = None 
            
        try:
            row = self.model.get_orcamento_by_id(orcamento_id) 
            if not row:
                messagebox.showerror("Erro", "Orçamento não encontrado."); return
                
            dados_cliente = {
                "cliente_nome": row["cliente_nome"], 
                "cliente_endereco": row["cliente_endereco"], 
                "cliente_cpf": row["cliente_cpf"], 
                "cliente_email": row["cliente_email"], 
                "cliente_telefone": row["cliente_telefone"]
            }
            dados_termos = {
                "observacoes": row["observacoes"], 
                "condicoes_pagamento": row["condicoes_pagamento"]
            }
            
            itens_carregados = [] 
            try:
                if row["itens_json"] and row["itens_json"].strip(): 
                    itens_carregados = json.loads(row["itens_json"])
                else:
                    print(f"Aviso (Carregar Histórico): Orçamento ID {orcamento_id} não possui itens.")
            except json.JSONDecodeError as e:
                print(f"AVISO (Carregar Histórico): Orçamento ID {orcamento_id} tem um 'itens_json' quebrado. Carregando sem itens. Erro: {e}")
            
            self.view_cliente.set_data(dados_cliente)
            self.view_termos.set_data(dados_termos)
            self.view_itens.set_data(itens_carregados)
            
            self.view_itens.atualizar_total() 
            
            self.notebook.select(self.view_orcamento) 
            self.view_orcamento.notebook_orcamento.select(self.view_cliente)
            messagebox.showinfo("Sucesso", f"Orçamento ID {orcamento_id} carregado!")
        except Exception as e:
            messagebox.showerror("Erro DB", f"Não foi possível carregar do histórico: {e}")
            print(f"Erro detalhado ao carregar: {e}")

    def iniciar_edicao_historico(self):
        orcamento_id = self.view_historico.get_selected_id()
        if not orcamento_id:
            return 

        if self.id_orcamento_em_edicao and self.id_orcamento_em_edicao != orcamento_id:
             if not messagebox.askyesno("Aviso", 
                                       f"Você já está a editar o Orçamento ID {self.id_orcamento_em_edicao}.\n"
                                       "Deseja cancelar e começar a editar o ID {orcamento_id}?"):
                return
        
        try:
            row = self.model.get_orcamento_by_id(orcamento_id) 
            if not row:
                messagebox.showerror("Erro", "Orçamento não encontrado."); return
                
            dados_cliente = {
                "cliente_nome": row["cliente_nome"], "cliente_endereco": row["cliente_endereco"], 
                "cliente_cpf": row["cliente_cpf"], "cliente_email": row["cliente_email"], 
                "cliente_telefone": row["cliente_telefone"]
            }
            dados_termos = {
                "observacoes": row["observacoes"], "condicoes_pagamento": row["condicoes_pagamento"]
            }
            itens_carregados = [] 
            try:
                if row["itens_json"] and row["itens_json"].strip(): 
                    itens_carregados = json.loads(row["itens_json"])
            except json.JSONDecodeError:
                pass 
            
            self.view_cliente.set_data(dados_cliente)
            self.view_termos.set_data(dados_termos)
            self.view_itens.set_data(itens_carregados)
            self.view_itens.atualizar_total() 
            
            self.notebook.select(self.view_orcamento) 
            self.view_orcamento.notebook_orcamento.select(self.view_cliente)
            
            self.id_orcamento_em_edicao = orcamento_id
            
            messagebox.showinfo("Modo de Edição", 
                                f"Editando Orçamento ID {orcamento_id}.\n\n"
                                "Faça as alterações e clique em 'Salvar PDF e no Histórico' para atualizar.")
        
        except Exception as e:
            messagebox.showerror("Erro DB", f"Não foi possível carregar para edição: {e}")
            print(f"Erro detalhado ao carregar para edição: {e}")
            self.id_orcamento_em_edicao = None 

    def remover_do_historico(self):
        orcamento_id = self.view_historico.get_selected_id()
        if not orcamento_id: return
        
        if self.id_orcamento_em_edicao == orcamento_id:
            messagebox.showerror("Ação Bloqueada", 
                                 f"Você está a editar o Orçamento ID {orcamento_id}.\n"
                                 "Não pode removê-lo agora. Salve ou cancele a edição primeiro.")
            return

        if not messagebox.askyesno("Confirmar", "Tem certeza que deseja remover este orçamento no histórico? Esta ação não pode ser desfeita."):
            return
        try:
            self.model.delete_orcamento(orcamento_id)
            self.popular_historico()
            messagebox.showinfo("Sucesso", "Orçamento removido do histórico.")
        except Exception as e:
            messagebox.showerror("Erro DB", f"Não foi possível remover do histórico: {e}")

    def atualizar_fundo_personalizado(self, novo_caminho):
        self.caminho_fundo_atual = novo_caminho
        self.config['custom_background_path'] = novo_caminho
        utils.save_config(self.config)
        self.fundo_base64 = utils.load_image_base64(self.caminho_fundo_atual)
        if self.fundo_base64:
            messagebox.showinfo("Sucesso", "Foto de capa atualizada!")
        else:
            messagebox.showerror("Erro", f"Não foi possível carregar a imagem em:\n{novo_caminho}")
            self.resetar_fundo_padrao() 

    def resetar_fundo_padrao(self):
        self.caminho_fundo_atual = self.caminho_fundo_padrao
        self.config['custom_background_path'] = None
        utils.save_config(self.config)
        self.fundo_base64 = utils.load_image_base64(self.caminho_fundo_padrao)
        messagebox.showinfo("Sucesso", "Foto de capa restaurada para o padrão.")

    def gerar_cartao_pdf(self):
        dados_cartao = self.view_cartao.get_data()
        
        if not dados_cartao["cliente_nome"]:
            messagebox.showwarning("Atenção", "Preencha o Nome do Cliente.", parent=self.view_cartao)
            self.notebook.select(self.view_cartao)
            return

        nome_cliente = dados_cartao["cliente_nome"].replace(" ", "_")
        filepath = filedialog.asksaveasfilename(
            initialfile=f"Cartao_Presente_{nome_cliente}.png",
            defaultextension=".png", 
            filetypes=[("Imagens PNG", "*.png"), ("Todos os arquivos", "*.*")]
        )
        if not filepath: return
        
        try:
            sucesso, mensagem = utils.gerar_imagem_cartao(
                nome=dados_cartao["cliente_nome"],
                porcentagem=dados_cartao["valor_desconto_formatado"], 
                data_validade=dados_cartao["data_validade_formatada"], 
                output_path=filepath
            )
            
            if sucesso:
                messagebox.showinfo("Sucesso!", f"Cartão Presente salvo em:\n{filepath}")
                if messagebox.askyesno("Abrir Pasta", "Deseja abrir a pasta do arquivo?"):
                    try: subprocess.Popen(f'explorer /select,"{os.path.normpath(filepath)}"')
                    except Exception as e: messagebox.showerror("Erro", f"Não foi possível abrir a pasta: {e}")
            else:
                messagebox.showerror("Erro ao Gerar Cartão", f"Não foi possível gerar a imagem:\n\n{mensagem}", parent=self.view_cartao)
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado ao gerar imagem do cartão: {e}", parent=self.view_cartao)