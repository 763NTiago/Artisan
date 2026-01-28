import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import DateEntry
from tkinter import messagebox, END, X, Y, VERTICAL, BOTH, NS, NSEW, EW, CENTER, W, E, LEFT, TOP, BOTTOM, RIGHT
from .. import utils
from datetime import datetime, timedelta
import calendar

class HomeView(ttk.Frame):
    
    def __init__(self, parent, controller):
        super().__init__(parent, padding=20)
        self.controller = controller
        self.model = controller.model
        self.mes_atual = datetime.now().month
        self.ano_atual = datetime.now().year
        self.eventos_datas = {} 
        
        self.columnconfigure(0, weight=0) 
        self.columnconfigure(1, weight=1)
        self.rowconfigure(1, weight=1)

        header_frame = ttk.Frame(self)
        header_frame.grid(row=0, column=0, columnspan=2, sticky=EW, pady=(0, 15))
        
        titulo_container = ttk.Frame(header_frame)
        titulo_container.pack(side=LEFT)
        
        ttk.Label(titulo_container, text="📊 Dashboard", 
                 font=("Arial", 22, "bold"), bootstyle="primary").pack(side=LEFT)
        ttk.Label(titulo_container, text=datetime.now().strftime("%d/%m/%Y"), 
                 font=("Arial", 12), bootstyle="secondary").pack(side=LEFT, padx=10, pady=(8,0))

        cal_frame = ttk.Labelframe(self, text="Calendário", padding=10, bootstyle="info")
        cal_frame.grid(row=1, column=0, sticky="nw", padx=(0, 20)) 
        
        cal_header = ttk.Frame(cal_frame)
        cal_header.pack(fill=X, pady=(0, 10))
        
        ttk.Button(cal_header, text="<", command=self.mes_anterior, bootstyle="secondary-outline", width=3).pack(side=LEFT)
        self.lbl_mes_ano = ttk.Label(cal_header, text="Mês/Ano", font=("Arial", 11, "bold"), width=18, anchor=CENTER)
        self.lbl_mes_ano.pack(side=LEFT, padx=5)
        ttk.Button(cal_header, text=">", command=self.proximo_mes, bootstyle="secondary-outline", width=3).pack(side=RIGHT)
        
        self.cal_grid = ttk.Frame(cal_frame)
        self.cal_grid.pack()

        kpi_frame = ttk.Frame(self)
        kpi_frame.grid(row=1, column=1, sticky=NSEW)

        self.kpi_proximo = self.criar_kpi(kpi_frame, "Próximo Evento", "--/--/----", "info", "📅")
        self.kpi_proximo.pack(fill=X, pady=(0, 6))
        
        self.kpi_receber_geral = self.criar_kpi(kpi_frame, "Total a Receber (Geral)", "R$ 0,00", "warning", "💰")
        self.kpi_receber_geral.pack(fill=X, pady=(0, 6))
        
        self.kpi_receber_30 = self.criar_kpi(kpi_frame, "A Receber (30 dias)", "R$ 0,00", "primary", "📆")
        self.kpi_receber_30.pack(fill=X, pady=(0, 6))
        
        self.kpi_recebido = self.criar_kpi(kpi_frame, "Total Recebido", "R$ 0,00", "success", "💵")
        self.kpi_recebido.pack(fill=X, pady=(0, 6))
        
        self.kpi_comissao_paga = self.criar_kpi(kpi_frame, "Comissões Já Pagas", "R$ 0,00", "secondary", "🤝")
        self.kpi_comissao_paga.pack(fill=X, pady=(0, 6))

        self.kpi_comissao_futura = self.criar_kpi(kpi_frame, "Comissões a Pagar (Geral)", "R$ 0,00", "danger", "⏳")
        self.kpi_comissao_futura.pack(fill=X, pady=(0, 6))

        self.on_focus()

    def criar_kpi(self, parent, titulo, valor_inicial, bootstyle, icone):
        frame = ttk.Frame(parent, bootstyle=f"{bootstyle}")
        inner = ttk.Frame(frame, padding=10) 
        inner.pack(fill=BOTH, expand=True, padx=2, pady=2) 
        
        lbl_icon = ttk.Label(inner, text=icone, font=("Segoe UI Emoji", 24))
        lbl_icon.pack(side=LEFT, padx=(0, 12))
        
        content = ttk.Frame(inner)
        content.pack(side=LEFT, fill=X, expand=True)
        
        ttk.Label(content, text=titulo, font=("Arial", 10), bootstyle="secondary").pack(anchor=W)
        val_lbl = ttk.Label(content, text=valor_inicial, font=("Arial", 16, "bold"), bootstyle=bootstyle)
        val_lbl.pack(anchor=W)
        
        frame.valor_label = val_lbl
        frame.titulo_label = content.winfo_children()[0]
        return frame

    def atualizar_calendario(self):
        for widget in self.cal_grid.winfo_children():
            widget.destroy()
            
        nome_mes = calendar.month_name[self.mes_atual]
        self.lbl_mes_ano.config(text=f"{nome_mes} {self.ano_atual}")
        
        dias_sem = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
        for idx, dia in enumerate(dias_sem):
            ttk.Label(self.cal_grid, text=dia[0], font=("Arial", 9, "bold"), anchor=CENTER).grid(row=0, column=idx, sticky=EW, pady=(0, 5))
            
        cal = calendar.monthcalendar(self.ano_atual, self.mes_atual)
        self.carregar_eventos_do_mes()
        hoje = datetime.now().date()
        
        for r, semana in enumerate(cal):
            for c, dia in enumerate(semana):
                if dia == 0:
                    ttk.Label(self.cal_grid, text="").grid(row=r+1, column=c)
                    continue
                
                dt_atual = datetime(self.ano_atual, self.mes_atual, dia).date()
                
                estilo = "secondary-outline" 
                tem_evento = False
                
                eventos_dia = self.eventos_datas.get(dt_atual, [])
                
                if eventos_dia:
                    tem_evento = True
                    tipos = [e['tipo'] for e in eventos_dia]
                    
                    if 'vencimento' in tipos:
                        estilo = "danger" 
                    elif 'entrega' in tipos:
                        estilo = "success" 
                    elif 'inicio' in tipos:
                        estilo = "info" 
                    else:
                        estilo = "primary"

                if dt_atual == hoje:
                    estilo = "warning" 

                btn = ttk.Button(self.cal_grid, text=str(dia), bootstyle=estilo,
                                 width=4, 
                                 command=lambda d=dt_atual: self.mostrar_detalhes_dia(d))
                
                btn.grid(row=r+1, column=c, padx=1, pady=1)

    def carregar_eventos_do_mes(self):
        self.eventos_datas = {}
        try:
            projetos = self.model.get_all_projetos_agenda()
            for p in projetos:
                if p['data_inicio']:
                    dt = datetime.strptime(p['data_inicio'], "%Y-%m-%d").date()
                    if dt.month == self.mes_atual and dt.year == self.ano_atual:
                        self._add_evento(dt, 'inicio', f"Início: {p['descricao']} ({p['cliente_nome']})")
                
                if p['data_previsao_termino']:
                    dt = datetime.strptime(p['data_previsao_termino'], "%Y-%m-%d").date()
                    if dt.month == self.mes_atual and dt.year == self.ano_atual:
                        self._add_evento(dt, 'entrega', f"Entrega: {p['descricao']} ({p['cliente_nome']})")

            recebimentos = self.model.get_all_recebimentos()
            for r in recebimentos:
                if r['data_vencimento']:
                    dt = datetime.strptime(r['data_vencimento'], "%Y-%m-%d").date()
                    if dt.month == self.mes_atual and dt.year == self.ano_atual:
                        val = utils.formatar_moeda(str(r['valor_parcela']))
                        self._add_evento(dt, 'vencimento', f"Receber: {val} - {r['cliente_nome']}")

        except Exception as e:
            print(f"Erro ao carregar eventos: {e}")

    def _add_evento(self, data, tipo, descricao):
        if data not in self.eventos_datas:
            self.eventos_datas[data] = []
        self.eventos_datas[data].append({'tipo': tipo, 'desc': descricao})

    def mostrar_detalhes_dia(self, data):
        eventos = self.eventos_datas.get(data, [])
        data_fmt = data.strftime("%d/%m/%Y")
        
        if not eventos:
            messagebox.showinfo(f"Agenda - {data_fmt}", "Nenhum evento agendado para este dia.")
            return
            
        texto = f"📅 Eventos para {data_fmt}:\n\n"
        for e in eventos:
            icone = "🔹"
            if e['tipo'] == 'vencimento': icone = "💰"
            elif e['tipo'] == 'entrega': icone = "✅"
            elif e['tipo'] == 'inicio': icone = "🚀"
            
            texto += f"{icone} {e['desc']}\n"
            
        messagebox.showinfo(f"Agenda - {data_fmt}", texto)

    def mes_anterior(self):
        if self.mes_atual == 1:
            self.mes_atual = 12
            self.ano_atual -= 1
        else:
            self.mes_atual -= 1
        self.atualizar_calendario()

    def proximo_mes(self):
        if self.mes_atual == 12:
            self.mes_atual = 1
            self.ano_atual += 1
        else:
            self.mes_atual += 1
        self.atualizar_calendario()

    def on_focus(self):
        try:
            total_receber_geral = self.model.get_total_a_receber_geral()
            self.kpi_receber_geral.valor_label.config(text=utils.formatar_moeda(str(total_receber_geral)))

            total_receber_30 = self.model.get_total_a_receber_30d()
            self.kpi_receber_30.valor_label.config(text=utils.formatar_moeda(str(total_receber_30)))

            prox_evento = self.model.get_proximo_evento_unificado()
            if prox_evento:
                data_ev, tipo_ev, desc_ev, cli_ev, dias = prox_evento
                try:
                    data_formatada = datetime.strptime(data_ev, "%Y-%m-%d").strftime("%d/%m/%Y")
                except:
                    data_formatada = data_ev
                self.kpi_proximo.titulo_label.config(text=f"{tipo_ev}: {desc_ev}")
                self.kpi_proximo.valor_label.config(text=data_formatada)
            else:
                self.kpi_proximo.titulo_label.config(text="Próximo Evento")
                self.kpi_proximo.valor_label.config(text="--/--/----")

            total_recebido = self.model.get_total_recebido_geral()
            self.kpi_recebido.valor_label.config(text=utils.formatar_moeda(str(total_recebido)))
            
            total_comissao_paga = self.model.get_total_comissoes_ja_pagas()
            self.kpi_comissao_paga.valor_label.config(text=utils.formatar_moeda(str(total_comissao_paga)))

            comissao_pendente = self.model.get_total_comissoes_pendentes()
            self.kpi_comissao_futura.valor_label.config(text=utils.formatar_moeda(str(comissao_pendente)))
            
            self.atualizar_calendario()
                
        except Exception as e:
            print(f"Erro ao atualizar KPIs: {e}")