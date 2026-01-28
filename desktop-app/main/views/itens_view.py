import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox, Text, END, WORD, SOLID, TOP, BOTTOM, BOTH, X, Y, CENTER, VERTICAL, NS, W, EW, NW, NSEW, LEFT, RIGHT, E
from .. import utils 
from ..utils import CurrencyEntry, formatar_moeda, string_para_float, string_para_int

class ItensView(ttk.Frame):
    
    def __init__(self, parent, controller):
        super().__init__(parent, padding=15)
        self.controller = controller 
        self.total_geral_float = 0.0

        btn_frame = ttk.Frame(self)
        btn_frame.pack(side=TOP, fill=X, pady=(0, 10))
        
        btn_add = ttk.Button(btn_frame, text="✔️ ADICIONAR ITEM", 
                             command=self.adicionar_item_dialog, bootstyle="success")
        btn_add.pack(side=LEFT, padx=(0, 10), ipady=5)
        
        btn_edit = ttk.Button(btn_frame, text="✏️ EDITAR ITEM", 
                              command=self.editar_item_dialog, bootstyle="warning")
        btn_edit.pack(side=LEFT, padx=(0, 10), ipady=5)
        
        btn_rem = ttk.Button(btn_frame, text="✖️ REMOVER ITEM", 
                             command=self.remover_item, bootstyle="danger-outline")
        btn_rem.pack(side=LEFT, ipady=5)

        tree_frame = ttk.Frame(self)
        tree_frame.pack(side=TOP, fill=BOTH, expand=True, pady=10)
        
        cols = ("qtd", "ambiente", "descricao", "valor_unit", "valor_total", "desc_real")
        
        self.tree_itens = ttk.Treeview(
            tree_frame, 
            columns=cols, 
            show="headings", 
            bootstyle="primary",
            displaycolumns=("qtd", "ambiente", "descricao", "valor_unit", "valor_total")
        )
        
        self.tree_itens.heading("qtd", text="Qtd", anchor=CENTER)
        self.tree_itens.heading("ambiente", text="Ambiente", anchor=W)
        self.tree_itens.heading("descricao", text="Descrição", anchor=W)
        self.tree_itens.heading("valor_unit", text="Vl. Unitário", anchor=E)
        self.tree_itens.heading("valor_total", text="Vl. Total", anchor=E)

        self.tree_itens.column("qtd", width=50, minwidth=40, stretch=False, anchor=CENTER)
        self.tree_itens.column("ambiente", width=150, minwidth=100)
        self.tree_itens.column("descricao", width=350, minwidth=200)
        self.tree_itens.column("valor_unit", width=120, minwidth=100, anchor=E)
        self.tree_itens.column("valor_total", width=120, minwidth=100, anchor=E)

        scrollbar_y = ttk.Scrollbar(tree_frame, orient=VERTICAL, command=self.tree_itens.yview)
        self.tree_itens.configure(yscrollcommand=scrollbar_y.set)
        scrollbar_y.pack(side=RIGHT, fill=Y)
        self.tree_itens.pack(side=LEFT, fill=BOTH, expand=True)

        total_frame = ttk.Frame(self)
        total_frame.pack(side=TOP, fill=X, pady=(10, 0))
        
        self.lbl_total = ttk.Label(total_frame, text="TOTAL ORÇAMENTO: R$ 0,00", 
                                   font=("Arial", 14, "bold"), bootstyle="success")
        self.lbl_total.pack(side=RIGHT)

    def _center_popup(self, dialog, width, height):
        try:
            root_x = self.controller.root.winfo_x()
            root_y = self.controller.root.winfo_y()
            root_width = self.controller.root.winfo_width()
            root_height = self.controller.root.winfo_height()
            
            center_x = root_x + (root_width // 2)
            center_y = root_y + (root_height // 2)
            
            popup_x = center_x - (width // 2)
            popup_y = center_y - (height // 2)
            
            dialog.geometry(f'{width}x{height}+{popup_x}+{popup_y}')
        except Exception:
            dialog.geometry(f'{width}x{height}')

    def atualizar_total(self):
        self.total_geral_float = 0.0
        try:
            for item_id in self.tree_itens.get_children():
                item_values = self.tree_itens.item(item_id, "values")
                valor_total_item = item_values[4] 
                self.total_geral_float += string_para_float(valor_total_item)
                
            self.lbl_total.config(text=f"TOTAL ORÇAMENTO: {formatar_moeda(str(self.total_geral_float))}")
            if hasattr(self.controller, 'atualizar_total_orcamento'):
                self.controller.atualizar_total_orcamento(self.total_geral_float)
        except Exception:
            self.lbl_total.config(text="Erro ao calcular total")
            
    def get_total(self):
        return self.total_geral_float

    def adicionar_item_dialog(self):
        dialog = ttk.Toplevel(self.winfo_toplevel())
        dialog.title("Adicionar Novo Item")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        
        self._center_popup(dialog, 600, 450)
        
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=BOTH, expand=True)
        
        field_frame = ttk.Frame(main_frame)
        field_frame.pack(fill=X, expand=True)
        field_frame.columnconfigure(1, weight=1)
        field_frame.columnconfigure(3, weight=1)
        
        ttk.Label(field_frame, text="Quantidade:").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        entry_qtd = ttk.Entry(field_frame, bootstyle="primary", width=10)
        entry_qtd.grid(row=0, column=1, padx=5, pady=5, sticky=EW)
        entry_qtd.insert(0, "1")
        
        ttk.Label(field_frame, text="Ambiente:").grid(row=0, column=2, padx=5, pady=5, sticky=W)
        entry_ambiente = ttk.Entry(field_frame, bootstyle="primary", width=30)
        entry_ambiente.grid(row=0, column=3, padx=5, pady=5, sticky=EW)
        
        ttk.Label(field_frame, text="Valor Unitário:").grid(row=1, column=0, padx=5, pady=5, sticky=W)
        entry_valor = CurrencyEntry(field_frame, bootstyle="primary", width=15)
        entry_valor.grid(row=1, column=1, padx=5, pady=5, sticky=W)
        entry_valor.insert(0, "R$ 0,00")
        
        ttk.Label(main_frame, text="Descrição Detalhada do Item:").pack(fill=X, padx=5, pady=(10, 5))
        
        desc_frame = ttk.Frame(main_frame)
        desc_frame.pack(fill=BOTH, expand=True)
        
        text_desc = Text(desc_frame, height=10, width=60, wrap=WORD, relief=SOLID, borderwidth=1, font=("Arial", 10))
        text_desc.pack(fill=BOTH, expand=True, side=LEFT)
        
        scrollbar_desc = ttk.Scrollbar(desc_frame, orient=VERTICAL, command=text_desc.yview)
        text_desc.config(yscrollcommand=scrollbar_desc.set)
        scrollbar_desc.pack(side=RIGHT, fill=Y)

        def on_save_item():
            try:
                qtd_str = entry_qtd.get() or "1"
                qtd = string_para_float(qtd_str)
                
                ambiente = entry_ambiente.get() or "N/D"
                valor_unit_str = entry_valor.get()
                valor_unit = string_para_float(valor_unit_str)
                
                descricao = text_desc.get("1.0", END).strip()
                if not descricao:
                    messagebox.showwarning("Atenção", "A descrição é obrigatória.", parent=dialog)
                    return
                
                valor_total = qtd * valor_unit
                desc_curta = descricao[:50] + "..." if len(descricao) > 50 else descricao
                
                valores_tabela = (
                    f"{qtd:g}", ambiente, desc_curta,
                    formatar_moeda(str(valor_unit)), 
                    formatar_moeda(str(valor_total)),
                    descricao 
                )
                
                self.tree_itens.insert(parent="", index=END, values=valores_tabela)
                self.atualizar_total()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro: {e}", parent=dialog)

        btn_bar = ttk.Frame(main_frame)
        btn_bar.pack(fill=X, pady=(15, 0))
        
        btn_salvar = ttk.Button(btn_bar, text="✔️ SALVAR ITEM", command=on_save_item, bootstyle="success")
        btn_salvar.pack(side=RIGHT)
        btn_cancel = ttk.Button(btn_bar, text="Cancelar", command=dialog.destroy, bootstyle="secondary")
        btn_cancel.pack(side=RIGHT, padx=10)
        entry_qtd.focus()

    def editar_item_dialog(self):
        selected = self.tree_itens.selection()
        if not selected:
            messagebox.showwarning("Atenção", "Selecione um item para editar.")
            return
        
        item_id = selected[0]
        try:
            item_data = self.tree_itens.item(item_id)
            valores_antigos = item_data['values']
            descricao_completa_antiga = valores_antigos[5] if len(valores_antigos) > 5 else valores_antigos[2]
            
            qtd_antiga = valores_antigos[0]
            ambiente_antigo = valores_antigos[1]
            valor_unit_antigo = valores_antigos[3]
        except Exception:
            return

        dialog = ttk.Toplevel(self.winfo_toplevel())
        dialog.title("Editar Item")
        dialog.transient(self.winfo_toplevel())
        dialog.grab_set()
        self._center_popup(dialog, 600, 450)
        
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill=BOTH, expand=True)
        
        field_frame = ttk.Frame(main_frame)
        field_frame.pack(fill=X, expand=True)
        field_frame.columnconfigure(1, weight=1)
        field_frame.columnconfigure(3, weight=1)
        
        ttk.Label(field_frame, text="Quantidade:").grid(row=0, column=0, padx=5, pady=5, sticky=W)
        entry_qtd = ttk.Entry(field_frame, bootstyle="primary", width=10)
        entry_qtd.grid(row=0, column=1, padx=5, pady=5, sticky=EW)
        
        ttk.Label(field_frame, text="Ambiente:").grid(row=0, column=2, padx=5, pady=5, sticky=W)
        entry_ambiente = ttk.Entry(field_frame, bootstyle="primary", width=30)
        entry_ambiente.grid(row=0, column=3, padx=5, pady=5, sticky=EW)
        
        ttk.Label(field_frame, text="Valor Unitário:").grid(row=1, column=0, padx=5, pady=5, sticky=W)
        entry_valor = CurrencyEntry(field_frame, bootstyle="primary", width=15)
        entry_valor.grid(row=1, column=1, padx=5, pady=5, sticky=W)
        
        ttk.Label(main_frame, text="Descrição Detalhada do Item:").pack(fill=X, padx=5, pady=(10, 5))
        
        desc_frame = ttk.Frame(main_frame)
        desc_frame.pack(fill=BOTH, expand=True)
        text_desc = Text(desc_frame, height=10, width=60, wrap=WORD, relief=SOLID, borderwidth=1, font=("Arial", 10))
        text_desc.pack(fill=BOTH, expand=True, side=LEFT)
        scrollbar_desc = ttk.Scrollbar(desc_frame, orient=VERTICAL, command=text_desc.yview)
        text_desc.config(yscrollcommand=scrollbar_desc.set)
        scrollbar_desc.pack(side=RIGHT, fill=Y)

        entry_qtd.insert(0, qtd_antiga)
        entry_ambiente.insert(0, ambiente_antigo)
        entry_valor.insert(0, valor_unit_antigo)
        text_desc.insert("1.0", descricao_completa_antiga)

        def on_update_item():
            try:
                qtd_str = entry_qtd.get() or "1"
                qtd = string_para_float(qtd_str)
                
                ambiente = entry_ambiente.get() or "N/D"
                valor_unit_str = entry_valor.get()
                valor_unit = string_para_float(valor_unit_str)
                
                descricao = text_desc.get("1.0", END).strip()
                if not descricao:
                    messagebox.showwarning("Atenção", "A descrição é obrigatória.", parent=dialog)
                    return
                
                valor_total = qtd * valor_unit
                desc_curta = descricao[:50] + "..." if len(descricao) > 50 else descricao
                
                valores_tabela = (
                    f"{qtd:g}", ambiente, desc_curta,
                    formatar_moeda(str(valor_unit)),
                    formatar_moeda(str(valor_total)),
                    descricao
                )
                
                self.tree_itens.item(item_id, values=valores_tabela)
                self.atualizar_total()
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro: {e}", parent=dialog)

        btn_bar = ttk.Frame(main_frame)
        btn_bar.pack(fill=X, pady=(15, 0))
        btn_atualizar = ttk.Button(btn_bar, text="✔️ ATUALIZAR ITEM", command=on_update_item, bootstyle="success")
        btn_atualizar.pack(side=RIGHT)
        btn_cancel = ttk.Button(btn_bar, text="Cancelar", command=dialog.destroy, bootstyle="secondary")
        btn_cancel.pack(side=RIGHT, padx=10)
        entry_qtd.focus()

    def remover_item(self):
        selected = self.tree_itens.selection()
        if not selected:
            messagebox.showwarning("Atenção", "Selecione um item.")
            return
        if messagebox.askyesno("Confirmar", "Remover item selecionado?"):
            for item_id in selected:
                self.tree_itens.delete(item_id)
            self.atualizar_total()

    def get_itens_data(self):
        itens_tabela = []
        for item_id in self.tree_itens.get_children():
            valores = self.tree_itens.item(item_id)['values']
            descricao_real = valores[5] if len(valores) > 5 else valores[2]
            itens_tabela.append({
                "qtd": valores[0],
                "ambiente": valores[1],
                "descricao": descricao_real,
                "valor_unit": valores[3],
                "valor_total": valores[4]
            })
        return itens_tabela
    
    def set_data(self, itens_carregados):
        self.tree_itens.delete(*self.tree_itens.get_children())
        if not itens_carregados:
            self.atualizar_total()
            return

        for item in itens_carregados:
            try:
                qtd_float = string_para_float(str(item.get('qtd', '1')))
                valor = string_para_float(str(item.get('valor_unit', '0')))
                total = qtd_float * valor
                descricao = item.get('descricao', '')
                desc_display = descricao[:50] + "..." if len(descricao) > 50 else descricao

                self.tree_itens.insert("", END, values=(
                    f"{qtd_float:g}", item.get('ambiente', ''), desc_display, 
                    formatar_moeda(str(valor)), formatar_moeda(str(total)),
                    descricao
                )) 
            except Exception:
                pass
        self.atualizar_total()