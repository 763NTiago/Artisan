import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, END, X, Y, VERTICAL, BOTH, CENTER, E, RIGHT, LEFT

class HistoricoView(ttk.Frame):
    
    def __init__(self, parent, controller):
        super().__init__(parent, padding=15)
        self.controller = controller
        self.model = controller.model 
        
        frame_botoes_hist = ttk.Frame(self)
        frame_botoes_hist.pack(fill=X, pady=(0, 10))

        btn_load = ttk.Button(
            frame_botoes_hist,
            text="📂 CARREGAR SELECIONADO",
            command=self.controller.carregar_do_historico, 
            bootstyle="info"
        )
        btn_load.pack(side=LEFT, padx=5, ipady=4)

        btn_edit = ttk.Button(
            frame_botoes_hist,
            text="📝 EDITAR SELECIONADO",
            command=self.controller.iniciar_edicao_historico, 
            bootstyle="warning" 
        )
        btn_edit.pack(side=LEFT, padx=5, ipady=4)
        btn_delete = ttk.Button(
            frame_botoes_hist,
            text="🗑️ REMOVER SELECIONADO",
            command=self.controller.remover_do_historico, 
            bootstyle="danger-outline"
        )
        btn_delete.pack(side=LEFT, padx=5, ipady=4)

        btn_refresh = ttk.Button(
            frame_botoes_hist,
            text="🔄 ATUALIZAR LISTA",
            command=self.popular_historico, 
            bootstyle="secondary-outline"
        )
        btn_refresh.pack(side=RIGHT, padx=5, ipady=4)

        frame_tree = ttk.Frame(self)
        frame_tree.pack(fill=BOTH, expand=True, pady=(10, 0))

        colunas = ("id", "data", "cliente", "valor")
        self.tree_historico = ttk.Treeview(
            frame_tree, 
            columns=colunas, 
            show="headings", 
            bootstyle="primary"
        )
        
        self.tree_historico.heading("id", text="ID", anchor=W)
        self.tree_historico.heading("data", text="Data", anchor=W)
        self.tree_historico.heading("cliente", text="Cliente", anchor=W)
        self.tree_historico.heading("valor", text="Valor Total", anchor=E)

        self.tree_historico.column("id", width=60, minwidth=40, stretch=False)
        self.tree_historico.column("data", width=120, minwidth=100, stretch=False)
        self.tree_historico.column("cliente", width=400, minwidth=200)
        self.tree_historico.column("valor", width=150, minwidth=120, stretch=False)

        scrollbar_y = ttk.Scrollbar(frame_tree, orient=VERTICAL, command=self.tree_historico.yview)
        self.tree_historico.configure(yscrollcommand=scrollbar_y.set)
        scrollbar_y.pack(side=RIGHT, fill=Y)
        self.tree_historico.pack(side=LEFT, fill=BOTH, expand=True)

    def popular_historico(self):
        for item in self.tree_historico.get_children():
            self.tree_historico.delete(item)
        
        try:
            lista_de_orcamentos = self.model.get_all_orcamentos()
            
            for row in lista_de_orcamentos:
                
                id_orcamento = row['id']
                data_orcamento = row['data_criacao']
                cliente_nome = row['cliente_nome']
                valor_total = row['valor_total_final']

                valores_para_tabela = (id_orcamento, data_orcamento, cliente_nome, valor_total)
                
                self.tree_historico.insert(parent="", index=END, iid=id_orcamento, values=valores_para_tabela)
                    
        except Exception as e:
            messagebox.showerror("Erro DB", f"Não foi possível carregar o histórico: {e}")

    def get_selected_id(self):
        selected = self.tree_historico.selection()
        if not selected:
            messagebox.showwarning("Atenção", "Selecione um orçamento do histórico.")
            return None
        
        try:
            item_id = selected[0]
            return int(item_id)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível ler o ID selecionado: {e}")
            return None