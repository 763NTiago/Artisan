import os
import json
import base64
import sys
from datetime import datetime
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
import re
import subprocess
import tempfile
import jinja2

def get_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

ASSETS_PATH = get_path("assets")
TEMPLATES_PATH = get_path(os.path.join("assets", "templates"))
CSS_PATH = get_path(os.path.join("assets", "css"))
IMAGES_PATH = get_path(os.path.join("assets", "images"))
VENDOR_PATH = get_path("vendor")
APP_DATA_PATH = os.path.join(os.environ.get('APPDATA', os.environ.get('HOME', '.')), "ArtisanOrcamentos")

PATH_LOGO = os.path.join(IMAGES_PATH, "logo.png")
PATH_FUNDO_PADRAO = os.path.join(IMAGES_PATH, "fundo_padrao.png")
PATH_FUNDO_CARTAO = os.path.join(IMAGES_PATH, "fundo_cartao.png")
PATH_WK_LOCAL = get_path(os.path.join("vendor", "wkhtmltopdf", "bin", "wkhtmltopdf.exe"))
PATH_ICONE = get_path("icone.ico")
CONFIG_FILE_PATH = os.path.join(APP_DATA_PATH, "config.json")

PATH_WK_IMG_LOCAL = get_path(os.path.join('vendor', 'wkhtmltopdf', 'bin', 'wkhtmltoimage.exe'))
PATH_QRCODE_INSTA = os.path.join(IMAGES_PATH, "Instagram.png")
PATH_WHATSAPP_ICON = os.path.join(IMAGES_PATH, "whatsapp_icon.png")

if not os.path.exists(APP_DATA_PATH):
    os.makedirs(APP_DATA_PATH)

def get_data_hoje():
    meses = {
        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
        5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
        9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
    }
    hoje = datetime.now()
    return f"{hoje.day} de {meses[hoje.month]} de {hoje.year}"

def formatar_moeda(valor_str):
    try:
        valor_float = float(valor_str.replace(",", "."))
        return f"R$ {valor_float:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except ValueError:
        return "R$ 0,00"

def string_para_float(valor_str):
    if not valor_str:
        return 0.0
    try:
        limpo = ''.join(c for c in valor_str if c.isdigit() or c == ',' or c == '.')
        if ',' in limpo and '.' in limpo:
            limpo = limpo.replace('.', '')
        limpo = limpo.replace(',', '.')
        return float(limpo)
    except ValueError:
        return 0.0
        
def string_para_int(valor_str):
    if not valor_str:
        return 0
    try:
        limpo = ''.join(c for c in valor_str if c.isdigit())
        return int(limpo)
    except ValueError:
        return 0

def formatar_telefone(tel):
    tel = ''.join(filter(str.isdigit, str(tel)))
    if len(tel) == 11:
        return f"({tel[:2]}) {tel[2:7]}-{tel[7:]}"
    elif len(tel) == 10:
        return f"({tel[:2]}) {tel[2:6]}-{tel[6:]}"
    return tel

def formatar_cpf_cnpj(doc):
    doc = ''.join(filter(str.isdigit, str(doc)))
    if len(doc) == 11:
        return f"{doc[:3]}.{doc[3:6]}.{doc[6:9]}-{doc[9:]}"
    elif len(doc) == 14:
        return f"{doc[:2]}.{doc[2:5]}.{doc[5:8]}/{doc[8:12]}-{doc[12:]}"
    return doc

def inicializar_db_persistente(db_name="orcamentos.db"):
    return os.path.join(APP_DATA_PATH, db_name)

def load_config():
    if os.path.exists(CONFIG_FILE_PATH):
        try:
            with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_config(config_data):
    try:
        with open(CONFIG_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4)
    except Exception as e:
        print(f"Erro ao salvar config: {e}")

