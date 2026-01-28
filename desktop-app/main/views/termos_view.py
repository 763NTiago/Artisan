import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import (Text, WORD, SOLID, W, NSEW, END, 
                     Toplevel, MULTIPLE, VERTICAL, 
                     LEFT, RIGHT, Y, BOTH, INSERT, NE, NW, X, CENTER, NS, EW, TOP, BOTTOM)
from tkinter import messagebox
import re

class TermosView(ttk.Frame):
    
    def __init__(self, parent, controller):
        super().__init__(parent, padding=15)
        self.controller = controller

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1) 

        paned_window = ttk.Panedwindow(self, orient=VERTICAL) 
        paned_window.grid(row=0, column=0, sticky=NSEW)

        frame_obs_container = ttk.Frame(paned_window, padding=0) 
        frame_obs = ttk.Labelframe(frame_obs_container, text="Observações e Materiais", padding=15)
        frame_obs.pack(fill=BOTH, expand=True)
        
        frame_obs.columnconfigure(0, weight=1)
        frame_obs.rowconfigure(1, weight=1) 

        btn_add_mat = ttk.Button(
            frame_obs,
            text="Editar Materiais Inclusos 🛠️",
            command=self.abrir_dialog_construtor_materiais,
            bootstyle="primary-outline"
        )
        btn_add_mat.grid(row=0, column=0, sticky=NE, pady=(0, 10))

        self.text_obs = Text(frame_obs, font=("Arial", 10), wrap=WORD,
                             relief=SOLID, borderwidth=1, highlightthickness=1)
        self.text_obs.grid(row=1, column=0, sticky=NSEW)
        self.text_obs.insert("1.0", "Ex: Todos os puxadores conforme projeto, corrediças invisíveis, dobradiças em inox com amortecimento.")

        paned_window.add(frame_obs_container, weight=1) 

        frame_pag_container = ttk.Frame(paned_window, padding=0) 
        frame_pag = ttk.Labelframe(frame_pag_container, text="Condições, Prazos e Validade", padding=15)
        frame_pag.pack(fill=BOTH, expand=True)
        
        frame_pag.columnconfigure(0, weight=1)
        frame_pag.rowconfigure(0, weight=1)

        self.text_pagamento = Text(frame_pag, font=("Arial", 10), wrap=WORD,
                                   relief=SOLID, borderwidth=1, highlightthickness=1)
        self.text_pagamento.grid(row=0, column=0, sticky=NSEW)
        
        texto_padrao_pagamento = (
            "Orçamento válido por: 20 dias.\n"
            "Prazo de entrega: 60 dias úteis.\n\n"
            "--- CONDIÇÕES DE PAGAMENTO ---\n"
            "À VISTA: 50% entrada, 50% na entrega.\n"
            "A PRAZO: 40% entrada, restante em 6x no cheque."
        )
        self.text_pagamento.insert("1.0", texto_padrao_pagamento)

        paned_window.add(frame_pag_container, weight=1)

    def abrir_dialog_construtor_materiais(self):
        try:
            materiais_db = self.controller.model.get_all_materiais()
        except Exception as e:
            messagebox.showerror("Erro DB", f"Não foi possível buscar os materiais: {e}")
            return

        if not materiais_db:
            messagebox.showinfo("Materiais", "Nenhum material cadastrado na aba 'Materiais'.", parent=self)
            return
        
        materiais_map = {mat[1]: mat[2] for mat in materiais_db} 
        nomes_materiais = [mat[1] for mat in materiais_db]

        itens_atuais = []
        texto_obs_completo = self.text_obs.get("1.0", "end-1c")
        
        match = re.search(
            r"--- MATERIAIS INCLUSOS ---\n(.*?)\n--- FIM MATERIAIS ---", 
            texto_obs_completo, 
            re.DOTALL | re.IGNORECASE
        )
        
        if match:
            linhas_materiais_brutas = match.group(1).strip()
            linhas_separadas = linhas_materiais_brutas.split('\n')
            for linha in linhas_separadas:
                if not linha.strip(): continue
                if "Nenhum material" in linha: continue 
                
                partes = linha.split('\t\t', 1)
                mat = partes[0].strip()
                desc = partes[1].strip() if len(partes) > 1 else ""
                if mat:
                    itens_atuais.append((mat, desc))

        dialog = Toplevel(self)
        dialog.title("Editor de Materiais Inclusos")
        dialog.minsize(600, 450)
        dialog.transient(self)
        dialog.grab_set()

        dialog.update_idletasks()
        root_window = self.winfo_toplevel()
        root_x = root_window.winfo_x()
        root_y = root_window.winfo_y()
        root_width = root_window.winfo_width()
        root_height = root_window.winfo_height()
        dialog_width = dialog.winfo_width()
        dialog_height = dialog.winfo_height()
        center_x = root_x + (root_width // 2) - (dialog_width // 2)
        center_y = root_y + (root_height // 2) - (dialog_height // 2)
        dialog.geometry(f"+{center_x}+{center_y}")
        
        form_frame = ttk.Frame(dialog, padding=15)
        form_frame.pack(fill=X, side=TOP)
        form_frame.columnconfigure(1, weight=1)

        ttk.Label(form_frame, text="Material:").grid(row=0, column=0, sticky=W, padx=(0, 10))
        combo_materiais = ttk.Combobox(form_frame, values=nomes_materiais, state="readonly")
        combo_materiais.grid(row=0, column=1, columnspan=2, sticky=EW, pady=5)

        ttk.Label(form_frame, text="Descrição:").grid(row=1, column=0, sticky=W, padx=(0, 10))
        entry_desc = ttk.Entry(form_frame)
        entry_desc.grid(row=1, column=1, columnspan=2, sticky=EW, pady=5)

        btn_adicionar_item = ttk.Button(form_frame, text="Adicionar à Lista ⬇️", bootstyle="info")
        btn_adicionar_item.grid(row=2, column=1, columnspan=2, sticky=EW, pady=10)

        botoes_dialog_frame = ttk.Frame(dialog, padding=15)
        botoes_dialog_frame.pack(fill=X, side=BOTTOM)
        botoes_dialog_frame.columnconfigure(0, weight=1)
        botoes_dialog_frame.columnconfigure(1, weight=1)

        btn_remover_item = ttk.Button(botoes_dialog_frame, text="Remover Item Selecionado 🗑️", bootstyle="danger-outline")
        btn_remover_item.grid(row=0, column=0, sticky=EW, padx=(0, 5), ipady=5)

        btn_confirmar = ttk.Button(
            botoes_dialog_frame,
            text="✔️ Confirmar e Atualizar Lista",
            bootstyle="success"
        )
        btn_confirmar.grid(row=0, column=1, sticky=EW, padx=(5, 0), ipady=5)
        
        tree_frame = ttk.Labelframe(dialog, text="Itens para Inserir", padding=10)
        tree_frame.pack(fill=BOTH, expand=True, padx=15, pady=5, side=TOP)
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        
        cols = ("material", "descricao")
        tree_itens_inserir = ttk.Treeview(tree_frame, columns=cols, show="headings", height=8)
        
        tree_itens_inserir.heading("material", text="Material")
        tree_itens_inserir.heading("descricao", text="Descrição")
        tree_itens_inserir.column("material", width=150)
        tree_itens_inserir.column("descricao", width=350)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient=VERTICAL, command=tree_itens_inserir.yview)
        tree_itens_inserir.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.grid(row=0, column=1, sticky=NS)
        tree_itens_inserir.grid(row=0, column=0, sticky=NSEW)

        for item in itens_atuais:
            tree_itens_inserir.insert("", END, values=item)
        
        def on_material_select(event):
            nome_selecionado = combo_materiais.get()
            descricao_db = materiais_map.get(nome_selecionado, "")
            entry_desc.delete(0, END)
            entry_desc.insert(0, descricao_db)
            entry_desc.focus() 

        def adicionar_item_tree():
            material = combo_materiais.get()
            desc = entry_desc.get().strip()

            if not material:
                messagebox.showwarning("Atenção", "Selecione um material.", parent=dialog)
                return
            
            tree_itens_inserir.insert("", END, values=(material, desc))
            entry_desc.delete(0, END)
            combo_materiais.focus()
            if combo_materiais.get():
                on_material_select(None)

        def remover_item_tree():
            selected_items = tree_itens_inserir.selection()
            if not selected_items:
                messagebox.showwarning("Atenção", "Selecione um item da lista para remover.", parent=dialog)
                return
            for item in selected_items:
                tree_itens_inserir.delete(item)
        
        def confirmar_e_inserir_texto():
            itens = tree_itens_inserir.get_children()
            texto_para_inserir = "\n\n--- MATERIAIS INCLUSOS ---\n"
            
            if not itens:
                texto_para_inserir += "Nenhum material específico incluso.\n"
            else:
                for item_id in itens:
                    valores = tree_itens_inserir.item(item_id, 'values')
                    if isinstance(valores, (list, tuple)) and len(valores) >= 2:
                        mat, desc = valores[0], valores[1]
                        linha = f"{mat}\t\t{desc}\n"
                        texto_para_inserir += linha

            texto_para_inserir += "--- FIM MATERIAIS ---\n\n"

            texto_obs_completo = self.text_obs.get("1.0", "end-1c")
            match = re.search(
                r"--- MATERIAIS INCLUSOS ---.*--- FIM MATERIAIS ---", 
                texto_obs_completo, 
                re.DOTALL | re.IGNORECASE
            )
            
            if match:
                bloco_antigo = match.group(0)
                start_index = self.text_obs.search(bloco_antigo, "1.0", END, nocase=True)
                if start_index:
                    end_index = f"{start_index} + {len(bloco_antigo)} chars"
                    self.text_obs.delete(start_index, end_index)
                    self.text_obs.insert(start_index, texto_para_inserir.strip())
                else:
                    self.text_obs.insert(INSERT, texto_para_inserir)
            else:
                self.text_obs.insert(INSERT, texto_para_inserir)

            dialog.destroy()

        btn_adicionar_item.config(command=adicionar_item_tree)
        btn_remover_item.config(command=remover_item_tree)
        btn_confirmar.config(command=confirmar_e_inserir_texto)
        
        combo_materiais.bind("<<ComboboxSelected>>", on_material_select)

        if nomes_materiais:
            combo_materiais.current(0)
            on_material_select(None) 
        
    def get_data(self):
        obs_brutas = self.text_obs.get("1.0", "end-1c").strip()
        pag_brutas = self.text_pagamento.get("1.0", "end-1c").strip()
        
        match = re.search(
            r"--- MATERIAIS INCLUSOS ---\n(.*?)\n--- FIM MATERIAIS ---", 
            obs_brutas, 
            re.DOTALL | re.IGNORECASE
        )
        
        obs_html = "" 

        if match:
            bloco_materiais_bruto_completo = match.group(0)
            linhas_materiais_brutas = match.group(1).strip()
            
            tabela_html = '<p class="descricao-tabela" style="margin-top: 15px;">Abaixo estão os materiais considerados para este orçamento:</p>'
            tabela_html += '<table class="tabela-materiais">'
            tabela_html += '<thead><tr><th style="width: 30%;">Material</th><th style="width: 70%;">Descrição</th></tr></thead>'
            tabela_html += '<tbody>'
            
            linhas_separadas = linhas_materiais_brutas.split('\n')
            
            if not linhas_materiais_brutas.strip() or "Nenhum material" in linhas_materiais_brutas:
                tabela_html += '<tr><td colspan="2">Nenhum material específico incluso.</td></tr>'
            else:
                for linha in linhas_separadas:
                    if not linha.strip(): continue 
                    partes = linha.split('\t\t', 1) 
                    mat = partes[0].strip()
                    desc = partes[1].strip() if len(partes) > 1 else ""
                    if mat: 
                        tabela_html += f'<tr><td>{mat}</td><td>{desc}</td></tr>'
            
            tabela_html += '</tbody></table>'
            
            obs_com_tabela = obs_brutas.replace(bloco_materiais_bruto_completo, tabela_html)
            obs_html = obs_com_tabela.replace("\n", "<br>")
            obs_html = re.sub(r'(<br\s*/?>\s*)+<p class="descricao-tabela">', r'<p class="descricao-tabela">', obs_html)
            obs_html = re.sub(r'</table>(<br\s*/?>\s*)+', r'</table>', obs_html)

        else:
            obs_html = obs_brutas.replace("\n", "<br>")
       
        return {
            "observacoes_brutas": obs_brutas,
            "pagamento_brutas": pag_brutas,
            "observacoes_html": obs_html, 
            "pagamento_html": pag_brutas.replace("\n", "<br>")
        }
        
    def set_data(self, data):
        self.clear_data()
        self.text_obs.insert("1.0", data.get("observacoes", "Ex: Todos os puxadores conforme projeto, corrediças invisíveis, dobradiças em inox com amortecimento."))
        
        texto_padrao_pagamento = (
            "Orçamento válido por: 20 dias.\n"
            "Prazo de entrega: 60 dias úteis.\n\n"
            "--- CONDIÇÕES DE PAGAMENTO ---\n"
            "À VISTA: 50% entrada, 50% na entrega.\n"
            "A PRAZO: 40% entrada, restante em 6x no cheque."
        )
        self.text_pagamento.insert("1.0", data.get("condicoes_pagamento", texto_padrao_pagamento))

    def clear_data(self):
        self.text_obs.delete("1.0", END)
        self.text_pagamento.delete("1.0", END)