import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import END, X, Y, VERTICAL, BOTH, NS, NSEW, EW, CENTER, W, E, LEFT, TOP, BOTTOM, RIGHT, messagebox
from ttkbootstrap.widgets import DateEntry
from .. import utils 
from ..utils import CurrencyEntry, formatar_moeda, string_para_float
from datetime import datetime, timedelta
import calendar

class ComissaoView(ttk.Frame):
    
    def __init__(self, parent, controller):
        super().__init__(parent, padding=15)
        self.controller = controller
        self.model = controller.model 

        self.lista_projetos_cache = []
        self.lista_arquitetos_cache = []
        self.dados_calculo = {} 

        self.notebook = ttk.Notebook(self, bootstyle="primary")
        self.notebook.pack(fill=BOTH, expand=True)

        self.frame_lancamento = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(self.frame_lancamento, text=" 🚀 A Pagar (Pendentes) ")

        self.frame_arquitetos = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(self.frame_arquitetos, text=" 👤 Gerenciar Arquitetos ")

        self.frame_historico = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(self.frame_historico, text=" 📜 Histórico Pagos ")

        self._create_widgets_lancamento(self.frame_lancamento)
        self._create_widgets_arquitetos(self.frame_arquitetos)
        self._create_widgets_historico(self.frame_historico)

    def on_focus(self):
        self.carregar_listas_cache()
        self.popular_tabela_arquitetos()
        self.popular_tabela_comissoes()
        self.popular_tabela_historico()

    def carregar_listas_cache(self):
        try:
            self.lista_projetos_cache = self.model.get_projetos_lancados_para_combobox()
            self.lista_arquitetos_cache = self.model.get_all_arquitetos()
        except Exception as e:
            messagebox.showerror(f"Erro ao carregar dados de cache: {e}", parent=self)

    def _create_widgets_arquitetos(self, parent_frame):
        parent_frame.columnconfigure(0, weight=1)
        parent_frame.rowconfigure(1, weight=1)
        
        form_frame = ttk.Labelframe(parent_frame, text="Novo Arquiteto / Beneficiário", padding=15)
        form_frame.grid(row=0, column=0, sticky=EW, pady=(0, 10))
        form_frame.columnconfigure(1, weight=1)

        ttk.Label(form_frame, text="Nome:").grid(row=0, column=0, sticky=W, padx=5, pady=5)
        self.entry_nome_arquiteto = ttk.Entry(form_frame, width=40)
        self.entry_nome_arquiteto.grid(row=0, column=1, sticky=EW, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Data de Pagamento:").grid(row=0, column=2, sticky=W, padx=(10, 5), pady=5)
        self.entry_data_pag_arquiteto = DateEntry(form_frame, bootstyle="primary", dateformat="%d/%m/%Y", width=12)
        self.entry_data_pag_arquiteto.grid(row=0, column=3, sticky=W, padx=5, pady=5)
        
        btn_salvar_arquiteto = ttk.Button(form_frame, text="Salvar Arquiteto", command=self.salvar_arquiteto, bootstyle="success")
        btn_salvar_arquiteto.grid(row=0, column=4, sticky=E, padx=(10, 5), pady=5)

        tree_frame = ttk.Labelframe(parent_frame, text="Arquitetos Cadastrados", padding=15)
        tree_frame.grid(row=1, column=0, sticky=NSEW)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        self.tree_arquitetos = ttk.Treeview(tree_frame, columns=("id", "nome", "data_pag"), show="headings", height=10)
        self.tree_arquitetos.heading("id", text="ID", anchor=W)
        self.tree_arquitetos.heading("nome", text="Nome", anchor=W)
        self.tree_arquitetos.heading("data_pag", text="Data Pagamento", anchor=CENTER)
        
        self.tree_arquitetos.column("id", width=50, stretch=False)
        self.tree_arquitetos.column("nome", width=300, stretch=True)
        self.tree_arquitetos.column("data_pag", width=110, stretch=False, anchor=CENTER)
        
        self.tree_arquitetos.pack(side=LEFT, fill=BOTH, expand=True)
        
        sb_arq = ttk.Scrollbar(tree_frame, orient=VERTICAL, command=self.tree_arquitetos.yview)
        self.tree_arquitetos.configure(yscrollcommand=sb_arq.set)
        sb_arq.pack(side=RIGHT, fill=Y)

        frame_botoes = ttk.Frame(parent_frame)
        frame_botoes.grid(row=2, column=0, sticky=E, pady=(10, 0))

        btn_edit_arquiteto = ttk.Button(frame_botoes, text="✏️ Editar", command=self.editar_arquiteto, bootstyle="warning-outline")
        btn_edit_arquiteto.pack(side=LEFT, padx=(0, 5)) 

        btn_del_arquiteto = ttk.Button(frame_botoes, text="Remover Arquiteto Selecionado", command=self.remover_arquiteto, bootstyle="danger-outline")
        btn_del_arquiteto.pack(side=LEFT)

    def _create_widgets_historico(self, parent_frame):
        parent_frame.columnconfigure(0, weight=1)
        parent_frame.rowconfigure(1, weight=1)

        frame_top = ttk.Frame(parent_frame)
        frame_top.grid(row=0, column=0, sticky=EW, pady=(0, 10))
        
        self.lbl_total_hist = ttk.Label(frame_top, text="Total Pago: R$ 0,00", font=("Arial", 12, "bold"), bootstyle="success")
        self.lbl_total_hist.pack(side=LEFT)
        
        ttk.Button(frame_top, text="🔄 Atualizar", command=self.popular_tabela_historico, bootstyle="secondary-outline").pack(side=RIGHT)

        cols = ("id", "data", "beneficiario", "projeto", "valor")
        self.tree_hist = ttk.Treeview(parent_frame, columns=cols, show="headings", bootstyle="success")
        
        self.tree_hist.heading("id", text="ID")
        self.tree_hist.heading("data", text="Data Pagamento")
        self.tree_hist.heading("beneficiario", text="Beneficiário")
        self.tree_hist.heading("projeto", text="Projeto")
        self.tree_hist.heading("valor", text="Valor Pago")
        
        self.tree_hist.column("id", width=40, anchor=CENTER)
        self.tree_hist.column("data", width=100, anchor=CENTER)
        self.tree_hist.column("beneficiario", width=200)
        self.tree_hist.column("projeto", width=250)
        self.tree_hist.column("valor", width=120, anchor=E)
        
        self.tree_hist.grid(row=1, column=0, sticky=NSEW)
        
        sb = ttk.Scrollbar(parent_frame, orient=VERTICAL, command=self.tree_hist.yview)
        self.tree_hist.configure(yscroll=sb.set)
        sb.grid(row=1, column=1, sticky=NS)
        
        frame_botoes_hist = ttk.Frame(parent_frame)
        frame_botoes_hist.grid(row=2, column=0, sticky=E, pady=(10, 0))

        btn_edit_hist = ttk.Button(frame_botoes_hist, text="✏️ Editar Histórico", 
                                    command=self.editar_historico_selecionado, 
                                    bootstyle="warning-outline")
        btn_edit_hist.pack(side=LEFT, padx=(0, 5)) 

        btn_del_hist = ttk.Button(frame_botoes_hist, text="🗑️ Remover do Histórico", 
                                   command=self.remover_historico, 
                                   bootstyle="danger-outline")
        btn_del_hist.pack(side=LEFT)

    def popular_tabela_historico(self):
        for i in self.tree_hist.get_children(): self.tree_hist.delete(i)
        try:
            todos = self.model.get_comissoes(filtro_texto="")
            total = 0.0
            hoje = datetime.now().date()
            for row in todos:
                try:
                    dt_obj = datetime.strptime(row['data'], "%d/%m/%Y").date()
                    if dt_obj <= hoje:
                        val = row['valor']
                        total += val
                        proj = f"{row['projeto_nome']} ({row['nome']})" if row['projeto_nome'] else row['nome']
                        val_fmt = formatar_moeda(str(val))
                        self.tree_hist.insert("", END, iid=row['id'], values=(row['id'], row['data'], row['beneficiario'], proj, val_fmt))
                except: pass
            self.lbl_total_hist.config(text=f"Total Pago: {formatar_moeda(str(total))}")
        except Exception as e: print(f"Erro histórico: {e}")

    def popular_tabela_arquitetos(self):
        for item in self.tree_arquitetos.get_children(): self.tree_arquitetos.delete(item)
        try:
            for arq in self.lista_arquitetos_cache:
                self.tree_arquitetos.insert("", END, iid=arq['id'], values=(arq['id'], arq['nome'], arq['data_pagamento_fmt']))
        except Exception as e: messagebox.showerror(f"Erro ao popular tabela arquitetos: {e}", parent=self)

    def salvar_arquiteto(self):
        nome = self.entry_nome_arquiteto.get()
        data_pag = self.entry_data_pag_arquiteto.entry.get()
        if not nome or not data_pag:
            messagebox.showwarning("Campos vazios", "Nome e Data de Pagamento são obrigatórios.", parent=self)
            return
        sucesso, msg = self.model.add_arquiteto(nome, data_pag)
        if sucesso:
            messagebox.showinfo("Sucesso", msg, parent=self)
            self.entry_nome_arquiteto.delete(0, END)
            self.carregar_listas_cache()
            self.popular_tabela_arquitetos()
        else: messagebox.showerror(f"Erro: {msg}", parent=self)

    def remover_arquiteto(self):
        selected = self.tree_arquitetos.selection()
        if not selected: return
        arquiteto_id = selected[0]
        if not messagebox.askyesno("Confirmar", "Tem certeza que deseja remover este arquiteto?", parent=self): return
        try:
            self.model.delete_arquiteto(arquiteto_id)
            self.carregar_listas_cache()
            self.popular_tabela_arquitetos()
        except Exception as e: messagebox.showerror(f"Erro ao remover: {e}", parent=self)

    def editar_arquiteto(self):
        selected = self.tree_arquitetos.selection()
        if not selected: return
        item_values = self.tree_arquitetos.item(selected[0], 'values')
        id_arq = item_values[0]
        nome_atual = item_values[1]
        data_atual_str = item_values[2]
        
        dialog = ttk.Toplevel(self.controller.root)
        dialog.title("Editar Arquiteto")
        dialog.geometry("400x250")
        try:
            x = self.winfo_rootx() + 100; y = self.winfo_rooty() + 100
            dialog.geometry(f"+{x}+{y}")
        except: pass

        ttk.Label(dialog, text="Editar Dados do Parceiro", font=("Arial", 11, "bold")).pack(pady=15)
        ttk.Label(dialog, text="Nome:").pack(fill=X, padx=20)
        ent_nome = ttk.Entry(dialog); ent_nome.pack(fill=X, padx=20, pady=5); ent_nome.insert(0, nome_atual)
        ttk.Label(dialog, text="Data Pagamento:").pack(fill=X, padx=20)
        try: dt_start = datetime.strptime(data_atual_str, "%d/%m/%Y")
        except: dt_start = datetime.now()
        ent_data = DateEntry(dialog, bootstyle="primary", startdate=dt_start, dateformat="%d/%m/%Y")
        ent_data.pack(fill=X, padx=20, pady=5)
        
        def salvar_edicao():
            novo_nome = ent_nome.get(); nova_data = ent_data.entry.get()
            sucesso, msg = self.model.update_arquiteto(id_arq, novo_nome, nova_data)
            if sucesso:
                messagebox.showinfo("Sucesso", msg, parent=dialog)
                self.carregar_listas_cache(); self.popular_tabela_arquitetos(); dialog.destroy()
            else: messagebox.showerror("Erro", msg, parent=dialog)
        ttk.Button(dialog, text="Salvar Alterações", command=salvar_edicao, bootstyle="warning").pack(pady=20, fill=X, padx=20)

    def _create_widgets_lancamento(self, parent_frame):
        parent_frame.columnconfigure(0, weight=1)
        parent_frame.rowconfigure(1, weight=1)

        frame_botoes = ttk.Frame(parent_frame)
        frame_botoes.grid(row=0, column=0, sticky=EW, pady=(0, 10))
        
        btn_add = ttk.Button(frame_botoes, text="➕ Lançar Nova Comissão", command=self.abrir_dialog_comissao, bootstyle="success")
        btn_add.pack(side=LEFT)

        btn_pagar = ttk.Button(frame_botoes, text="💰 Pagar (Baixar)", command=self.realizar_pagamento, bootstyle="warning")
        btn_pagar.pack(side=LEFT, padx=10)
        
        btn_refresh = ttk.Button(frame_botoes, text="🔄 Atualizar Relatório", command=self.on_focus, bootstyle="info-outline")
        btn_refresh.pack(side=RIGHT)

        tree_frame = ttk.Labelframe(parent_frame, text="Comissões a Pagar (Pendentes)", padding=15)
        tree_frame.grid(row=1, column=0, sticky=NSEW)
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        cols = ("data_pag", "arquiteto", "cliente", "projeto", "base", "pct", "valor")
        self.tree_comissoes = ttk.Treeview(tree_frame, columns=cols, show="headings", height=10)
        
        self.tree_comissoes.heading("data_pag", text="Data Pag.")
        self.tree_comissoes.heading("arquiteto", text="Arquiteto")
        self.tree_comissoes.heading("cliente", text="Cliente")
        self.tree_comissoes.heading("projeto", text="Projeto")
        self.tree_comissoes.heading("base", text="Valor Base")
        self.tree_comissoes.heading("pct", text="%")
        self.tree_comissoes.heading("valor", text="Valor Comissão")
        
        self.tree_comissoes.column("data_pag", width=90, anchor=CENTER)
        self.tree_comissoes.column("arquiteto", width=150, anchor=W)
        self.tree_comissoes.column("cliente", width=150, anchor=W)
        self.tree_comissoes.column("projeto", width=200, anchor=W)
        self.tree_comissoes.column("base", width=100, anchor=E)
        self.tree_comissoes.column("pct", width=40, anchor=CENTER)
        self.tree_comissoes.column("valor", width=100, anchor=E)

        self.tree_comissoes.pack(side=LEFT, fill=BOTH, expand=True)
        
        sb_com = ttk.Scrollbar(tree_frame, orient=VERTICAL, command=self.tree_comissoes.yview)
        self.tree_comissoes.configure(yscrollcommand=sb_com.set)
        sb_com.pack(side=RIGHT, fill=Y)

        frame_botoes_rodape = ttk.Frame(parent_frame)
        frame_botoes_rodape.grid(row=2, column=0, sticky=E, pady=(10, 0))

        btn_edit_comissao = ttk.Button(frame_botoes_rodape, text="✏️ Editar Lançamento", 
                                        command=self.editar_comissao_selecionada, 
                                        bootstyle="warning")
        btn_edit_comissao.pack(side=LEFT, padx=(0, 5)) 

        btn_del_comissao = ttk.Button(frame_botoes_rodape, text="Remover Lançamento Selecionado", 
                                        command=self.remover_comissao, 
                                        bootstyle="danger-outline")
        btn_del_comissao.pack(side=LEFT)

    def popular_tabela_comissoes(self):
        for item in self.tree_comissoes.get_children():
            self.tree_comissoes.delete(item)
        try:
            lista = self.model.get_comissoes(filtro_texto="") 
            hoje = datetime.now().date()
            for row in lista:
                try:
                    dt_obj = datetime.strptime(row['data'], "%d/%m/%Y").date()
                    if dt_obj > hoje:
                        valores = (
                            row['data'], row['beneficiario'], row['nome'], row['projeto_nome'],
                            formatar_moeda(str(row['valor_base'])),
                            f"{int(row['porcentagem'])}%" if row['porcentagem'] else "0%",
                            formatar_moeda(str(row['valor']))
                        )
                        self.tree_comissoes.insert("", END, iid=row['id'], values=valores)
                except: pass
        except Exception as e:
            messagebox.showerror(f"Erro ao carregar comissões: {e}", parent=self)

    def realizar_pagamento(self):
        selected = self.tree_comissoes.selection()
        if not selected:
            messagebox.showwarning("Atenção", "Selecione uma comissão para pagar.", parent=self)
            return
        
        comissao_id = selected[0]
        
        if not messagebox.askyesno("Pagar", "Deseja marcar esta comissão como PAGA HOJE?\nEla será movida para o Histórico.", parent=self):
            return
            
        try:
            dados_atuais = self.model.get_comissao_by_id(comissao_id)
            if not dados_atuais:
                messagebox.showerror("Erro", "Comissão não encontrada.", parent=self)
                return
            
            nova_data = datetime.now().strftime("%Y-%m-%d")
            
            self.model.update_comissao(
                comissao_id, nova_data, dados_atuais['cliente_id'], 
                dados_atuais['recebimento_id'], dados_atuais['beneficiario'], 
                dados_atuais['descricao'], dados_atuais['valor'], 
                dados_atuais['porcentagem'], dados_atuais['valor_base']
            )
            
            messagebox.showinfo("Sucesso", "Pagamento registrado com sucesso!", parent=self)
            self.popular_tabela_comissoes()
            self.popular_tabela_historico()
            self.controller.atualizar_aba('home')
        except Exception as e: messagebox.showerror("Erro", f"Erro ao realizar pagamento: {e}", parent=self)
            
    def remover_comissao(self):
        selected = self.tree_comissoes.selection()
        if not selected:
            messagebox.showwarning("Nenhum item selecionado", "Selecione um lançamento na tabela para remover.", parent=self)
            return
        comissao_id = selected[0]
        if not messagebox.askyesno("Confirmar", "Tem certeza que deseja remover este lançamento de comissão?", parent=self): return
        try:
            self.model.delete_comissao(comissao_id)
            self.popular_tabela_comissoes()
            self.popular_tabela_historico()
            self.controller.atualizar_aba('home')
        except Exception as e: messagebox.showerror(f"Erro ao remover: {e}", parent=self)
            
    def editar_comissao_selecionada(self):
        selected = self.tree_comissoes.selection()
        if not selected:
            messagebox.showwarning("Nenhum item selecionado", "Selecione um lançamento na tabela para editar.", parent=self)
            return
        comissao_id = selected[0] 
        self._logica_editar_comissao(comissao_id)

    def editar_historico_selecionado(self):
        selected = self.tree_hist.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um item do histórico para editar.", parent=self)
            return
        comissao_id = selected[0]
        self._logica_editar_comissao(comissao_id)

    def remover_historico(self):
        selected = self.tree_hist.selection()
        if not selected:
            messagebox.showwarning("Aviso", "Selecione um item do histórico para remover.", parent=self)
            return
        comissao_id = selected[0]
        if not messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir este registro histórico?", parent=self): return
        try:
            self.model.delete_comissao(comissao_id)
            self.popular_tabela_comissoes()
            self.popular_tabela_historico()
            self.controller.atualizar_aba('home')
        except Exception as e: messagebox.showerror(f"Erro ao remover: {e}", parent=self)

    def _logica_editar_comissao(self, comissao_id):
        try:
            comissao_data = self.model.get_comissao_by_id(comissao_id)
            if not comissao_data:
                messagebox.showerror("Erro", "Comissão não encontrada no banco de dados.", parent=self)
                return
            self.abrir_dialog_edicao(comissao_data)
        except Exception as e: messagebox.showerror(f"Erro ao buscar dados para edição: {e}", parent=self)
            
    def abrir_dialog_edicao(self, comissao_data):
        dialog = ttk.Toplevel(master=self.controller.root, title=f"Editar Comissão ID {comissao_data['id']}")
        dialog.transient(self.controller.root)
        dialog.grab_set()
        dialog.resizable(False, False)

        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=BOTH, expand=True)
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Arquiteto:").grid(row=0, column=0, sticky=W, padx=5, pady=8)
        combo_arquitetos = ttk.Combobox(frame, state="readonly", width=40)
        combo_arquitetos.grid(row=0, column=1, sticky=EW, padx=5, pady=8)
        
        arquitetos_display = [f"{arq['id']} - {arq['nome']}" for arq in self.lista_arquitetos_cache]
        combo_arquitetos['values'] = arquitetos_display
        
        nome_beneficiario = comissao_data['beneficiario'] or ""
        for item in arquitetos_display:
            if nome_beneficiario in item:
                combo_arquitetos.set(item)
                break

        ttk.Label(frame, text="Projeto (Recebimento):").grid(row=1, column=0, sticky=W, padx=5, pady=8)
        entry_projeto = ttk.Entry(frame, width=40)
        entry_projeto.grid(row=1, column=1, sticky=EW, padx=5, pady=8)
        entry_projeto.insert(0, comissao_data['projeto_nome'] or "N/A")
        entry_projeto.config(state="readonly")
        
        ttk.Label(frame, text="Porcentagem (%):").grid(row=2, column=0, sticky=W, padx=5, pady=8)
        entry_porcentagem = ttk.Spinbox(frame, from_=0, to=100, width=10)
        entry_porcentagem.grid(row=2, column=1, sticky=W, padx=5, pady=8)
        entry_porcentagem.set(comissao_data['porcentagem'] or 0.0)

        lbl_valor_base = ttk.Label(frame, text="Valor Base do Projeto:", bootstyle="secondary")
        lbl_valor_base.grid(row=3, column=0, sticky=W, padx=5, pady=(15, 2))
        lbl_valor_base_val = ttk.Label(frame, text=formatar_moeda(str(comissao_data['valor_base'])), font=("-weight bold"), bootstyle="secondary")
        lbl_valor_base_val.grid(row=3, column=1, sticky=W, padx=5, pady=(15, 2))

        lbl_valor_comissao = ttk.Label(frame, text="Valor da Comissão:", bootstyle="success")
        lbl_valor_comissao.grid(row=4, column=0, sticky=W, padx=5, pady=(2, 15))
        lbl_valor_comissao_val = ttk.Label(frame, text=formatar_moeda(str(comissao_data['valor'])), font=("-weight bold"), bootstyle="success")
        lbl_valor_comissao_val.grid(row=4, column=1, sticky=W, padx=5, pady=(2, 15))
        
        ttk.Label(frame, text="Data Pagamento:").grid(row=5, column=0, sticky=W, padx=5, pady=8)
        try: dt_start = datetime.strptime(comissao_data['data'], "%Y-%m-%d")
        except: dt_start = datetime.now()
        entry_data_edit = DateEntry(frame, bootstyle="primary", startdate=dt_start, dateformat=r"%d/%m/%Y")
        entry_data_edit.grid(row=5, column=1, sticky=W, padx=5, pady=8)

        self.dados_edicao = {"valor_base": comissao_data['valor_base'] or 0.0, "pct": comissao_data['porcentagem'] or 0.0, "valor_final": comissao_data['valor'] or 0.0}

        def atualizar_calculo_edicao(*args):
            try: pct_str = entry_porcentagem.get(); self.dados_edicao["pct"] = float(pct_str) if pct_str else 0.0
            except ValueError: self.dados_edicao["pct"] = 0.0
            self.dados_edicao["valor_final"] = self.dados_edicao["valor_base"] * (self.dados_edicao["pct"] / 100)
            lbl_valor_comissao_val.config(text=formatar_moeda(str(self.dados_edicao["valor_final"])))

        entry_porcentagem.bind("<KeyRelease>", atualizar_calculo_edicao)

        def salvar():
            try:
                arquiteto_str = combo_arquitetos.get()
                if not arquiteto_str:
                    messagebox.showwarning("Campos Obrigatórios", "Arquiteto é obrigatório.", parent=dialog); return
                arquiteto_nome = arquiteto_str.split(" - ", 1)[1] 
                pct_final = self.dados_edicao["pct"]
                valor_final_calc = self.dados_edicao["valor_final"]
                if valor_final_calc <= 0 and pct_final <= 0:
                    messagebox.showwarning("Valor Inválido", "O valor final da comissão ou a porcentagem não pode ser zero.", parent=dialog); return
                
                data_str = entry_data_edit.entry.get()
                data_pag_iso = datetime.strptime(data_str, "%d/%m/%Y").strftime("%Y-%m-%d")
                
                self.model.update_comissao(comissao_id=comissao_data['id'], data=data_pag_iso, beneficiario=arquiteto_nome, valor=valor_final_calc, porcentagem=pct_final, cliente_id=comissao_data['cliente_id'], recebimento_id=comissao_data['recebimento_id'], descricao=comissao_data['descricao'], valor_base=comissao_data['valor_base'])
                
                messagebox.showinfo("Sucesso", f"Comissão ID {comissao_data['id']} atualizada!", parent=dialog)
                self.popular_tabela_comissoes()
                self.popular_tabela_historico()
                self.controller.atualizar_aba('home')
                dialog.destroy()
            except Exception as e: messagebox.showerror("Erro ao Salvar", f"Não foi possível atualizar a comissao: {e}", parent=dialog)

        btn_salvar = ttk.Button(frame, text="✔️ Salvar Alterações", command=salvar, bootstyle="success")
        btn_salvar.grid(row=6, column=0, columnspan=2, pady=15, sticky=E)
        dialog.update_idletasks()
        try:
            x = self.winfo_rootx() + 100; y = self.winfo_rooty() + 100
            dialog.geometry(f"+{x}+{y}")
        except: pass

    def abrir_dialog_comissao(self):
        dialog = ttk.Toplevel(master=self.controller.root, title="Lançar Nova Comissão")
        dialog.transient(self.controller.root)
        dialog.grab_set()
        dialog.resizable(False, False)

        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=BOTH, expand=True)
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Arquiteto:").grid(row=0, column=0, sticky=W, padx=5, pady=8)
        combo_arquitetos = ttk.Combobox(frame, state="readonly", width=40)
        combo_arquitetos.grid(row=0, column=1, sticky=EW, padx=5, pady=8)
        
        arquitetos_display = [f"{arq['id']} - {arq['nome']}" for arq in self.lista_arquitetos_cache]
        combo_arquitetos['values'] = arquitetos_display

        ttk.Label(frame, text="Projeto (Recebimento):").grid(row=1, column=0, sticky=W, padx=5, pady=8)
        combo_projetos = ttk.Combobox(frame, state="readonly", width=40)
        combo_projetos.grid(row=1, column=1, sticky=EW, padx=5, pady=8)
        
        projetos_display = []
        for proj in self.lista_projetos_cache:
            projetos_display.append(f"{proj['id']} - {proj['nome']} - {proj['projeto_nome']}")
        combo_projetos['values'] = projetos_display
        
        ttk.Label(frame, text="Porcentagem (%):").grid(row=2, column=0, sticky=W, padx=5, pady=8)
        entry_porcentagem = ttk.Spinbox(frame, from_=0, to=100, width=10)
        entry_porcentagem.grid(row=2, column=1, sticky=W, padx=5, pady=8)

        lbl_valor_base = ttk.Label(frame, text="Valor Base do Projeto:", bootstyle="secondary")
        lbl_valor_base.grid(row=3, column=0, sticky=W, padx=5, pady=(15, 2))
        lbl_valor_base_val = ttk.Label(frame, text="R$ 0,00", font=("-weight bold"), bootstyle="secondary")
        lbl_valor_base_val.grid(row=3, column=1, sticky=W, padx=5, pady=(15, 2))

        lbl_valor_comissao = ttk.Label(frame, text="Valor da Comissão:", bootstyle="success")
        lbl_valor_comissao.grid(row=4, column=0, sticky=W, padx=5, pady=(2, 15))
        lbl_valor_comissao_val = ttk.Label(frame, text="R$ 0,00", font=("-weight bold"), bootstyle="success")
        lbl_valor_comissao_val.grid(row=4, column=1, sticky=W, padx=5, pady=(2, 15))

        ttk.Label(frame, text="Data Prevista:").grid(row=5, column=0, sticky=W, padx=5, pady=8)
        dt_prevista = DateEntry(frame, bootstyle="primary", dateformat=r"%d/%m/%Y")
        dt_prevista.grid(row=5, column=1, sticky=W, padx=5, pady=8)
        
        self.dados_calculo = {"valor_base": 0.0, "pct": 0.0, "valor_final": 0.0}

        def atualizar_calculo(*args):
            try: pct_str = entry_porcentagem.get(); self.dados_calculo["pct"] = float(pct_str) if pct_str else 0.0
            except ValueError: self.dados_calculo["pct"] = 0.0
            self.dados_calculo["valor_final"] = self.dados_calculo["valor_base"] * (self.dados_calculo["pct"] / 100)
            lbl_valor_base_val.config(text=formatar_moeda(str(self.dados_calculo["valor_base"])))
            lbl_valor_comissao_val.config(text=formatar_moeda(str(self.dados_calculo["valor_final"])))

        def on_projeto_select(event):
            selected_str = combo_projetos.get()
            if not selected_str: self.dados_calculo["valor_base"] = 0.0; atualizar_calculo(); return
            try:
                recebimento_id = int(selected_str.split(" - ")[0])
                detalhes = self.model.get_detalhes_recebimento_para_comissao(recebimento_id)
                self.dados_calculo["valor_base"] = detalhes.get("valor_total", 0.0) if detalhes else 0.0
                atualizar_calculo()
            except: self.dados_calculo["valor_base"] = 0.0; atualizar_calculo()
            
        def on_arquiteto_select(event):
            try:
                arq_str = combo_arquitetos.get()
                if not arq_str: return
                id_arq = int(arq_str.split(" - ")[0])
                
                data_pag_base = None
                for arq in self.lista_arquitetos_cache:
                    if arq['id'] == id_arq:
                        data_pag_base = arq['data_pagamento_fmt']
                        break
                
                if data_pag_base:
                    dia_pag = datetime.strptime(data_pag_base, "%d/%m/%Y").day
                    hoje = datetime.now()
                    
                    if hoje.day > dia_pag:
                        prox_mes = hoje.month + 1
                        ano = hoje.year
                        if prox_mes > 12: prox_mes = 1; ano += 1
                        
                        ultimo_dia = calendar.monthrange(ano, prox_mes)[1]
                        dia_valido = min(dia_pag, ultimo_dia)
                        nova_data = datetime(ano, prox_mes, dia_valido)
                    else:
                        ultimo_dia = calendar.monthrange(hoje.year, hoje.month)[1]
                        dia_valido = min(dia_pag, ultimo_dia)
                        nova_data = datetime(hoje.year, hoje.month, dia_valido)
                        
                    dt_prevista.entry.delete(0, END)
                    dt_prevista.entry.insert(0, nova_data.strftime("%d/%m/%Y"))
            except Exception as e: print(f"Erro calculo data: {e}")

        entry_porcentagem.set("0")
        entry_porcentagem.bind("<KeyRelease>", atualizar_calculo)
        combo_projetos.bind("<<ComboboxSelected>>", on_projeto_select)
        combo_arquitetos.bind("<<ComboboxSelected>>", on_arquiteto_select)

        def salvar():
            try:
                arquiteto_str = combo_arquitetos.get(); projeto_str = combo_projetos.get()
                if not arquiteto_str or not projeto_str: messagebox.showwarning("Campos Obrigatórios", "Arquiteto e Projeto são obrigatórios.", parent=dialog); return
                if self.dados_calculo["valor_final"] <= 0: messagebox.showwarning("Valor Inválido", "O valor final da comissão ou a porcentagem não pode ser zero.", parent=dialog); return
                
                arquiteto_id = int(arquiteto_str.split(" - ")[0])
                arquiteto_nome = arquiteto_str.split(" - ", 1)[1] 
                recebimento_id = int(projeto_str.split(" - ")[0])
                
                cliente_id = None
                for proj in self.lista_projetos_cache:
                    if proj['id'] == recebimento_id: cliente_id = proj['cliente_id']; break
                
                data_pag_str = dt_prevista.entry.get()
                data_pag_iso = datetime.strptime(data_pag_str, "%d/%m/%Y").strftime("%Y-%m-%d")
                
                self.model.add_comissao(data=data_pag_iso, cliente_id=cliente_id, recebimento_id=recebimento_id, beneficiario=arquiteto_nome, descricao=f"Comissão {self.dados_calculo['pct']}% de {projeto_str.split(' - ', 2)[2]}", valor=self.dados_calculo['valor_final'], porcentagem=self.dados_calculo['pct'], valor_base=self.dados_calculo['valor_base'])
                
                messagebox.showinfo("Sucesso", f"Comissão lançada com sucesso!\nPagamento agendado para: {data_pag_str}", parent=dialog)
                self.popular_tabela_comissoes()
                self.controller.atualizar_aba('home')
                dialog.destroy()
            except Exception as e: messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar a comissão: {e}", parent=dialog)

        btn_salvar = ttk.Button(frame, text="✔️ Salvar Lançamento", command=salvar, bootstyle="success")
        btn_salvar.grid(row=6, column=0, columnspan=2, pady=15, sticky=E)

        dialog.update_idletasks()
        try: x = self.winfo_rootx() + 100; y = self.winfo_rooty() + 100; dialog.geometry(f"+{x}+{y}")
        except: pass