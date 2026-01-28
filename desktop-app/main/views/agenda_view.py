import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import DateEntry
from tkinter import messagebox, END, X, Y, VERTICAL, BOTH, NS, NSEW, EW, CENTER, W, E, LEFT, TOP, BOTTOM, RIGHT
from .. import utils
from datetime import datetime
import json

class AgendaView(ttk.Frame):
    
    def __init__(self, parent, controller):
        super().__init__(parent, padding=15)
        self.controller = controller
        self.model = controller.model 
        
        self.lista_clientes_cache = []
        self.lista_orcamentos_cache = []
        
        self.setup_calendar_styles()
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        frame_superior = ttk.Frame(self)
        frame_superior.grid(row=0, column=0, sticky=EW, pady=(0, 15))
        
        self.btn_add_projeto = ttk.Button(frame_superior, text="➕ Novo Projeto na Agenda", 
                                        command=self.abrir_dialog_projeto, bootstyle="success")
        self.btn_add_projeto.pack(side=LEFT, padx=(0, 10))
        
        self.btn_edit_projeto = ttk.Button(frame_superior, text="✏️ Editar Selecionado", 
                                         command=self.editar_projeto_selecionado, bootstyle="info")
        self.btn_edit_projeto.pack(side=LEFT, padx=10)
        
        self.btn_del_projeto = ttk.Button(frame_superior, text="🗑️ Remover Selecionado", 
                                         command=self.remover_projeto_selecionado, bootstyle="danger-outline")
        self.btn_del_projeto.pack(side=LEFT, padx=10)
        
        frame_filtros = ttk.Frame(frame_superior)
        frame_filtros.pack(side=RIGHT)
        
        self.btn_filtro_todos = ttk.Button(frame_filtros, text="Todos", command=self.popular_tabela_agenda, bootstyle="secondary")
        self.btn_filtro_todos.pack(side=LEFT, padx=5)

        self.btn_filtro_hoje = ttk.Button(frame_filtros, text="Hoje", command=self.filtrar_agenda_hoje, bootstyle="secondary")
        self.btn_filtro_hoje.pack(side=LEFT, padx=5)

        self.btn_filtro_semana = ttk.Button(frame_filtros, text="Esta Semana", command=self.filtrar_agenda_semana, bootstyle="secondary")
        self.btn_filtro_semana.pack(side=LEFT, padx=5)

        self.btn_filtro_mes = ttk.Button(frame_filtros, text="Este Mês", command=self.filtrar_agenda_mes, bootstyle="secondary")
        self.btn_filtro_mes.pack(side=LEFT, padx=5)
        
        self.entry_data_filtro = DateEntry(frame_filtros, bootstyle="primary", dateformat="%d/%m/%Y")
        self.entry_data_filtro.pack(side=LEFT, padx=5)

        self.btn_buscar_data = ttk.Button(frame_filtros, text="Buscar Data", command=self.buscar_agenda_por_data, bootstyle="primary")
        self.btn_buscar_data.pack(side=LEFT, padx=5)

        frame_tabela = ttk.Frame(self)
        frame_tabela.grid(row=1, column=0, sticky=NSEW)
        frame_tabela.rowconfigure(0, weight=1)
        frame_tabela.columnconfigure(0, weight=1)

        cols = ("id", "cliente", "data_inicio", "data_termino", "descricao")
        self.tree_agenda = ttk.Treeview(frame_tabela, columns=cols, show="headings", height=10, bootstyle="primary")
        
        self.tree_agenda.heading("id", text="ID")
        self.tree_agenda.heading("cliente", text="Cliente")
        self.tree_agenda.heading("data_inicio", text="Data Início")
        self.tree_agenda.heading("data_termino", text="Data Término")
        self.tree_agenda.heading("descricao", text="Descrição do Projeto")

        self.tree_agenda.column("id", width=40, anchor=CENTER)
        self.tree_agenda.column("cliente", width=180)
        self.tree_agenda.column("data_inicio", width=100, anchor=CENTER)
        self.tree_agenda.column("data_termino", width=100, anchor=CENTER)
        self.tree_agenda.column("descricao", width=350)

        scrollbar_y = ttk.Scrollbar(frame_tabela, orient=VERTICAL, command=self.tree_agenda.yview)
        self.tree_agenda.configure(yscrollcommand=scrollbar_y.set)
        
        scrollbar_y.pack(side=RIGHT, fill=Y)
        self.tree_agenda.pack(side=LEFT, fill=BOTH, expand=True)
        
    def setup_calendar_styles(self):
        try:
            style = ttk.Style.get_instance()
            
            style.configure("TCalendar", font=("Arial", 9))
            style.configure("calendar.WeekDay.TLabel", foreground="#333333") 
            style.configure("calendar.Day.TButton", foreground="#000000") 
            
            style.configure("calendar.Saturday.TButton", foreground="#007bff", font=("-weight", "bold"))
            style.configure("calendar.Sunday.TButton", foreground="#dc3545", font=("-weight", "bold"))
            
            style.map("calendar.DateMark.TButton",
                      background=[('pressed', '#17a2b8'), ('selected', '#17a2b8'), ('!selected', '#17a2b8')],
                      foreground=[('!selected', '#ffffff')])
                      
            style.map("calendar.DateMark.danger.TButton",
                      background=[('pressed', '#dc3545'), ('selected', '#dc3545'), ('!selected', '#dc3545')],
                      foreground=[('!selected', '#ffffff')])
                      
            style.map("calendar.DateMark.info.TButton",
                      background=[('pressed', '#007bff'), ('selected', '#007bff'), ('!selected', '#007bff')],
                      foreground=[('!selected', '#ffffff')])

        except Exception as e:
            print(f"Erro ao aplicar estilo do calendário: {e}")

    def on_focus(self):
        self.popular_tabela_agenda()

    def popular_tabela_agenda(self, lista_projetos=None):
        for item in self.tree_agenda.get_children():
            self.tree_agenda.delete(item)
        
        try:
            if lista_projetos is None:
                lista_projetos = self.model.get_agenda()
            
            for row in lista_projetos:
                
                id_projeto = row[0]
                cliente_nome = row[1]
                data_inicio = row[2]
                data_termino = row[3]
                descricao = row[4]
                
                valores_para_tabela = (id_projeto, cliente_nome, data_inicio, data_termino, descricao)
                
                self.tree_agenda.insert("", END, iid=id_projeto, values=valores_para_tabela)
                
        except Exception as e:
            messagebox.showerror("Erro DB", f"Não foi possível carregar a agenda: {e}", parent=self)

    def filtrar_agenda_hoje(self):
        try:
            resultados = self.model.get_agenda(filtro_data="hoje")
            self.popular_tabela_agenda(resultados)
        except Exception as e:
            messagebox.showerror("Erro DB", f"Não foi possível filtrar por 'hoje': {e}", parent=self)

    def filtrar_agenda_semana(self):
        try:
            resultados = self.model.get_agenda(filtro_data="semana")
            self.popular_tabela_agenda(resultados)
        except Exception as e:
            messagebox.showerror("Erro DB", f"Não foi possível filtrar por 'semana': {e}", parent=self)

    def filtrar_agenda_mes(self):
        try:
            resultados = self.model.get_agenda(filtro_data="mes")
            self.popular_tabela_agenda(resultados)
        except Exception as e:
            messagebox.showerror("Erro DB", f"Não foi possível filtrar por 'mês': {e}", parent=self)

    def buscar_agenda_por_data(self):
        data_selecionada = self.entry_data_filtro.entry.get()
        if not data_selecionada:
            self.popular_tabela_agenda()
            return
        
        try:
            data_iso = datetime.strptime(data_selecionada, "%d/%m/%Y").strftime("%Y-%m-%d")
            resultados = self.model.get_agenda(filtro_data=data_iso)
            self.popular_tabela_agenda(resultados)
        except Exception as e:
             messagebox.showerror("Erro DB", f"Não foi possível filtrar por data: {e}", parent=self)

    def abrir_dialog_projeto(self, projeto_id=None):
        dialog = ttk.Toplevel(master=self.controller.root, title="Novo Projeto na Agenda")
        dialog.transient(self.controller.root) 
        dialog.grab_set()
        dialog.resizable(False, False)

        frame = ttk.Frame(dialog, padding=20)
        frame.pack(fill=BOTH, expand=True)
        frame.columnconfigure(1, weight=1)
        
        ttk.Label(frame, text="Puxar de Orçamento:").grid(row=0, column=0, sticky=W, padx=5, pady=8)
        combo_orcamentos = ttk.Combobox(frame, state="readonly", width=40)
        combo_orcamentos.grid(row=0, column=1, sticky=EW, padx=5, pady=8)

        ttk.Separator(frame, orient=HORIZONTAL).grid(row=1, column=0, columnspan=2, sticky=EW, pady=10)

        ttk.Label(frame, text="Cliente:").grid(row=2, column=0, sticky=W, padx=5, pady=8)
        # AJUSTE 1: Removido state="readonly" para permitir digitar cliente novo
        combo_clientes = ttk.Combobox(frame, width=40)
        combo_clientes.grid(row=2, column=1, sticky=EW, padx=5, pady=8)
        
        try:
            self.lista_clientes_cache = self.model.get_all_clientes_app_para_combobox()
            combo_clientes['values'] = self.lista_clientes_cache
            
            self.lista_orcamentos_cache = self.model.get_orcamentos_antigos_para_combobox()
            orcamentos_display = ["Nenhum (Projeto Manual)"]
            for orc in self.lista_orcamentos_cache:
                orcamentos_display.append(f"{orc['id']} - {orc['cliente_nome']}")
            combo_orcamentos['values'] = orcamentos_display
            combo_orcamentos.set("Nenhum (Projeto Manual)")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível carregar listas: {e}", parent=dialog)

        ttk.Label(frame, text="Data Início:").grid(row=3, column=0, sticky=W, padx=5, pady=8)
        entry_data_inicio = DateEntry(frame, bootstyle="primary", dateformat="%d/%m/%Y", width=15)
        entry_data_inicio.grid(row=3, column=1, sticky=W, padx=5, pady=8)
        
        ttk.Label(frame, text="Data Término:").grid(row=4, column=0, sticky=W, padx=5, pady=8)
        entry_data_termino = DateEntry(frame, bootstyle="primary", dateformat="%d/%m/%Y", width=15)
        entry_data_termino.grid(row=4, column=1, sticky=W, padx=5, pady=8)
        
        ttk.Label(frame, text="Item/Ambiente:").grid(row=5, column=0, sticky=W, padx=5, pady=8)
        entry_ambientes = ttk.Entry(frame, width=42)
        entry_ambientes.grid(row=5, column=1, sticky=EW, padx=5, pady=8)
        
        ttk.Label(frame, text="Descrição:").grid(row=6, column=0, sticky=W, padx=5, pady=8)
        entry_descricao = ttk.Entry(frame, width=42)
        entry_descricao.grid(row=6, column=1, sticky=EW, padx=5, pady=8)

        def on_orcamento_select(event):
            selected_str = combo_orcamentos.get()
            
            entry_ambientes.delete(0, END)
            entry_descricao.delete(0, END)
            
            if selected_str == "Nenhum (Projeto Manual)":
                combo_clientes.set("")
                return

            try:
                orc_id = int(selected_str.split(" - ")[0])
                
                orcamento_selecionado = None
                for orc in self.lista_orcamentos_cache:
                    if orc['id'] == orc_id:
                        orcamento_selecionado = orc
                        break
                
                if not orcamento_selecionado:
                    return

                cliente_nome = orcamento_selecionado['cliente_nome']
                cliente_id_str = ""
                
                for c_str in self.lista_clientes_cache:
                    if c_str.endswith(f" - {cliente_nome}"):
                        cliente_id_str = c_str
                        break
                
                if cliente_id_str:
                    combo_clientes.set(cliente_id_str)
                else:
                    try:
                        novo_id = self.model.get_or_create_cliente_app(cliente_nome)
                        novo_str = f"{novo_id} - {cliente_nome}"
                        
                        self.lista_clientes_cache.append(novo_str)
                        combo_clientes['values'] = self.lista_clientes_cache
                        combo_clientes.set(novo_str)
                        
                        messagebox.showinfo("Novo Cliente", f"Cliente '{cliente_nome}' não estava na lista, foi cadastrado com ID {novo_id}.", parent=dialog)
                        
                    except Exception as e:
                        messagebox.showerror("Erro", f"Não foi possível criar/encontrar o cliente '{cliente_nome}': {e}", parent=dialog)
                        combo_clientes.set("")
                        return
                
                itens_json = orcamento_selecionado['itens_json']
                if itens_json:
                    itens_data = json.loads(itens_json)
                    amb_list = []
                    desc_list = []
                    
                    for item in itens_data:
                        amb = item.get('ambiente', '').strip()
                        desc = item.get('descricao', '').strip().split('\n')[0]
                        
                        if amb:
                            amb_list.append(amb)
                        if desc:
                            desc_list.append(desc)
                    
                    amb_auto = ", ".join(dict.fromkeys(amb_list))
                    desc_auto = ", ".join(dict.fromkeys(desc_list))
                    
                    if amb_auto:
                        entry_ambientes.insert(0, amb_auto)
                    else:
                        entry_ambientes.insert(0, "Projeto (sem ambientes)")
                        
                    if desc_auto:
                        entry_descricao.insert(0, desc_auto)
                    else:
                        entry_descricao.insert(0, "Projeto (sem descrição)")
                else:
                    entry_ambientes.insert(0, "Projeto (sem itens)")
                    entry_descricao.insert(0, "Projeto (sem itens)")

            except Exception as e:
                print(f"Erro ao selecionar orçamento: {e}")
                messagebox.showerror("Erro", f"Erro ao processar orçamento: {e}", parent=dialog)
        
        combo_orcamentos.bind("<<ComboboxSelected>>", on_orcamento_select)

        dados_antigos = None
        if projeto_id:
            dialog.title("Editar Projeto")
            combo_orcamentos.config(state="disabled") 
            try:
                dados_antigos = self.model.get_agenda_by_id(projeto_id)
                if dados_antigos:
                    cliente_str_antigo = f"{dados_antigos['cliente_id']} - {dados_antigos['nome']}"
                    if cliente_str_antigo in self.lista_clientes_cache:
                        combo_clientes.set(cliente_str_antigo)
                    
                    entry_data_inicio.entry.delete(0, END)
                    entry_data_inicio.entry.insert(0, datetime.strptime(dados_antigos['data_inicio'], "%Y-%m-%d").strftime("%d/%m/%Y"))
                    
                    entry_data_termino.entry.delete(0, END)
                    entry_data_termino.entry.insert(0, datetime.strptime(dados_antigos['data_previsao_termino'], "%Y-%m-%d").strftime("%d/%m/%Y"))
                    
                    entry_ambientes.insert(0, dados_antigos['descricao'])
                    
            except Exception as e:
                 messagebox.showerror("Erro", f"Não foi possível carregar dados para edição: {e}", parent=dialog)

        dialog.update_idletasks()
        try:
            root_x = self.controller.root.winfo_x()
            root_y = self.controller.root.winfo_y()
            root_width = self.controller.root.winfo_width()
            root_height = self.controller.root.winfo_height()
            
            dialog_width = dialog.winfo_width()
            dialog_height = dialog.winfo_height()
            
            center_x = root_x + (root_width // 2) - (dialog_width // 2)
            center_y = root_y + (root_height // 2) - (dialog_height // 2)
            
            dialog.geometry(f"+{center_x}+{center_y}")
        except Exception as e:
            print(f"Erro ao centralizar dialog: {e}")

        def salvar():
            cliente_selecionado = combo_clientes.get()
            data_inicio = entry_data_inicio.entry.get()
            data_termino = entry_data_termino.entry.get()
            
            ambientes = entry_ambientes.get().strip()
            descricao = entry_descricao.get().strip()
            
            descricao_final = ambientes
            if descricao:
                descricao_final = f"{ambientes} - {descricao}"

            if not cliente_selecionado or not data_inicio or not data_termino or not ambientes:
                messagebox.showwarning("Atenção", "Preencha pelo menos Cliente, Datas e Item/Ambiente.", parent=dialog)
                return

            try:
                # AJUSTE 2: Lógica para detectar se é ID existente ou Cliente Novo
                if " - " in cliente_selecionado and cliente_selecionado.split(" - ")[0].isdigit():
                     cliente_id = int(cliente_selecionado.split(" - ")[0])
                else:
                     # Cliente digitado manualmente -> Criar ou buscar pelo nome
                     cliente_id = self.model.get_or_create_cliente_app(cliente_selecionado.strip())

                data_inicio_iso = datetime.strptime(data_inicio, "%d/%m/%Y").strftime("%Y-%m-%d")
                data_termino_iso = datetime.strptime(data_termino, "%d/%m/%Y").strftime("%Y-%m-%d")

                if projeto_id:
                    self.model.update_agenda(projeto_id, cliente_id, data_inicio_iso, data_termino_iso, descricao_final)
                else:
                    self.model.add_agenda(cliente_id, data_inicio_iso, data_termino_iso, descricao_final)
                
                self.popular_tabela_agenda()
                self.controller.atualizar_aba('home')
                self.controller.atualizar_aba('recebimentos')
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Erro DB", f"Não foi possível salvar o projeto: {e}", parent=dialog)

        btn_salvar = ttk.Button(frame, text="✔️ Salvar Projeto", command=salvar, bootstyle="success")
        btn_salvar.grid(row=7, column=0, columnspan=2, pady=15, sticky=E)

    def editar_projeto_selecionado(self):
        selected = self.tree_agenda.selection()
        if not selected:
            messagebox.showwarning("Atenção", "Selecione um projeto na tabela para editar.", parent=self)
            return
        
        projeto_id = self.tree_agenda.item(selected[0], 'values')[0]
        self.abrir_dialog_projeto(projeto_id=projeto_id)

    def remover_projeto_selecionado(self):
        selected = self.tree_agenda.selection()
        if not selected:
            messagebox.showwarning("Atenção", "Selecione um projeto na tabela para remover.", parent=self)
            return
            
        projeto_id = self.tree_agenda.item(selected[0], 'values')[0]
        
        if not messagebox.askyesno("Confirmar Remoção", f"Tem certeza que deseja remover o Projeto ID {projeto_id}?\n\nEsta ação não pode ser desfeita.", parent=self):
            return
            
        try:
            self.model.delete_agenda(projeto_id)
            self.popular_tabela_agenda()
            self.controller.atualizar_aba('home')
            self.controller.atualizar_aba('recebimentos')
        except Exception as e:
            messagebox.showerror("Erro DB", f"Não foi possível remover o projeto: {e}\n\nPode estar vinculado a um recebimento.", parent=self)