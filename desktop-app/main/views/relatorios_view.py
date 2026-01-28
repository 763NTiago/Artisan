import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import DateEntry
from tkinter import messagebox, filedialog
import csv
from datetime import datetime
from ..utils import formatar_moeda

class RelatoriosView(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, padding=15)
        self.controller = controller
        self.dados_atuais = []
        
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=X, pady=(0, 15))
        
        lbl_titulo = ttk.Label(header_frame, text="📊 Relatórios Financeiros", 
                               font=("Arial", 18, "bold"), bootstyle="primary")
        lbl_titulo.pack(side=LEFT)

        filter_frame = ttk.Labelframe(self, text="🔍 Filtros de Pesquisa", 
                                      padding=15, bootstyle="info")
        filter_frame.pack(fill=X, pady=5)
        
        row1 = ttk.Frame(filter_frame)
        row1.pack(fill=X, pady=5)
        
        col1 = ttk.Frame(row1)
        col1.pack(side=LEFT, padx=5, fill=X, expand=True)
        ttk.Label(col1, text="Cliente:", font=("Arial", 9, "bold")).pack(anchor=W)
        self.combo_cliente = ttk.Combobox(col1, width=25, bootstyle="primary", postcommand=self.carregar_opcoes_combobox)
        self.combo_cliente.pack(fill=X, pady=2)

        col2 = ttk.Frame(row1)
        col2.pack(side=LEFT, padx=5, fill=X, expand=True)
        ttk.Label(col2, text="Projeto:", font=("Arial", 9, "bold")).pack(anchor=W)
        self.combo_projeto = ttk.Combobox(col2, width=25, bootstyle="primary", postcommand=self.carregar_opcoes_combobox)
        self.combo_projeto.pack(fill=X, pady=2)

        col3 = ttk.Frame(row1)
        col3.pack(side=LEFT, padx=5, fill=X, expand=True)
        ttk.Label(col3, text="Arquiteto:", font=("Arial", 9, "bold")).pack(anchor=W)
        self.combo_arquiteto = ttk.Combobox(col3, width=25, bootstyle="primary", postcommand=self.carregar_opcoes_combobox)
        self.combo_arquiteto.pack(fill=X, pady=2)

        row2 = ttk.Frame(filter_frame)
        row2.pack(fill=X, pady=10)
        
        date_container = ttk.Frame(row2)
        date_container.pack(side=LEFT)
        
        date_frame1 = ttk.Frame(date_container)
        date_frame1.pack(side=LEFT, padx=5)
        ttk.Label(date_frame1, text="📅 De:", font=("Arial", 9, "bold")).pack(side=LEFT)
        self.date_inicio = DateEntry(date_frame1, width=12, bootstyle='primary', 
                                     startdate=datetime.now(), dateformat='%d/%m/%Y')
        self.date_inicio.pack(side=LEFT, padx=5)
        
        date_frame2 = ttk.Frame(date_container)
        date_frame2.pack(side=LEFT, padx=5)
        ttk.Label(date_frame2, text="📅 Até:", font=("Arial", 9, "bold")).pack(side=LEFT)
        self.date_fim = DateEntry(date_frame2, width=12, bootstyle='primary', 
                                  startdate=datetime.now(), dateformat='%d/%m/%Y')
        self.date_fim.pack(side=LEFT, padx=5)
        
        self.usar_filtro_data = ttk.BooleanVar(value=False)
        chk_data = ttk.Checkbutton(date_container, text="Usar filtro de data", 
                                   variable=self.usar_filtro_data,
                                   bootstyle="primary-round-toggle")
        chk_data.pack(side=LEFT, padx=10)
        
        btn_container = ttk.Frame(row2)
        btn_container.pack(side=RIGHT)
        
        btn_filtrar = ttk.Button(btn_container, text="🔍 PESQUISAR", 
                                 command=self.aplicar_filtros, 
                                 bootstyle="success", width=15)
        btn_filtrar.pack(side=LEFT, padx=5)

        btn_limpar = ttk.Button(btn_container, text="🗑️ Limpar Filtros", 
                               command=self.limpar_filtros, 
                               bootstyle="secondary-outline", width=15)
        btn_limpar.pack(side=LEFT, padx=5)

        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=BOTH, expand=True, pady=10)
        
        tree_border = ttk.Frame(tree_frame, bootstyle="secondary")
        tree_border.pack(fill=BOTH, expand=True)
        
        cols = ("inicio", "termino", "cliente", "projeto", "tipo", "parc", "total_proj", 
                "comissao", "pago", "a_receber", "lucro")
        self.tree = ttk.Treeview(tree_border, columns=cols, show="headings", 
                                 bootstyle="info", selectmode="browse", height=15)
        
        self.tree.heading("inicio", text="📅 Início")
        self.tree.heading("termino", text="📅 Término")
        self.tree.heading("cliente", text="👤 Cliente")
        self.tree.heading("projeto", text="📁 Projeto")
        self.tree.heading("tipo", text="💳 Pagamento")
        self.tree.heading("parc", text="#")
        self.tree.heading("total_proj", text="💰 Total")
        self.tree.heading("comissao", text="● Comissão")
        self.tree.heading("pago", text="● Recebido")
        self.tree.heading("a_receber", text="● A Receber")
        self.tree.heading("lucro", text="● Lucro")
        
        self.tree.column("inicio", width=90, anchor=CENTER)
        self.tree.column("termino", width=90, anchor=CENTER)
        self.tree.column("cliente", width=140)
        self.tree.column("projeto", width=140)
        self.tree.column("tipo", width=110, anchor=CENTER)
        self.tree.column("parc", width=40, anchor=CENTER)
        self.tree.column("total_proj", width=100, anchor=E)
        self.tree.column("comissao", width=110, anchor=E)
        self.tree.column("pago", width=110, anchor=E)
        self.tree.column("a_receber", width=110, anchor=E)
        self.tree.column("lucro", width=110, anchor=E)
        
        self.tree.tag_configure('linha_par', background='#f8f9fa')
        self.tree.tag_configure('linha_impar', background='#ffffff')
        
        scrolly = ttk.Scrollbar(tree_border, orient=VERTICAL, command=self.tree.yview)
        scrollx = ttk.Scrollbar(tree_border, orient=HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrolly.set, xscrollcommand=scrollx.set)
        
        scrolly.pack(side=RIGHT, fill=Y)
        scrollx.pack(side=BOTTOM, fill=X)
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)

        self.tree.bind("<Double-1>", self.on_double_click)

        footer_frame = ttk.Labelframe(self, text="📈 Resumo Financeiro", 
                                      padding=10, bootstyle="success")
        footer_frame.pack(fill=X, pady=10)
        
        stats_frame = ttk.Frame(footer_frame)
        stats_frame.pack(fill=X, pady=(0, 5))
        
        self.lbl_registros = ttk.Label(stats_frame, text="Registros: 0", 
                                       font=("Arial", 10, "bold"))
        self.lbl_registros.pack(side=LEFT, padx=10)
        
        self.lbl_total_proj = ttk.Label(stats_frame, text="💰 Total: R$ 0,00", 
                                        font=("Arial", 10, "bold"))
        self.lbl_total_proj.pack(side=LEFT, padx=10)
        
        self.lbl_comissao = ttk.Label(stats_frame, text="● Comissões: R$ 0,00", 
                                      font=("Arial", 10, "bold"), foreground="#dc3545")
        self.lbl_comissao.pack(side=LEFT, padx=10)
        
        self.lbl_recebido = ttk.Label(stats_frame, text="● Recebido: R$ 0,00", 
                                      font=("Arial", 10, "bold"), foreground="#28a745")
        self.lbl_recebido.pack(side=LEFT, padx=10)
        
        self.lbl_receber = ttk.Label(stats_frame, text="● A Receber: R$ 0,00", 
                                     font=("Arial", 10, "bold"), foreground="#ffc107")
        self.lbl_receber.pack(side=LEFT, padx=10)
        
        self.lbl_lucro = ttk.Label(stats_frame, text="● Lucro: R$ 0,00", 
                                   font=("Arial", 11, "bold"), foreground="#007bff")
        self.lbl_lucro.pack(side=LEFT, padx=10)
        
        btn_frame = ttk.Frame(footer_frame)
        btn_frame.pack(fill=X)
        
        btn_export = ttk.Button(btn_frame, text="💾 Salvar Excel", 
                               command=self.exportar_excel, 
                               bootstyle="success", width=20)
        btn_export.pack(side=RIGHT, padx=5)

        self.on_focus()

    def on_double_click(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        valores = item['values']
        
        detalhes = f"""
📊 DETALHES DO PROJETO

📅 Início: {valores[0]}
📅 Término: {valores[1]}
👤 Cliente: {valores[2]}
📁 Projeto: {valores[3]}
💳 Tipo Pagamento: {valores[4]}
🔢 Parcelas: {valores[5]}

💰 Valor Total: {valores[6]}
● Comissão Paga: {valores[7]}
● Valor Recebido: {valores[8]}
● Ainda a Receber: {valores[9]}
● Lucro Líquido: {valores[10]}
        """
        
        messagebox.showinfo("Detalhes do Projeto", detalhes)

    def limpar_filtros(self):
        self.combo_cliente.set('')
        self.combo_projeto.set('')
        self.combo_arquiteto.set('')
        self.usar_filtro_data.set(False)
        self.carregar_todos_dados()

    def carregar_todos_dados(self):
        try:
            resultados = self.controller.model.get_relatorio_completo()
            self.dados_atuais = resultados
            self.popular_tabela(resultados)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar dados: {e}")

    def carregar_opcoes_combobox(self):
        try:
            model = self.controller.model
            
            clientes = model.get_all_clientes_app_para_combobox()
            self.combo_cliente['values'] = [''] + clientes
            
            arquitetos = model.get_all_arquitetos_para_combobox()
            self.combo_arquiteto['values'] = [''] + arquitetos
            
            projetos_rows = model.get_projetos_agenda_para_combobox()
            self.combo_projeto['values'] = [''] + [f"{p['id']} - {p['descricao']}" for p in projetos_rows]
            
        except Exception as e:
            pass

    def _extrair_texto(self, texto):
        if not texto or texto.strip() == '':
            return None
        if " - " in texto:
            return texto.split(" - ", 1)[1]
        return texto

    def aplicar_filtros(self):
        dt_ini = None
        dt_fim = None
        
        if self.usar_filtro_data.get():
            dt_ini_str = self.date_inicio.entry.get().strip()
            dt_fim_str = self.date_fim.entry.get().strip()
            
            try:
                if dt_ini_str:
                    dt_ini = datetime.strptime(dt_ini_str, "%d/%m/%Y").strftime("%Y-%m-%d")
                if dt_fim_str:
                    dt_fim = datetime.strptime(dt_fim_str, "%d/%m/%Y").strftime("%Y-%m-%d")
            except ValueError:
                messagebox.showerror("Erro", "Formato de data inválido. Use dia/mês/ano.")
                return

        cli = self._extrair_texto(self.combo_cliente.get())
        proj = self._extrair_texto(self.combo_projeto.get())
        arq = self._extrair_texto(self.combo_arquiteto.get())
        
        try:
            resultados = self.controller.model.get_relatorio_completo(
                filtro_data_inicio=dt_ini,
                filtro_data_fim=dt_fim,
                filtro_cliente=cli,
                filtro_projeto=proj,
                filtro_arquiteto=arq,
                filtro_material=None
            )
            self.dados_atuais = resultados
            self.popular_tabela(resultados)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao processar relatório: {e}")

    def popular_tabela(self, dados):
        self.tree.delete(*self.tree.get_children())
        
        soma_total = 0.0
        soma_comissao = 0.0
        soma_recebido = 0.0
        soma_a_receber = 0.0
        soma_lucro = 0.0
        
        for idx, item in enumerate(dados):
            dt_ini = ""
            if item.get('data_inicio'):
                 try: dt_ini = datetime.strptime(item['data_inicio'], "%Y-%m-%d").strftime("%d/%m/%Y")
                 except: dt_ini = item['data_inicio']
            
            dt_fim = ""
            if item.get('data'):
                try: dt_fim = datetime.strptime(item['data'], "%Y-%m-%d").strftime("%d/%m/%Y")
                except: dt_fim = item['data']
            
            item_id = self.tree.insert("", END, values=(
                dt_ini,
                dt_fim,
                item['cliente'] or '',
                item['projeto'] or '',
                item['tipo_pagamento'] or 'N/D',
                item['num_parcelas'] or 0,
                formatar_moeda(str(item['total_projeto'])),
                formatar_moeda(str(item['total_comissao'])),
                formatar_moeda(str(item['valor_pago_cliente'])),
                formatar_moeda(str(item['a_receber'])),
                formatar_moeda(str(item['sobrou_liquido']))
            ), tags=('linha_par' if idx % 2 == 0 else 'linha_impar',))
            
            soma_total += item['total_projeto']
            soma_comissao += item['total_comissao']
            soma_recebido += item['valor_pago_cliente']
            soma_a_receber += item['a_receber']
            soma_lucro += item['sobrou_liquido']
        
        self.lbl_registros.config(text=f"Registros: {len(dados)}")
        self.lbl_total_proj.config(text=f"💰 Total: {formatar_moeda(str(soma_total))}")
        self.lbl_comissao.config(text=f"● Comissões: {formatar_moeda(str(soma_comissao))}")
        self.lbl_recebido.config(text=f"● Recebido: {formatar_moeda(str(soma_recebido))}")
        self.lbl_receber.config(text=f"● A Receber: {formatar_moeda(str(soma_a_receber))}")
        self.lbl_lucro.config(text=f"● Lucro: {formatar_moeda(str(soma_lucro))}")

    def exportar_excel(self):
        if not self.dados_atuais:
            messagebox.showwarning("Aviso", "Não há dados para exportar!")
            return
            
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV (Excel)", "*.csv"), ("Todos os arquivos", "*.*")],
            title="Salvar Relatório Excel"
        )
        
        if not filepath:
            return
            
        try:
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f, delimiter=';')
                
                writer.writerow([
                    "Início", "Término", "Cliente", "Projeto", "Tipo Pagamento", "Parcelas",
                    "Total Projeto", "Comissão Paga", "Valor Recebido", "A Receber", "Lucro Líquido"
                ])
                
                for i in self.dados_atuais:
                    d_ini = ""
                    if i.get('data_inicio'):
                        try: d_ini = datetime.strptime(i['data_inicio'], "%Y-%m-%d").strftime("%d/%m/%Y")
                        except: d_ini = i['data_inicio']
                    
                    d_fim = ""
                    if i.get('data'):
                         try: d_fim = datetime.strptime(i['data'], "%Y-%m-%d").strftime("%d/%m/%Y")
                         except: d_fim = i['data']

                    writer.writerow([
                        d_ini,
                        d_fim,
                        i['cliente'] or '',
                        i['projeto'] or '',
                        i['tipo_pagamento'] or 'N/D',
                        i['num_parcelas'] or 0,
                        str(i['total_projeto']).replace('.', ','),
                        str(i['total_comissao']).replace('.', ','),
                        str(i['valor_pago_cliente']).replace('.', ','),
                        str(i['a_receber']).replace('.', ','),
                        str(i['sobrou_liquido']).replace('.', ',')
                    ])
                
                writer.writerow([])
                soma_total = sum(i['total_projeto'] for i in self.dados_atuais)
                soma_comissao = sum(i['total_comissao'] for i in self.dados_atuais)
                soma_recebido = sum(i['valor_pago_cliente'] for i in self.dados_atuais)
                soma_receber = sum(i['a_receber'] for i in self.dados_atuais)
                soma_lucro = sum(i['sobrou_liquido'] for i in self.dados_atuais)
                
                writer.writerow([
                    '', '', '', '', '', 'TOTAIS:',
                    str(soma_total).replace('.', ','),
                    str(soma_comissao).replace('.', ','),
                    str(soma_recebido).replace('.', ','),
                    str(soma_receber).replace('.', ','),
                    str(soma_lucro).replace('.', ',')
                ])
                
            messagebox.showinfo("✅ Sucesso", 
                              f"Relatório Excel salvo com sucesso!\n\n"
                              f"📊 {len(self.dados_atuais)} registros\n"
                              f"📁 {filepath}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar Excel: {e}")

    def on_focus(self):
        self.carregar_opcoes_combobox()
        self.carregar_todos_dados()