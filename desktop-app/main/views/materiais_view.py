import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import Text, WORD, SOLID, messagebox, END, X, Y, VERTICAL, BOTH, NS, NSEW, EW, CENTER

class MateriaisView(ttk.Frame):
    """ Aba para Gerenciamento de Materiais (CRUD Completo). """
    def __init__(self, parent, controller):
        super().__init__(parent, padding=15)
        self.controller = controller
        self.model = controller.model
        
        self.selected_material_id = None 

        self.columnconfigure(0, weight=1, minsize=300) 
        self.columnconfigure(1, weight=2)
        self.rowconfigure(0, weight=1)
        
        form_frame = ttk.Labelframe(self, text="Formulário de Material", padding=20)
        form_frame.grid(row=0, column=0, sticky=NS, padx=(0, 10))
        form_frame.columnconfigure(0, weight=1)

        ttk.Label(form_frame, text="Nome do Material (Ex: MDF, Puxador):").pack(fill=X, pady=(0,5))
        self.entry_mat_nome = ttk.Entry(form_frame)
        self.entry_mat_nome.pack(fill=X, pady=(0,15))
        self.entry_mat_nome.focus()

        ttk.Label(form_frame, text="Descrição (Opcional):").pack(fill=X, pady=(0,5))
        self.text_mat_desc = Text(form_frame, height=5, font=("Arial", 10), wrap=WORD,
                                   relief=SOLID, borderwidth=1, highlightthickness=1)
        self.text_mat_desc.pack(fill=BOTH, expand=True, pady=(0,15))

        self.btn_salvar = ttk.Button(
            form_frame,
            text="✔️ SALVAR NOVO MATERIAL", 
            command=self.salvar_material,
            bootstyle="success"
        )
        self.btn_salvar.pack(fill=X, ipady=5, pady=(5,0))
        
        btn_limpar = ttk.Button(
            form_frame,
            text="LIMPAR FORMULÁRIO / CANCELAR EDIÇÃO",
            command=self.clear_form_materiais,
            bootstyle="secondary-outline"
        )
        btn_limpar.pack(fill=X, ipady=4, pady=(10,0))


        list_frame = ttk.Labelframe(self, text="Materiais Cadastrados (Clique para Editar)", padding=20)
        list_frame.grid(row=0, column=1, sticky=NSEW)
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        cols_mat = ("id", "nome")
        self.tree_materiais = ttk.Treeview(list_frame, columns=cols_mat, show="headings", height=15, bootstyle="primary")
        
        self.tree_materiais.heading("id", text="ID")
        self.tree_materiais.heading("nome", text="Nome")

        self.tree_materiais.column("id", width=40, anchor=CENTER)
        self.tree_materiais.column("nome", width=200)

        scrollbar_mat = ttk.Scrollbar(list_frame, orient=VERTICAL, command=self.tree_materiais.yview)
        self.tree_materiais.configure(yscrollcommand=scrollbar_mat.set)
        
        self.tree_materiais.grid(row=0, column=0, sticky=NSEW)
        scrollbar_mat.grid(row=0, column=1, sticky=NS)
        
        self.tree_materiais.bind("<<TreeviewSelect>>", self.on_material_select)

        btn_remover_mat = ttk.Button(
            list_frame,
            text="🗑️ REMOVER SELECIONADO",
            command=self.remover_material,
            bootstyle="danger-outline"
        )
        btn_remover_mat.grid(row=1, column=0, columnspan=2, sticky=EW, pady=(10,0), ipady=4)

        self.popular_materiais()

    def on_material_select(self, event):
        """ Chamada quando um item é clicado na Treeview. """
        selected_items = self.tree_materiais.selection()
        if not selected_items:
            return

        item_id_str = self.tree_materiais.item(selected_items[0], 'values')[0]
        self.selected_material_id = int(item_id_str)
        
        try:
            dados = self.model.get_material_by_id(self.selected_material_id)
            if not dados:
                messagebox.showerror("Erro", "Material não encontrado no banco de dados.", parent=self)
                return

            self.clear_form_materiais(reset_selection=False)
            
            self.entry_mat_nome.insert(0, dados[1])
            self.text_mat_desc.insert("1.0", dados[2] if dados[2] else "")
            
            self.btn_salvar.config(text="✔️ ATUALIZAR MATERIAL", bootstyle="info")
            self.selected_material_id = dados[0] 

        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível carregar material: {e}", parent=self)
            self.clear_form_materiais()


    def popular_materiais(self):
        """ Busca materiais no model e preenche a treeview. """
        for item in self.tree_materiais.get_children():
            self.tree_materiais.delete(item)
        try:
            for row in self.model.get_all_materiais():
                self.tree_materiais.insert("", END, values=row[:2]) 
        except Exception as e:
            messagebox.showerror("Erro DB", f"Não foi possível carregar os materiais: {e}")

    def salvar_material(self):
        """ 
        Salva um NOVO material ou ATUALIZA um material existente.
        """
        nome = self.entry_mat_nome.get().strip()
        desc = self.text_mat_desc.get("1.0", "end-1c").strip()

        if not nome:
            messagebox.showwarning("Atenção", "O campo 'Nome do Material' é obrigatório.", parent=self)
            self.entry_mat_nome.focus()
            return
        
        resultado = None
        
        try:
            if self.selected_material_id:
                resultado = self.model.update_material(self.selected_material_id, nome, desc)
                if resultado == True:
                    messagebox.showinfo("Sucesso", f"Material '{nome}' atualizado!", parent=self)
                
            else:
                resultado = self.model.add_material(nome, desc)
                if resultado == True:
                    messagebox.showinfo("Sucesso", f"Material '{nome}' salvo!", parent=self)
            
            if resultado == "IntegrityError":
                messagebox.showerror("Erro", f"O material '{nome}' já existe e não pode ser duplicado.", parent=self)
            elif resultado == False:
                 messagebox.showerror("Erro DB", "Não foi possível salvar o material.", parent=self)

            self.popular_materiais()
            self.clear_form_materiais()
            
        except Exception as e:
             messagebox.showerror("Erro DB", f"Erro inesperado: {e}", parent=self)

    def remover_material(self):
        """ Remove o material selecionado da treeview e do banco. """
        selected = self.tree_materiais.selection()
        if not selected:
            messagebox.showwarning("Atenção", "Selecione um material para remover.", parent=self)
            return

        if not messagebox.askyesno("Confirmar", "Tem certeza que deseja remover este material?", parent=self):
            return

        try:
            material_id = self.tree_materiais.item(selected[0], 'values')[0]
            self.model.delete_material(material_id)
            self.popular_materiais()
            
            self.clear_form_materiais()
            
            messagebox.showinfo("Sucesso", "Material removido.", parent=self)
        except Exception as e:
            messagebox.showerror("Erro DB", f"Não foi possível remover o material: {e}", parent=self)

    def clear_form_materiais(self, reset_selection=True):
        """ 
        Limpa o formulário de cadastro de materiais e 
        reseta o estado para "SALVAR NOVO".
        """
        self.entry_mat_nome.delete(0, END)
        self.text_mat_desc.delete("1.0", END)
        self.entry_mat_nome.focus()
        
        self.selected_material_id = None
        self.btn_salvar.config(text="✔️ SALVAR NOVO MATERIAL", bootstyle="success")
        
        if reset_selection:
            selecao_atual = self.tree_materiais.selection()
            if selecao_atual:
                self.tree_materiais.selection_remove(selecao_atual)