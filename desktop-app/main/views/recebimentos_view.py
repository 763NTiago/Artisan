import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, END, X, Y, VERTICAL, BOTH, NS, NSEW, EW, CENTER, W, E, LEFT, TOP, BOTTOM, RIGHT
from ttkbootstrap.widgets import DateEntry
from datetime import datetime
from .. import utils  
from ..utils import CurrencyEntry, formatar_moeda, string_para_float

class RecebimentosView(ttk.Frame):
    
    def __init__(self, parent, controller):
        super().__init__(parent, padding=15)
        self.controller = controller
        self.model = controller.model 
        
        self.lista_clientes_cache = []
        self.lista_parcelas_pendentes_cache = []
        self.lista_agenda_cache = [] 
        
        self.selected_agenda_id = None
        self.selected_cliente_id = None

        self.notebook = ttk.Notebook(self, bootstyle="primary")
        self.notebook.pack(fill=BOTH, expand=True)

        self.frame_lancamento = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(self.frame_lancamento, text=" 🚀 Novo Lançamento ")

        self.frame_baixa = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(self.frame_baixa, text=" 💲 Recebimento Parcelas ")

        self.frame_historico = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(self.frame_historico, text=" 📊 Histórico de Recebimentos ")

        self._create_widgets_lancamento(self.frame_lancamento)
        self._create_widgets_baixa(self.frame_baixa)
        self._create_widgets_historico(self.frame_historico)

    def on_focus(self):
        print("Aba de Recebimentos (Refatorada) ganhou foco.")
        self.carregar_combobox_agenda() 
        self.carregar_combobox_clientes()
        self.popular_tabela_baixa_parcelas()
        self.popular_tabela_historico()

    def _create_widgets_lancamento(self, parent_frame):
        
        parent_frame.columnconfigure(0, weight=1)
        parent_frame.rowconfigure(0, weight=1)

        form_frame = ttk.Labelframe(parent_frame, text=" 1. Novo Lançamento ", padding=20, bootstyle="primary")
        form_frame.grid(row=0, column=0, sticky=NSEW)
        
        form_frame.columnconfigure(1, weight=1)

        ttk.Label(form_frame, text="Puxar da Agenda:", font=("-weight bold")).grid(row=0, column=0, padx=5, pady=8, sticky=W)
        self.lanc_agenda_combo = ttk.Combobox(form_frame, width=40, state="readonly")
        self.lanc_agenda_combo.grid(row=0, column=1, padx=5, pady=8, sticky=EW)
        self.lanc_agenda_combo.bind("<<ComboboxSelected>>", self.on_agenda_select)

        ttk.Label(form_frame, text="Cliente:", font=("-weight bold")).grid(row=1, column=0, padx=5, pady=8, sticky=W)
        self.lanc_cliente_combo = ttk.Combobox(form_frame, width=40, state="disabled")
        self.lanc_cliente_combo.grid(row=1, column=1, padx=5, pady=8, sticky=EW)

        ttk.Label(form_frame, text="Valor Total (R$):", font=("-weight bold")).grid(row=2, column=0, padx=5, pady=8, sticky=W)
        self.lanc_valor_total_entry = CurrencyEntry(form_frame, width=20)
        self.lanc_valor_total_entry.grid(row=2, column=1, padx=5, pady=8, sticky=W)
        
        ttk.Label(form_frame, text="Tipo de Pagamento:", font=("-weight bold")).grid(row=3, column=0, padx=5, pady=8, sticky=W)
        tipos = ["À Vista", "Cartão (Débito)", "Cartão (Crédito)", "Entrada + Parcelas", "Saldo Aberto (Abatimento)"]
        self.lanc_tipo_pag_combo = ttk.Combobox(form_frame, values=tipos, width=20, state="readonly")
        self.lanc_tipo_pag_combo.grid(row=3, column=1, padx=5, pady=8, sticky=W)
        self.lanc_tipo_pag_combo.bind("<<ComboboxSelected>>", self.toggle_parcela_fields)

        self.frame_parcelas = ttk.Frame(form_frame)
        self.frame_parcelas.grid(row=4, column=0, columnspan=2, sticky=EW, pady=10) 
        self.frame_parcelas.columnconfigure(1, weight=1)
        self.frame_parcelas.columnconfigure(3, weight=1)

        self.lbl_total_abatimento = ttk.Label(self.frame_parcelas, text="Valor Total (R$):")
        self.lanc_total_abatimento_display = CurrencyEntry(self.frame_parcelas, width=15, state="disabled")
        
        self.lbl_entrada = ttk.Label(self.frame_parcelas, text="Valor Entrada (R$):")
        self.lanc_entrada_entry = CurrencyEntry(self.frame_parcelas, width=15)
        self.lbl_num_parcelas = ttk.Label(self.frame_parcelas, text="Nº de Parcelas:")
        self.lanc_num_parcelas_entry = ttk.Entry(self.frame_parcelas, width=10)
        self.lbl_valor_parcela = ttk.Label(self.frame_parcelas, text="Valor Parcela (R$):")
        self.lanc_valor_parcela_entry = CurrencyEntry(self.frame_parcelas, width=15)
        self.lbl_data_venc = ttk.Label(self.frame_parcelas, text="Data 1º Venc:")
        self.lbl_data_inicio = ttk.Label(self.frame_parcelas, text="Data de Início:") 
        self.lanc_data_venc_entry = DateEntry(self.frame_parcelas, bootstyle="primary", dateformat="%d/%m/%Y", width=12)

        frame_botoes = ttk.Frame(form_frame)
        frame_botoes.grid(row=5, column=0, columnspan=2, sticky=E, pady=20) 
        
        self.btn_lanc_limpar = ttk.Button(frame_botoes, text="✖️ Limpar", command=self.limpar_form_lancamento, bootstyle="secondary-outline")
        self.btn_lanc_limpar.pack(side=LEFT, padx=5)
        
        self.btn_lanc_salvar = ttk.Button(frame_botoes, text="✔️ Salvar Lançamento", command=self.salvar_novo_lancamento, bootstyle="success")
        self.btn_lanc_salvar.pack(side=LEFT, padx=5)
        
        self.toggle_parcela_fields()

    def carregar_combobox_agenda(self):
        try:
            self.lista_agenda_cache = self.model.get_projetos_agenda_para_combobox()
            display_list = ["Nenhum (Lançamento Manual)"]
            
            for item in self.lista_agenda_cache:
                cliente_nome = item['nome']
                projeto_desc = item['descricao']
                
                if cliente_nome and projeto_desc: 
                    display_list.append(f"{item['id']} - {cliente_nome} - {projeto_desc}")
                
            self.lanc_agenda_combo['values'] = display_list
            self.lanc_agenda_combo.set("Nenhum (Lançamento Manual)")
        except Exception as e:
            print(f"Erro ao carregar agenda: {e}")
            messagebox.showerror(f"Erro ao carregar lista da agenda: {e}", parent=self)

    def on_agenda_select(self, event=None):
        
        selecionado_raw = self.lanc_agenda_combo.get()
        self.lanc_cliente_combo.config(state="normal")
        
        if selecionado_raw == "Nenhum (Lançamento Manual)":
            self.lanc_cliente_combo.set("")
            self.lanc_cliente_combo.config(state="disabled")
            self.lanc_valor_total_entry.set_value(0.0)
            self.selected_agenda_id = None
            self.selected_cliente_id = None
            return

        try:
            agenda_id = int(selecionado_raw.split(" - ")[0])
            
            valor_total_orcamento = self.model.get_valor_total_by_agenda_id(agenda_id)
            self.lanc_valor_total_entry.set_value(valor_total_orcamento)
            
            for item in self.lista_agenda_cache:
                if item['id'] == agenda_id:
                    self.selected_agenda_id = item['id']
                    self.selected_cliente_id = item['id_cliente']
                    
                    cliente_id_str = f"{item['id_cliente']} - {item['nome']}"
                    
                    self.lanc_cliente_combo.set(cliente_id_str)
                    self.lanc_cliente_combo.config(state="disabled")
                    break 
                    
        except Exception as e:
            print(f"Erro ao selecionar agenda: {e}")
            self.lanc_cliente_combo.set("")
            self.lanc_cliente_combo.config(state="disabled")
            self.lanc_valor_total_entry.set_value(0.0)
            self.selected_agenda_id = None
            self.selected_cliente_id = None

    def carregar_combobox_clientes(self):
        pass

    def toggle_parcela_fields(self, event=None):
        
        tipo_selecionado = self.lanc_tipo_pag_combo.get()
        valor_total = self.lanc_valor_total_entry.get_value()
        
        self.lanc_total_abatimento_display.set_value(valor_total)

        self.lbl_total_abatimento.grid_remove() 
        self.lanc_total_abatimento_display.grid_remove() 
        self.lbl_entrada.grid_remove()
        self.lanc_entrada_entry.grid_remove()
        self.lbl_num_parcelas.grid_remove()
        self.lanc_num_parcelas_entry.grid_remove()
        self.lbl_valor_parcela.grid_remove()
        self.lanc_valor_parcela_entry.grid_remove()
        self.lbl_data_venc.grid_remove()
        self.lbl_data_inicio.grid_remove() 
        self.lanc_data_venc_entry.grid_remove()

        if tipo_selecionado == "Entrada + Parcelas":
            self.lbl_entrada.grid(row=0, column=0, padx=5, pady=5, sticky=W)
            self.lanc_entrada_entry.grid(row=0, column=1, padx=5, pady=5, sticky=W)
            self.lbl_num_parcelas.grid(row=1, column=0, padx=5, pady=5, sticky=W)
            self.lanc_num_parcelas_entry.grid(row=1, column=1, padx=5, pady=5, sticky=W)
            self.lbl_valor_parcela.grid(row=0, column=2, padx=(10,5), pady=5, sticky=W)
            self.lanc_valor_parcela_entry.grid(row=0, column=3, padx=5, pady=5, sticky=W)
            self.lbl_data_venc.grid(row=1, column=2, padx=(10,5), pady=5, sticky=W) 
            self.lanc_data_venc_entry.grid(row=1, column=3, padx=5, pady=5, sticky=W)

        elif tipo_selecionado == "Cartão (Crédito)":
            self.lbl_num_parcelas.grid(row=1, column=0, padx=5, pady=5, sticky=W)
            self.lanc_num_parcelas_entry.grid(row=1, column=1, padx=5, pady=5, sticky=W)
            self.lbl_valor_parcela.grid(row=0, column=0, padx=5, pady=5, sticky=W)
            self.lanc_valor_parcela_entry.grid(row=0, column=1, padx=5, pady=5, sticky=W)
            self.lbl_data_venc.grid(row=0, column=2, padx=(10,5), pady=5, sticky=W) 
            self.lanc_data_venc_entry.grid(row=0, column=3, padx=5, pady=5, sticky=W)
        
        elif tipo_selecionado == "Saldo Aberto (Abatimento)":
            self.lbl_total_abatimento.grid(row=0, column=0, padx=5, pady=5, sticky=W)
            self.lanc_total_abatimento_display.grid(row=0, column=1, padx=5, pady=5, sticky=W)
            self.lbl_entrada.grid(row=1, column=0, padx=5, pady=5, sticky=W)
            self.lanc_entrada_entry.grid(row=1, column=1, padx=5, pady=5, sticky=W)
            self.lbl_data_inicio.grid(row=2, column=0, padx=(5,5), pady=5, sticky=W) 
            self.lanc_data_venc_entry.grid(row=2, column=1, padx=5, pady=5, sticky=W)
            
    def limpar_form_lancamento(self):
        self.lanc_agenda_combo.set("Nenhum (Lançamento Manual)") 
        
        self.lanc_cliente_combo.config(state="normal")
        self.lanc_cliente_combo.set("")
        self.lanc_cliente_combo.config(state="disabled")
        
        self.selected_agenda_id = None
        self.selected_cliente_id = None
        
        self.lanc_valor_total_entry.set_value(0.0) 
        self.lanc_tipo_pag_combo.set("")
        self.lanc_entrada_entry.set_value(0.0)
        self.lanc_num_parcelas_entry.delete(0, END)
        self.lanc_valor_parcela_entry.set_value(0.0)
        self.toggle_parcela_fields()

    def salvar_novo_lancamento(self):
        try:
            tipo_pagamento = self.lanc_tipo_pag_combo.get()
            agenda_id = self.selected_agenda_id
            cliente_id = self.selected_cliente_id
            
            if not agenda_id or not cliente_id or not tipo_pagamento:
                messagebox.showwarning("Campos Obrigatórios", "Projeto (Agenda) e Tipo de Pagamento são obrigatórios.", parent=self)
                return
            
            valor_total_float = self.lanc_valor_total_entry.get_value()
            
            dados = {
                "cliente_id": cliente_id,
                "agenda_id": agenda_id,
                "tipo_pagamento": tipo_pagamento,
                "valor_total": valor_total_float,
                "valor_entrada": 0.0,
                "num_parcelas": 0,
                "valor_parcela": 0.0,
                "data_1_venc": None 
            }

            if tipo_pagamento == "Entrada + Parcelas":
                dados["valor_entrada"] = self.lanc_entrada_entry.get_value()
                dados["num_parcelas"] = utils.string_para_int(self.lanc_num_parcelas_entry.get())
                dados["valor_parcela"] = self.lanc_valor_parcela_entry.get_value()
                dados["data_1_venc"] = self.lanc_data_venc_entry.entry.get()
                
            elif tipo_pagamento == "Cartão (Crédito)":
                dados["valor_entrada"] = 0.0
                dados["num_parcelas"] = utils.string_para_int(self.lanc_num_parcelas_entry.get())
                dados["valor_parcela"] = self.lanc_valor_parcela_entry.get_value()
                dados["data_1_venc"] = self.lanc_data_venc_entry.entry.get()
            
            elif tipo_pagamento == "Saldo Aberto (Abatimento)":
                dados["valor_entrada"] = self.lanc_entrada_entry.get_value()
                valor_restante = valor_total_float - dados["valor_entrada"]
                dados["num_parcelas"] = 1 
                dados["valor_parcela"] = valor_restante
                dados["data_1_venc"] = self.lanc_data_venc_entry.entry.get() 
            
            self.model.add_recebimento_pagamento(dados)
            
            messagebox.showinfo("Sucesso", "Novo pagamento lançado com sucesso!", parent=self)
            self.limpar_form_lancamento()
            
            self.carregar_combobox_agenda() 
            self.popular_tabela_baixa_parcelas() 
            
            self.popular_tabela_historico() 
            
            self.controller.atualizar_aba('comissao')
            self.controller.atualizar_aba('home')
            self.notebook.select(self.frame_baixa) 

        except Exception as e:
            messagebox.showerror(f"Erro ao salvar lançamento: {e}", parent=self)
            print(f"Erro detalhado ao salvar: {e}")

    def _create_widgets_baixa(self, parent_frame):
        
        parent_frame.rowconfigure(0, weight=1)
        parent_frame.columnconfigure(0, weight=1)

        tabela_frame_principal = ttk.Labelframe(parent_frame, text=" 2. Parcelas Pendentes (Valores em Aberto) ", padding=15, bootstyle="primary")
        tabela_frame_principal.grid(row=0, column=0, sticky=NSEW)
        tabela_frame_principal.rowconfigure(1, weight=1)
        tabela_frame_principal.columnconfigure(0, weight=1)

        frame_filtro = ttk.Frame(tabela_frame_principal)
        frame_filtro.grid(row=0, column=0, sticky=EW, pady=(0, 10))
        
        lbl_filtro = ttk.Label(frame_filtro, text="Buscar Cliente ou Projeto:")
        lbl_filtro.pack(side=LEFT, padx=(0, 5))

        self.search_var_baixa = ttk.StringVar()
        self.search_var_baixa.trace_add("write", self.filtrar_tabela_baixa)
        
        entry_filtro = ttk.Entry(frame_filtro, textvariable=self.search_var_baixa, width=40)
        entry_filtro.pack(side=LEFT, fill=X, expand=True, padx=5)
        
        self.btn_atualizar_baixa = ttk.Button(
            frame_filtro, 
            text="🔄 Atualizar", 
            command=self.popular_tabela_baixa_parcelas, 
            bootstyle="info-outline"
        )
        self.btn_atualizar_baixa.pack(side=RIGHT, padx=5)

        frame_tabela = ttk.Frame(tabela_frame_principal)
        frame_tabela.grid(row=1, column=0, sticky=NSEW, pady=5)
        frame_tabela.rowconfigure(0, weight=1)
        frame_tabela.columnconfigure(0, weight=1)
        
        colunas = {"id": ("ID", 0), "cliente": ("Cliente", 180), "projeto": ("Projeto", 180),
                   "parcela": ("Parcela", 130), 
                   "valor": ("Valor Restante (R$)", 110),
                   "vencimento": ("Vencimento", 90)}
        
        self.tree_baixa_parcelas = ttk.Treeview(frame_tabela, columns=list(colunas.keys()), show="headings", height=10, bootstyle="primary")
        
        for col_id, (text, width) in colunas.items():
            self.tree_baixa_parcelas.heading(col_id, text=text, anchor=W)
            self.tree_baixa_parcelas.column(col_id, width=width, anchor=W, stretch=False if width > 0 else True)

        scrollbar_y = ttk.Scrollbar(frame_tabela, orient=VERTICAL, command=self.tree_baixa_parcelas.yview)
        self.tree_baixa_parcelas.configure(yscrollcommand=scrollbar_y.set)
        
        scrollbar_y.pack(side=RIGHT, fill=Y)
        self.tree_baixa_parcelas.pack(side=LEFT, fill=BOTH, expand=True)
        
        self.tree_baixa_parcelas.bind("<<TreeviewSelect>>", self.on_parcela_select_baixa)

        frame_acao = ttk.Frame(tabela_frame_principal)
        frame_acao.grid(row=2, column=0, sticky=EW, pady=(10, 0))

        lbl_data = ttk.Label(frame_acao, text="Data de Recebimento:")
        lbl_data.pack(side=LEFT, padx=(0, 5))
        
        self.data_pagamento_entry = DateEntry(frame_acao, bootstyle="danger", dateformat="%d/%m/%Y")
        self.data_pagamento_entry.pack(side=LEFT, padx=5)
        
        lbl_valor_pago = ttk.Label(frame_acao, text="Valor Recebido (R$):")
        lbl_valor_pago.pack(side=LEFT, padx=(10, 5))
        
        self.valor_pago_entry = CurrencyEntry(frame_acao, width=15, bootstyle="danger")
        self.valor_pago_entry.pack(side=LEFT, padx=5)
        
        self.btn_marcar_paga = ttk.Button(
            frame_acao, 
            text="💲 Confirmar Recebimento", 
            command=self.on_confirmar_recebimento, 
            bootstyle="success" 
        )
        self.btn_marcar_paga.pack(side=RIGHT, padx=5)
        
        self.btn_editar_parcela_pendente = ttk.Button(
            frame_acao, 
            text="✏️ Editar Parcela", 
            command=lambda: self.editar_parcela_selecionada(paga=False), 
            bootstyle="warning" 
        )
        self.btn_editar_parcela_pendente.pack(side=RIGHT, padx=5)


    def popular_tabela_baixa_parcelas(self):
        try:
            self.lista_parcelas_pendentes_cache = self.model.get_todas_parcelas_pendentes_detalhadas()
            self.search_var_baixa.set("") 
            self.valor_pago_entry.set_value(0.0)
            self.filtrar_tabela_baixa()
        except Exception as e:
            messagebox.showerror(f"Erro ao buscar parcelas pendentes: {e}", parent=self)

    def filtrar_tabela_baixa(self, *args):
        for item in self.tree_baixa_parcelas.get_children():
            self.tree_baixa_parcelas.delete(item)
            
        termo_busca = self.search_var_baixa.get().lower()

        for parcela in self.lista_parcelas_pendentes_cache:
            
            cliente_nome = str(parcela['nome']).lower()
            projeto_nome = str(parcela['projeto_nome']).lower()
            
            if termo_busca in cliente_nome or termo_busca in projeto_nome:
                parcela_id = parcela['id']
                valores_formatados = (
                    parcela_id, 
                    parcela['nome'], 
                    parcela['projeto_nome'], 
                    parcela['nome_parcela'],
                    utils.formatar_moeda(str(parcela['valor_restante'])), 
                    parcela['data_vencimento']
                )
                self.tree_baixa_parcelas.insert(parent="", index=END, iid=parcela_id, values=valores_formatados)

    def on_parcela_select_baixa(self, event=None):
        selected_iids = self.tree_baixa_parcelas.selection()
        if not selected_iids:
            return
        
        selected_iid = selected_iids[0]
        parcela_id = int(selected_iid)

        valor_restante_parcela = 0.0
        for p in self.lista_parcelas_pendentes_cache:
            if p['id'] == parcela_id:
                valor_restante_parcela = p['valor_restante'] 
                break
        
        self.valor_pago_entry.set_value(valor_restante_parcela)

    def on_confirmar_recebimento(self):
        selected_iids = self.tree_baixa_parcelas.selection()
        if not selected_iids:
            messagebox.showwarning("Nenhuma parcela selecionada", "Por favor, selecione uma parcela na tabela.", parent=self)
            return
            
        selected_iid = selected_iids[0]
        
        try:
            item_data = self.tree_baixa_parcelas.item(selected_iid)
            item_values = item_data['values']
            
            parcela_id = int(selected_iid)
            nome_cliente = item_values[1]
            nome_parcela = item_values[3]
            
            valor_pago = self.valor_pago_entry.get_value()
            
            if valor_pago <= 0:
                 messagebox.showwarning("Valor Inválido", "O valor a ser pago não pode ser zero.", parent=self)
                 return
            
            data_pagamento = self.data_pagamento_entry.entry.get()
            
            msg_confirm = (
                f"Cliente: {nome_cliente}\nParcela: {nome_parcela}\n"
                f"Valor: {utils.formatar_moeda(str(valor_pago))}\nData: {data_pagamento}\n\n"
                "Confirmar o recebimento?"
            )
            
            if not messagebox.askyesno("Confirmar Recebimento", msg_confirm, parent=self):
                return

            self.model.receber_parcela(parcela_id, data_pagamento, valor_pago)
            
            messagebox.showinfo("Sucesso", "Pagamento/Abatimento registrado!", parent=self)
            
            self.popular_tabela_baixa_parcelas()
            self.popular_tabela_historico() 
            self.controller.atualizar_aba('home')

        except Exception as e:
            print(f"Erro ao marcar parcela como paga: {e}")
            messagebox.showerror(f"Erro ao salvar: {e}", parent=self)

    def _create_widgets_historico(self, parent_frame):
        
        parent_frame.rowconfigure(0, weight=1)
        parent_frame.columnconfigure(0, weight=1)

        tabela_frame_historico = ttk.Labelframe(parent_frame, text=" 3. Histórico de Recebimentos (Concluídos) ", padding=15, bootstyle="secondary")
        tabela_frame_historico.grid(row=0, column=0, sticky=NSEW)
        tabela_frame_historico.rowconfigure(0, weight=1)
        tabela_frame_historico.columnconfigure(0, weight=1)
        
        frame_tabela_hist = ttk.Frame(tabela_frame_historico)
        frame_tabela_hist.grid(row=0, column=0, sticky=NSEW)
        frame_tabela_hist.rowconfigure(0, weight=1)
        frame_tabela_hist.columnconfigure(0, weight=1)

        colunas = {"id": ("ID", 0), "cliente": ("Cliente", 180), "projeto": ("Projeto", 180),
                   "parcela": ("Parcela", 130), 
                   "valor": ("Valor Pago (R$)", 110),
                   "data_pag": ("Data Pagamento", 90)}
        
        self.tree_historico = ttk.Treeview(frame_tabela_hist, columns=list(colunas.keys()), show="headings", height=10, bootstyle="secondary")
        
        for col_id, (text, width) in colunas.items():
            self.tree_historico.heading(col_id, text=text, anchor=W)
            self.tree_historico.column(col_id, width=width, anchor=W, stretch=False if width > 0 else True)

        scrollbar_y = ttk.Scrollbar(frame_tabela_hist, orient=VERTICAL, command=self.tree_historico.yview)
        self.tree_historico.configure(yscrollcommand=scrollbar_y.set)
        
        scrollbar_y.pack(side=RIGHT, fill=Y)
        self.tree_historico.pack(side=LEFT, fill=BOTH, expand=True)

        frame_botoes_hist = ttk.Frame(tabela_frame_historico)
        frame_botoes_hist.grid(row=1, column=0, sticky=E, pady=(10, 0))

        self.btn_editar_parcela_paga = ttk.Button(
            frame_botoes_hist, 
            text="✏️ Editar Lançamento Pago", 
            command=lambda: self.editar_parcela_selecionada(paga=True), 
            bootstyle="secondary" 
        )
        self.btn_editar_parcela_paga.pack(side=RIGHT, padx=5)

    def popular_tabela_historico(self):
        for item in self.tree_historico.get_children():
            self.tree_historico.delete(item)
        try:
            
            lista_pagas = self.model.get_todas_parcelas_pagas_detalhadas() 

            for parcela in lista_pagas:
                parcela_id = parcela['id']
                valores_formatados = (
                    parcela_id, 
                    parcela['nome'], 
                    parcela['projeto_nome'], 
                    parcela['nome_parcela'],
                    utils.formatar_moeda(str(parcela['valor_pago'])), 
                    parcela['data_pagamento']
                )
                self.tree_historico.insert(parent="", index=END, iid=parcela_id, values=valores_formatados)
                
        except AttributeError as ae:
             if "'Model' object has no attribute 'get_todas_parcelas_pagas_detalhadas'" in str(ae):
                print("Aviso: A função 'get_todas_parcelas_pagas_detalhadas' ainda não foi implementada no model.py.")
             else:
                messagebox.showerror(f"Erro ao buscar histórico (Atributo): {ae}", parent=self)
        except Exception as e:
             messagebox.showerror(f"Erro ao buscar histórico de parcelas: {e}", parent=self)

    def get_selected_parcela_id(self, tree_widget):
        selected_iids = tree_widget.selection()
        if not selected_iids:
            messagebox.showwarning("Nenhuma parcela selecionada", 
                                    "Por favor, selecione uma parcela na tabela para editar.", 
                                    parent=self)
            return None
        
        try:
            parcela_id = int(selected_iids[0])
            return parcela_id
        except Exception as e:
            messagebox.showerror(f"Erro ao ler ID da seleção: {e}", parent=self)
            return None

    def editar_parcela_selecionada(self, paga=False):
        if paga:
            tree_alvo = self.tree_historico
        else:
            tree_alvo = self.tree_baixa_parcelas
            
        parcela_id = self.get_selected_parcela_id(tree_alvo)
        if not parcela_id:
            return
            
        try:
            parcela_data = self.model.get_parcela_by_id(parcela_id)
            if not parcela_data:
                messagebox.showerror("Erro", "Parcela não encontrada no banco de dados.", parent=self)
                return
            
            self.abrir_dialog_edicao_parcela(parcela_data, paga)
            
        except Exception as e:
            messagebox.showerror(f"Erro ao buscar dados da parcela: {e}", parent=self)

    def abrir_dialog_edicao_parcela(self, parcela_data, paga=False):
        dialog = ttk.Toplevel(self.winfo_toplevel())
        dialog.title(f"Editar Parcela ID {parcela_data['id']}")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        
        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=BOTH, expand=True)
        frame.columnconfigure(1, weight=1)
        
        ttk.Label(frame, text="Data Vencimento:").grid(row=0, column=0, padx=5, pady=8, sticky=W)
        entry_data_venc = DateEntry(frame, bootstyle="primary", dateformat="%d/%m/%Y")
        try:
            data_db = datetime.strptime(parcela_data['data_vencimento'], "%Y-%m-%d").date()
            entry_data_venc.entry.delete(0, END)
            entry_data_venc.entry.insert(0, data_db.strftime("%d/%m/%Y"))
        except:
             pass 
        entry_data_venc.grid(row=0, column=1, padx=5, pady=8, sticky=W)
        
        ttk.Label(frame, text="Valor da Parcela (R$):").grid(row=1, column=0, padx=5, pady=8, sticky=W)
        entry_valor_parcela = CurrencyEntry(frame, width=20)
        entry_valor_parcela.set_value(parcela_data['valor_parcela'])
        entry_valor_parcela.grid(row=1, column=1, padx=5, pady=8, sticky=W)

        entry_valor_recebido = None 
        
        if paga:
            ttk.Label(frame, text="Valor Recebido (R$):", bootstyle="success").grid(row=2, column=0, padx=5, pady=8, sticky=W)
            entry_valor_recebido = CurrencyEntry(frame, width=20, bootstyle="success")
            entry_valor_recebido.set_value(parcela_data['valor_recebido'] or 0.0)
            entry_valor_recebido.grid(row=2, column=1, padx=5, pady=8, sticky=W)

        def salvar_edicao_parcela():
            try:
                data_venc_str = entry_data_venc.entry.get()
                valor_parcela_float = entry_valor_parcela.get_value()
                
                valor_recebido_float = None
                if paga and entry_valor_recebido:
                    valor_recebido_float = entry_valor_recebido.get_value()
                
                if valor_parcela_float <= 0:
                     messagebox.showwarning("Valor Inválido", "O valor da parcela deve ser maior que zero.", parent=dialog)
                     return

                sucesso = self.model.update_parcela_details(
                    parcela_id=parcela_data['id'],
                    nova_data_venc=data_venc_str,
                    novo_valor=valor_parcela_float,
                    novo_valor_recebido=valor_recebido_float
                )
                
                if sucesso:
                    messagebox.showinfo("Sucesso", "Parcela atualizada!", parent=dialog)
                    self.popular_tabela_baixa_parcelas()
                    self.popular_tabela_historico()
                    self.controller.atualizar_aba('home')
                    dialog.destroy()
                else:
                    messagebox.showerror("Erro DB", "Não foi possível salvar as alterações no banco de dados.", parent=dialog)
            
            except Exception as e:
                 messagebox.showerror("Erro ao Salvar", f"Não foi possível atualizar a parcela: {e}", parent=dialog)
        
        btn_salvar = ttk.Button(frame, text="✔️ Salvar Alterações", 
                                command=salvar_edicao_parcela, 
                                bootstyle="success")
        btn_salvar.grid(row=3, column=0, columnspan=2, pady=15, sticky=E)

        dialog.update_idletasks()
        try:
            main_app = self.controller.root
            main_x = main_app.winfo_x()
            main_y = main_app.winfo_y()
            main_width = main_app.winfo_width()
            main_height = main_app.winfo_height()
            dialog_width = dialog.winfo_width()
            dialog_height = dialog.winfo_height()
            center_x = main_x + (main_width // 2) - (dialog_width // 2)
            center_y = main_y + (main_height // 2) - (dialog_height // 2)
            dialog.geometry(f"+{center_x}+{center_y}")
        except Exception:
            pass 
        dialog.focus_force()