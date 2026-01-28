import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from .cliente_view import ClienteView
from .itens_view import ItensView
from .termos_view import TermosView
from .historico_view import HistoricoView
from .materiais_view import MateriaisView
from .config_view import ConfigView

class OrcamentoView(ttk.Frame):
    """
    Uma view "container" auto-contida que agrupa tudo de Orçamentos
    usando sub-abas (Notebook).
    """
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.frame_botoes = ttk.Frame(self, padding=(10, 15))
        self.frame_botoes.pack(side=BOTTOM, fill=X)
        
        self.btn_save = ttk.Button(
            self.frame_botoes, 
            text="💾 SALVAR PDF E NO HISTÓRICO", 
            command=self.controller.save_pdf_e_historico, 
            bootstyle="danger"
        )
        self.btn_save.pack(side=RIGHT, padx=(5, 0)) 

        self.btn_preview = ttk.Button(
            self.frame_botoes, 
            text="👁️ VISUALIZAR PDF", 
            command=self.controller.preview_pdf, 
            bootstyle="success-outline"
        )
        self.btn_preview.pack(side=RIGHT, padx=5)

        self.notebook_orcamento = ttk.Notebook(self, bootstyle="primary")
        self.notebook_orcamento.pack(side=TOP, fill=BOTH, expand=True, pady=5)
        
        self.view_cliente = ClienteView(self.notebook_orcamento, self.controller)
        self.notebook_orcamento.add(self.view_cliente, text="👤 Cliente")

        self.view_itens = ItensView(self.notebook_orcamento, self.controller)
        self.notebook_orcamento.add(self.view_itens, text="📋 Itens do Orçamento")

        self.view_termos = TermosView(self.notebook_orcamento, self.controller)
        self.notebook_orcamento.add(self.view_termos, text="📄 Termos e Pagamento")

        self.view_historico = HistoricoView(self.notebook_orcamento, self.controller)
        self.notebook_orcamento.add(self.view_historico, text="📈 Histórico")
        
        self.view_materiais = MateriaisView(self.notebook_orcamento, self.controller)
        self.notebook_orcamento.add(self.view_materiais, text="🛠️ Materiais")
        
        self.view_config = ConfigView(self.notebook_orcamento, self.controller)
        self.notebook_orcamento.add(self.view_config, text="⚙️ Configurações")
        