def load_image_base64(path):
    if not os.path.exists(path):
        return None
    try:
        with open(path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        return encoded_string
    except Exception:
        return None
        
class CurrencyEntry(ttk.Entry):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self.valor_numerico = 0.0
        self.configure(justify='right')
        self.bind("<KeyRelease>", self.on_key_release)
        self.bind("<FocusOut>", self.on_focus_out)
        self.bind("<FocusIn>", self.on_focus_in)
        self.set_value(0.0)

    def formatar_valor(self, texto_puro):
        try:
            if not texto_puro:
                self.valor_numerico = 0.0
                return "0,00"
            valor = int(texto_puro)
            self.valor_numerico = valor / 100.0
            valor_str = f"{self.valor_numerico:,.2f}"
            return valor_str.replace(",", "X").replace(".", ",").replace("X", ".")
        except ValueError:
            return self.get() or "0,00"

    def on_key_release(self, event=None):
        if event and event.keysym not in ('BackSpace', 'Delete', 'Left', 'Right', 'Up', 'Down', 'Tab'):
            texto_atual = self.get() or ""
            texto_puro = "".join(filter(str.isdigit, texto_atual))
            texto_formatado = self.formatar_valor(texto_puro)
            pos_cursor = self.index(INSERT)
            self.delete(0, END)
            self.insert(0, texto_formatado)
            diff = len(texto_formatado) - len(texto_atual)
            if diff != 0:
                self.icursor(pos_cursor + diff)
            else:
                self.icursor(pos_cursor)

    def on_focus_out(self, event=None):
        texto_puro = "".join(filter(str.isdigit, self.get() or ""))
        if not texto_puro:
            self.set_value(0.0)
        else:
            self.delete(0, END)
            self.insert(0, self.formatar_valor(texto_puro))

    def on_focus_in(self, event=None):
        if self.valor_numerico == 0.0:
            self.delete(0, END)
            self.insert(0, "0,00")
        texto_atual = self.get() or ""
        texto_puro = "".join(filter(str.isdigit, texto_atual))
        self.delete(0, END)
        self.insert(0, texto_puro)

    def get_value(self):
        self.on_focus_out() 
        return self.valor_numerico

    def set_value(self, valor_float):
        try:
            self.valor_numerico = float(valor_float)
            valor_str = f"{self.valor_numerico:,.2f}"
            texto_formatado = valor_str.replace(",", "X").replace(".", ",").replace("X", ".")
            self.delete(0, END)
            self.insert(0, texto_formatado)
        except (ValueError, TypeError):
            self.valor_numerico = 0.0
            self.delete(0, END)
            self.insert(0, "0,00")

def gerar_imagem_cartao(nome, porcentagem, data_validade, output_path):
    temp_html_path = None
    try:
        if not os.path.exists(PATH_WK_IMG_LOCAL):
            return False, f"wkhtmltoimage.exe não encontrado em {PATH_WK_IMG_LOCAL}"

        css_path = os.path.join(CSS_PATH, "cartao.css")
        css_content = "" 
        if os.path.exists(css_path):
            with open(css_path, 'r', encoding='utf-8') as f:
                css_content = f.read()

        template_loader = jinja2.FileSystemLoader(searchpath=TEMPLATES_PATH)
        jinja_env = jinja2.Environment(loader=template_loader)
        template = jinja_env.get_template("cartao.html")

        fundo_cartao_base64 = load_image_base64(PATH_FUNDO_CARTAO)
        qrcode_insta_base64 = load_image_base64(PATH_QRCODE_INSTA)
        whatsapp_icon_base64 = load_image_base64(PATH_WHATSAPP_ICON)

        contexto = {
            "nome_cliente": nome,
            "porcentagem": porcentagem,
            "data_validade": data_validade,
            "fundo_cartao_base64": fundo_cartao_base64 or "",
            "qrcode_insta_base64": qrcode_insta_base64 or "",
            "whatsapp_icon_base64": whatsapp_icon_base64 or "",
            "css_style": css_content 
        }
            
        html_renderizado = template.render(contexto)
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.html', mode='w', encoding='utf-8') as temp_html:
            temp_html.write(html_renderizado)
            temp_html_path = temp_html.name

        command = [
            PATH_WK_IMG_LOCAL, '--format', 'png', '--quality', '100',
            '--width', '1080', '--height', '1080', '--disable-smart-width', 
            '--enable-local-file-access', '--no-stop-slow-scripts',
            temp_html_path, output_path
        ]
        
        creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        subprocess.run(command, check=True, creationflags=creationflags, capture_output=True, text=True)
        return True, "Sucesso"

    except Exception as e:
        return False, f"Erro: {str(e)}"
    finally:
        if temp_html_path and os.path.exists(temp_html_path):
            try:
                os.remove(temp_html_path)
            except:
                pass