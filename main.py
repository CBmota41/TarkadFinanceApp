# main.py
# Tarkad Finance App para Android (Kivy + KivyMD)

import os
os.environ['KIVY_METRICS_DENSITY'] = '2'
os.environ['KIVY_METRICS_FONTSCALE'] = '1'

# Verifica se está no Android e configura as permissões
from kivy.utils import platform
if platform == 'android':
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.READ_EXTERNAL_STORAGE, 
                        Permission.WRITE_EXTERNAL_STORAGE])
    
    # Configura o matplotlib para usar um backend não interativo
    import matplotlib
    matplotlib.use('Agg')

from kivy.config import Config
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '600')

from kivy.metrics import dp

# CORREÇÃO DO ERRO DO dp(1)
original_dp = dp
def safe_dp(value):
    result = original_dp(value)
    return max(result, 1)  # Garante que nunca seja 0

dp = safe_dp

# Resto das importações...
import json
import tempfile
import calendar
from datetime import datetime, date
from functools import partial

import pandas as pd
import matplotlib.pyplot as plt

from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen

from kivymd.app import MDApp
from kivymd.uix.list import OneLineListItem, MDList
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.textfield import MDTextField
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.navigationdrawer import MDNavigationLayout, MDNavigationDrawer
from kivymd.uix.card import MDCard
from kivymd.uix.menu import MDDropdownMenu
from kivy.properties import BooleanProperty, ColorProperty
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from kivymd.uix.label import MDLabel
import io
from kivy.metrics import dp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivy.uix.scrollview import ScrollView
from datetime import datetime, date
import pandas as pd
import os
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

KV = '''
<HeaderBar@MDTopAppBar>:
    title: app.title
    left_action_items: [["menu", lambda x: app.toggle_nav_drawer()]]
    right_action_items: 
        [
        ["filter", lambda x: app.menu_mes.open()],  # Novo botão de filtro
        ["refresh", lambda x: app.refresh_ui()]
        ]

<TreeItem>:
    cols: 5
    size_hint_y: None
    height: dp(40)
    spacing: dp(5)
    padding: dp(2)
    
    MDLabel:
        text: root.data
        size_hint_x: 0.2
        theme_text_color: "Custom"
        text_color: root.cor_texto
        halign: "center"
    
    MDLabel:
        text: root.valor
        size_hint_x: 0.2
        theme_text_color: "Custom"
        text_color: root.cor_texto
        halign: "center"
    
    MDLabel:
        text: root.tipo
        size_hint_x: 0.15
        theme_text_color: "Custom"
        text_color: root.cor_texto
        halign: "center"
    
    MDLabel:
        text: root.meio
        size_hint_x: 0.2
        theme_text_color: "Custom"
        text_color: root.cor_texto
        halign: "center"
    
    MDLabel:
        text: root.descricao
        size_hint_x: 0.25
        theme_text_color: "Custom"
        text_color: root.cor_texto
        halign: "left"
        shorten: True

Screen:
    MDNavigationLayout:
        id: nav_layout

        ScreenManager:
            id: screen_manager

            Screen:
                name: "main_screen"

                BoxLayout:
                    orientation: "vertical"

                    HeaderBar:
                        id: topbar
                        elevation: 10
                        left_action_items: [["menu", lambda x: app.toggle_nav_drawer()]]
                        right_action_items: 
                            [
                            ["filter", lambda x: app.menu_mes.open()],
                            ["refresh", lambda x: app.refresh_ui()]
                            ]

                    # CONTEÚDO PRINCIPAL - SEMPRE VISÍVEL
                    BoxLayout:
                        orientation: "vertical"
                        padding: dp(8)
                        spacing: dp(8)

                        # LABELS DE TOTAL
                        MDBoxLayout:
                            adaptive_height: True
                            spacing: dp(8)
                            MDCard:
                                size_hint: 0.5, None
                                height: dp(80)
                                padding: dp(8)
                                MDLabel:
                                    id: lbl_total
                                    text: "TOTAL: R$ 0,00"
                                    theme_text_color: "Primary"
                                    halign: "center"
                            
                            MDCard:
                                size_hint: 0.5, None
                                height: dp(80)
                                padding: dp(8)
                                MDLabel:
                                    id: lbl_receitas
                                    text: "RECEITAS: R$ 0,00"
                                    theme_text_color: "Primary"
                                    halign: "center"

                        MDBoxLayout:
                            adaptive_height: True
                            spacing: dp(8)
                            MDCard:
                                size_hint: 0.5, None
                                height: dp(80)
                                padding: dp(8)
                                MDLabel:
                                    id: lbl_despesas
                                    text: "DESPESAS: R$ 0,00"
                                    theme_text_color: "Primary"
                                    halign: "center"
                            
                            MDCard:
                                size_hint: 0.5, None
                                height: dp(80)
                                padding: dp(8)
                                MDLabel:
                                    id: lbl_corr
                                    text: "INVEST: R$ 0,00"
                                    theme_text_color: "Primary"
                                    halign: "center"

                        # TREEVIEW
                        BoxLayout:
                            orientation: 'vertical'
                            padding: dp(8)
                            spacing: dp(8)
                            
                            # Cabeçalho da tabela
                            GridLayout:
                                cols: 5
                                size_hint_y: None
                                height: dp(40)
                                spacing: dp(5)
                                padding: dp(5)
                                
                                MDLabel:
                                    text: "DATA"
                                    bold: True
                                    size_hint_x: 0.2
                                    halign: "center"
                                MDLabel:
                                    text: "VALOR"
                                    bold: True
                                    size_hint_x: 0.2
                                    halign: "center"
                                MDLabel:
                                    text: "TIPO"
                                    bold: True
                                    size_hint_x: 0.15
                                    halign: "center"
                                MDLabel:
                                    text: "MEIO"
                                    bold: True
                                    size_hint_x: 0.2
                                    halign: "center"
                                MDLabel:
                                    text: "DESCRIÇÃO"
                                    bold: True
                                    size_hint_x: 0.25
                                    halign: "center"
                            
                            # Corpo da tabela com scroll
                            ScrollView:
                                id: scroll_tree
                                MDList:
                                    id: tree_list
                                    padding: dp(5)
                                    spacing: dp(2)

        # MENU HAMBURGUER (FORA do conteúdo principal)
        MDNavigationDrawer:
            id: nav_drawer
            size_hint: 0.8, 1
            elevation: 12
            auto_dismiss: False

            ScrollView:
                do_scroll_x: False
                
                BoxLayout:
                    orientation: "vertical"
                    size_hint_y: None
                    height: self.minimum_height
                    padding: dp(10)
                    spacing: dp(10)
                    
                    MDLabel:
                        text: "NOVO LANÇAMENTO"
                        font_style: "H6"
                        size_hint_y: None
                        height: dp(40)
                        halign: "center"
                        bold: True
                    
                    GridLayout:
                        cols: 1
                        size_hint_y: None
                        height: self.minimum_height
                        spacing: dp(8)
                        padding: dp(5)
                        
                        MDTextField:
                            id: entry_date
                            hint_text: "Data (toque para selecionar)"
                            readonly: True
                            on_focus: if self.focus: app.show_date_picker()
                            text: app.default_date_str
                            size_hint_y: None
                            height: dp(56)
                                                
                        MDTextField:
                            id: entry_valor
                            hint_text: "Valor (ex: 150.50)"
                            input_filter: "float"
                            size_hint_y: None
                            height: dp(56)
                        
                        MDTextField:
                            id: entry_tipo
                            hint_text: "Tipo"
                            text: "DESPESA"
                            readonly: True
                            on_focus: if self.focus: app.menu_tipo.open()
                            size_hint_y: None
                            height: dp(56)
                        
                        MDTextField:
                            id: entry_meio
                            hint_text: "Meio de Pagamento"
                            text: "PIX"
                            readonly: True
                            on_focus: if self.focus: app.menu_meio.open()
                            size_hint_y: None
                            height: dp(56)
                        
                        MDTextField:
                            id: entry_categoria
                            hint_text: "Categoria"
                            text: "OUTROS"
                            readonly: True
                            on_focus: if self.focus: app.menu_categoria.open()
                            size_hint_y: None
                            height: dp(56)
                        
                        MDTextField:
                            id: entry_desc
                            hint_text: "Descrição"
                            size_hint_y: None
                            height: dp(56)
                    
                    BoxLayout:
                        size_hint_y: None
                        height: dp(60)
                        spacing: dp(8)
                        padding: dp(5)
                        
                        MDRaisedButton:
                            text: "ADICIONAR"
                            md_bg_color: app.theme_cls.primary_color
                            on_release: app.add_entry()
                        
                        MDFlatButton:
                            text: "LIMPAR"
                            on_release: app.limpar_campos()
                    
                    # BOTÃO PARA EXPORTAR RELATÓRIO
                    MDRaisedButton:
                        size_hint_y: None
                        height: dp(40)
                        text: "EXPORTAR RELATÓRIO"
                        md_bg_color: app.theme_cls.accent_color
                        on_release: app.export_pdf_prompt()
                    
                    MDFlatButton:
                        size_hint_y: None
                        height: dp(40)
                        text: "FECHAR"
                        theme_text_color: "Custom"
                        text_color: app.theme_cls.primary_color
                        on_release: app.toggle_nav_drawer()

'''

# ---------- Config / Defaults ----------
USERS = ["MOTA", "ROGERIO", "CRISLAINE", "ALEXANDRE", "CALVO", "COBAIA"]
COLUMNS = ["DATA","VALOR","TIPO","MEIO","DESCRICAO","CATEGORIA"]

def format_currency(x):
    try:
        return f"R$ {float(x):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "R$ 0,00"

class RowWidget(BoxLayout):
    idx = NumericProperty(0)
    index = NumericProperty(0)
    date_text = StringProperty("")
    valor_text = StringProperty("")
    tipo = StringProperty("")
    meio = StringProperty("")
    categoria = StringProperty("")
    descricao = StringProperty("")
    long_press_event = None

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            # schedule long-press
            self.long_press_event = Clock.schedule_once(self._do_long_press, 0.5)
        return super().on_touch_down(touch)

    def on_touch_up(self, touch):
        if self.long_press_event and self.long_press_event.is_triggered is False:
            self.long_press_event.cancel()
            # it's a tap -> open edit menu (also allow tap to select)
            app = MDApp.get_running_app()
            app.open_edit_menu(self.idx)
        return super().on_touch_up(touch)

    def _do_long_press(self, dt):
        # long press -> open edit dialog
        app = MDApp.get_running_app()
        app.open_edit_dialog(self.idx)

    def on_paid_toggled(self, idx, state):
        app = MDApp.get_running_app()
        

class TreeItem(BoxLayout):
    data = StringProperty("")
    valor = StringProperty("")
    tipo = StringProperty("")
    meio = StringProperty("")
    descricao = StringProperty("")
    cor_texto = ColorProperty([0, 0, 0, 1])
    idx = NumericProperty(0)
    real_idx = NumericProperty(0)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            # Long press para editar
            app = MDApp.get_running_app()
            Clock.schedule_once(lambda dt: app.open_edit_menu(self.idx), 0.5)
        return super().on_touch_down(touch)

class TarkadAndroidApp(MDApp):
    title = "TARKAD FINANCE"
    default_date_str = StringProperty(datetime.now().strftime("%d/%m/%Y"))
    data_file = StringProperty()
    df = None
    md_items = ListProperty([])
    # Define o mês atual como padrão
    mes_filtro = StringProperty(f"{datetime.now().month:02d}")

    TIPOS = ["DESPESA", "RECEITA"]
    MEIOS = ["PIX", "DINHEIRO", "CARTAO DE CRÉDITO", "CARTAO DE DÉBITO", "OUTROS"]
    CATEGORIAS = [
        "ALIMENTACAO", "TRANSPORTE", "ROUPA", "ESTUDO", "INVESTIMENTOS",
        "LAZER", "VIAGEM", "FIRULA", "OUTROS", "CONTAS FIXAS", "MERCADO",
        "DIVIDENDOS", "SAQUE DE DIVIDENDOS", "SALARIO", "APOSTAS", "CASA"
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.menu_tipo = None
        self.menu_meio = None
        self.menu_categoria = None
        self.menu_mes = None

    def get_nome_mes(self, mes_num):
        """Retorna o nome do mês a partir do número"""
        meses = [
            "JANEIRO", "FEVEREIRO", "MARÇO", "ABRIL", "MAIO", "JUNHO",
            "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"
        ]
        return meses[mes_num - 1] if 1 <= mes_num <= 12 else ""

    def export_pdf_prompt(self):
        """Abre diálogo para escolher o período do relatório"""
        content = MDBoxLayout(orientation="vertical", spacing=dp(15), adaptive_height=True)
        
        # Opção de período
        period_label = MDLabel(text="Exportar por:", size_hint_y=None, height=dp(20))
        content.add_widget(period_label)
        
        # Usar um MDDropDownItem em vez de MDTextField
        period_dropdown = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(56),
                                     adaptive_width=True)
        period_text = MDLabel(text="MÊS", size_hint_x=None, width=dp(200))
        period_dropdown.add_widget(period_text)
        period_button = MDRaisedButton(text="Selecionar", size_hint_x=None, width=dp(100))
        period_dropdown.add_widget(period_button)
        content.add_widget(period_dropdown)
        
        # Menu dropdown para período
        period_options = ["MÊS", "PERÍODO", "ANO INTEIRO", "GERAL"]
        period_menu_items = []
        for option in period_options:
            period_menu_items.append({
                "text": option,
                "viewclass": "OneLineListItem",
                "on_release": lambda opt=option: self.set_period_option(period_text, period_menu, opt)
            })

        
        period_menu = MDDropdownMenu(
            caller=period_button,
            items=period_menu_items,
            width_mult=4
        )
        
        period_button.bind(on_release=lambda x: period_menu.open())
        
        # Mês específico (só aparece se período for "MÊS")
        self.month_container = MDBoxLayout(orientation='vertical', size_hint_y=None, height=0, adaptive_height=True)
        content.add_widget(self.month_container)
        
        month_label = MDLabel(text="Mês:", size_hint_y=None, height=dp(20))
        self.month_container.add_widget(month_label)
        
        month_dropdown = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(56),
                                    adaptive_width=True)
        month_text = MDLabel(text=datetime.now().strftime("%B").upper(), size_hint_x=None, width=dp(200))
        month_dropdown.add_widget(month_text)
        month_button = MDRaisedButton(text="Selecionar", size_hint_x=None, width=dp(100))
        month_dropdown.add_widget(month_button)
        self.month_container.add_widget(month_dropdown)
        
        # Menu dropdown para mês
        meses = ["JANEIRO", "FEVEREIRO", "MARÇO", "ABRIL", "MAIO", "JUNHO", 
                 "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"]
        month_menu_items = []
        for mes in meses:
            month_menu_items.append({
                "text": mes,
                "viewclass": "OneLineListItem",
                "on_release": lambda m=mes: self.set_month_option(month_text, month_menu, m)
            })

        
        month_menu = MDDropdownMenu(
            caller=month_button,
            items=month_menu_items,
            width_mult=4
        )
        
        month_button.bind(on_release=lambda x: month_menu.open())
        
        # Período personalizado (só aparece se período for "PERÍODO")
        self.period_container = MDBoxLayout(orientation='vertical', size_hint_y=None, height=0, adaptive_height=True)
        content.add_widget(self.period_container)
        
        start_label = MDLabel(text="Data início (DD/MM/AAAA):", size_hint_y=None, height=dp(20))
        self.period_container.add_widget(start_label)
        
        start_field = MDTextField(
            size_hint_y=None,
            height=dp(56)
        )
        self.period_container.add_widget(start_field)
        
        end_label = MDLabel(text="Data fim (DD/MM/AAAA):", size_hint_y=None, height=dp(20))
        self.period_container.add_widget(end_label)
        
        end_field = MDTextField(
            size_hint_y=None,
            height=dp(56)
        )
        self.period_container.add_widget(end_field)
        
        # Inicialmente esconder os containers
        self.month_container.height = 0
        self.month_container.opacity = 0
        self.period_container.height = 0
        self.period_container.opacity = 0
        
        dialog = MDDialog(
            title="Exportar Relatório - Opções",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="CANCELAR", on_release=lambda x: dialog.dismiss()),
                MDRaisedButton(text="EXPORTAR", on_release=lambda x: self._confirm_export(
                    dialog, period_text.text, month_text.text, start_field.text, end_field.text
                ))
            ]
        )
        
        # Guardar referência para atualizar a UI
        self.export_dialog = dialog
        self.period_text = period_text
        self.month_text = month_text
        self.start_field = start_field
        self.end_field = end_field
        
        dialog.open()

    def set_period_option(self, field, menu, option):
        field.text = option
        menu.dismiss()
        
        # Mostrar/ocultar containers baseado na seleção
        if option == "MÊS":
            self.month_container.height = dp(136)  # label + dropdown
            self.month_container.opacity = 1
            self.period_container.height = 0
            self.period_container.opacity = 0
        elif option == "PERÍODO":
            self.month_container.height = 0
            self.month_container.opacity = 0
            self.period_container.height = dp(192)  # 2 labels + 2 fields
            self.period_container.opacity = 1
        else:  # ANO INTEIRO ou GERAL
            self.month_container.height = 0
            self.month_container.opacity = 0
            self.period_container.height = 0
            self.period_container.opacity = 0

    def set_month_option(self, field, menu, month):
        field.text = month
        menu.dismiss()

    def _confirm_export(self, dialog, period_option, month_option, start_text, end_text):
        try:
            year = datetime.now().year

            if period_option == "MÊS":
                meses = ["JANEIRO", "FEVEREIRO", "MARÇO", "ABRIL", "MAIO", "JUNHO",
                         "JULHO", "AGOSTO", "SETEMBRO", "OUTUBRO", "NOVEMBRO", "DEZEMBRO"]
                
                if not month_option or month_option == "GERAL":
                    # Geral = sem filtro de mês
                    start = date(1900, 1, 1)
                    end = date(2100, 12, 31)
                else:
                    month_index = meses.index(month_option) + 1
                    start = date(year, month_index, 1)
                    if month_index == 12:
                        end = date(year, 12, 31)
                    else:
                        end = date(year, month_index + 1, 1) - pd.Timedelta(days=1)

            elif period_option == "PERÍODO":
                if not start_text or not end_text:
                    # Se vazio, usa mês atual inteiro
                    m = datetime.now().month
                    start = date(year, m, 1)
                    if m == 12:
                        end = date(year, 12, 31)
                    else:
                        end = date(year, m + 1, 1) - pd.Timedelta(days=1)
                else:
                    start = datetime.strptime(start_text, "%d/%m/%Y").date()
                    end = datetime.strptime(end_text, "%d/%m/%Y").date()

            elif period_option == "ANO INTEIRO":
                start = date(year, 1, 1)
                end = date(year, 12, 31)

            else:  # GERAL
                start = date(1900, 1, 1)
                end = date(2100, 12, 31)

            dialog.dismiss()
            filepath = self.export_pdf(start, end)

            # Abrir automaticamente
            if platform == "android":
                from jnius import autoclass
                Intent = autoclass('android.content.Intent')
                Uri = autoclass('android.net.Uri')
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                intent = Intent(Intent.ACTION_VIEW)
                intent.setDataAndType(Uri.parse("file://" + filepath), "application/pdf")
                intent.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                PythonActivity.mActivity.startActivity(intent)
            else:
                import webbrowser
                if os.path.exists(filepath):
                    webbrowser.open_new(filepath)

        except Exception as e:
            self.show_message(f"Erro ao processar datas: {str(e)}")

    def export_pdf(self, start, end):
        """Exporta os dados para PDF"""
        try:
            # Filtrar dados pelo período
            df = self.df.copy()
            df = df[pd.to_datetime(df["DATA"]).dt.date >= start]
            df = df[pd.to_datetime(df["DATA"]).dt.date <= end]
            
            if df.empty:
                self.show_message("Não há dados nesse período")
                return
            
            # Criar nome do arquivo
            user = os.environ.get("USER", "USER")
            filename = f"RELATORIO_{user}_{start.strftime('%Y%m%d')}_{end.strftime('%Y%m%d')}.pdf"
            
            # Configuração de caminho para Android
            if platform == "android":
                try:
                    from android.storage import app_storage_path
                    base = app_storage_path()
                    # Cria o diretório se não existir
                    os.makedirs(base, exist_ok=True)
                except ImportError:
                    base = os.path.join(os.path.expanduser("~"), "Documents")
            else:
                base = os.path.join(os.path.expanduser("~"), "Documents")
            
            filepath = os.path.join(base, filename)
            
            # Criar gráficos
            fig1 = plt.figure(figsize=(10, 5))
            ax1 = fig1.add_subplot(111)
            receitas = df[df["VALOR"] > 0].groupby("CATEGORIA")["VALOR"].sum().sort_values(ascending=False)
            if not receitas.empty:
                receitas.plot(kind="bar", ax=ax1)
                ax1.set_title("RECEITAS POR CATEGORIA")
                plt.xticks(rotation=45, ha='right')
            else:
                ax1.text(0.5, 0.5, "SEM RECEITAS", ha="center", va="center")
            
            buf1 = io.BytesIO()
            fig1.tight_layout()
            fig1.savefig(buf1, format='png', dpi=150)
            plt.close(fig1)
            
            fig2 = plt.figure(figsize=(10, 5))
            ax2 = fig2.add_subplot(111)
            despesas = df[df["VALOR"] < 0].groupby("CATEGORIA")["VALOR"].sum().abs().sort_values(ascending=False)
            if not despesas.empty:
                despesas.plot(kind="bar", ax=ax2, color='tab:red')
                ax2.set_title("DESPESAS POR CATEGORIA")
                plt.xticks(rotation=45, ha='right')
            else:
                ax2.text(0.5, 0.5, "SEM DESPESAS", ha="center", va="center")
            
            buf2 = io.BytesIO()
            fig2.tight_layout()
            fig2.savefig(buf2, format='png', dpi=150)
            plt.close(fig2)
            
            # Criar PDF
            c = canvas.Canvas(filepath, pagesize=landscape(A4))
            w, h = landscape(A4)
            
            # Título
            c.setFont("Helvetica-Bold", 18)
            title = "RELATÓRIO FINANCEIRO"
            c.drawString(40, h - 40, title)
            
            c.setFont("Helvetica", 10)
            periodo_str = f"PERÍODO: {start.strftime('%d/%m/%Y')} - {end.strftime('%d/%m/%Y')}"
            c.drawString(40, h - 60, periodo_str)
            
            # Gráficos
            buf1.seek(0)
            buf2.seek(0)
            
            img1 = ImageReader(buf1)
            img2 = ImageReader(buf2)
            
            c.drawImage(img1, 40, h - 350, width=350, height=250)
            c.drawImage(img2, 430, h - 350, width=350, height=250)
            
            # Tabela com dados
            c.setFont("Helvetica-Bold", 10)
            y = h - 400
            headers = ["DATA", "VALOR", "TIPO", "MEIO", "CATEGORIA", "DESCRIÇÃO"]
            positions = [40, 100, 160, 220, 280, 400]
            
            for header, pos in zip(headers, positions):
                c.drawString(pos, y, header)
            
            c.setFont("Helvetica", 8)
            y -= 15
            
            for _, row in df.sort_values("DATA").iterrows():
                if y < 60:
                    c.showPage()
                    y = h - 40
                    c.setFont("Helvetica-Bold", 10)
                    for header, pos in zip(headers, positions):
                        c.drawString(pos, y, header)
                    y -= 15
                    c.setFont("Helvetica", 8)
                
                values = [
                    pd.to_datetime(row["DATA"]).strftime("%d/%m/%Y"),
                    format_currency(row["VALOR"]),
                    row["TIPO"],
                    row["MEIO"],
                    str(row["CATEGORIA"]),
                    str(row["DESCRICAO"])[:30]
                ]
                
                for value, pos in zip(values, positions):
                    c.drawString(pos, y, str(value))
                
                y -= 12
            
            # Resumo
            c.showPage()
            y = h - 40
            c.setFont("Helvetica-Bold", 14)
            c.drawString(40, y, "RESUMO DO PERÍODO")
            y -= 25
            
            c.setFont("Helvetica", 12)
            entradas = df[df["VALOR"] > 0]["VALOR"].sum()
            saidas = df[df["VALOR"] < 0]["VALOR"].sum()
            total = entradas + saidas
            
            c.drawString(40, y, f"TOTAL: {format_currency(total)}")
            y -= 20
            c.drawString(40, y, f"ENTRADAS: {format_currency(entradas)}")
            y -= 20
            c.drawString(40, y, f"SAÍDAS: {format_currency(saidas)}")
            y -= 30
            
            # Ranking de categorias
            c.setFont("Helvetica-Bold", 12)
            c.drawString(40, y, "TOP 5 - MAIORES GASTOS")
            y -= 20
            c.setFont("Helvetica", 10)
            
            top_gastos = despesas.head(5)
            for cat, val in top_gastos.items():
                c.drawString(40, y, f"{cat}: {format_currency(val)}")
                y -= 15
            
            y -= 10
            c.setFont("Helvetica-Bold", 12)
            c.drawString(40, y, "TOP 5 - MAIORES GANHOS")
            y -= 20
            c.setFont("Helvetica", 10)
            
            top_ganhos = receitas.head(5)
            for cat, val in top_ganhos.items():
                c.drawString(40, y, f"{cat}: {format_currency(val)}")
                y -= 15
            
            c.save()
            buf1.close()
            buf2.close()
            self.show_message(f"PDF gerado com sucesso: {filepath}")
            return filepath
            
        except Exception as e:
            self.show_message(f"Erro ao gerar PDF: {str(e)}")

    def create_dropdown_menus(self):
        # Função factory para criar callbacks (corrigida)
        def create_callback(func, *args):
            return lambda *a, **k: func(*args)
        
        # Menu para Tipo
        tipo_items = []
        for item in self.TIPOS:
            tipo_items.append({
                "text": item, 
                "viewclass": "OneLineListItem", 
                "on_release": create_callback(self.set_tipo, item)
            })
        
        self.menu_tipo = MDDropdownMenu(
            caller=self.root.ids.entry_tipo,
            items=tipo_items,
            width_mult=4
        )
        
        # Menu para Meio
        meio_items = []
        for item in self.MEIOS:
            meio_items.append({
                "text": item, 
                "viewclass": "OneLineListItem", 
                "on_release": create_callback(self.set_meio, item)
            })
        
        self.menu_meio = MDDropdownMenu(
            caller=self.root.ids.entry_meio,
            items=meio_items,
            width_mult=4
        )
        
        # Menu para Categoria
        categoria_items = []
        for item in self.CATEGORIAS:
            categoria_items.append({
                "text": item, 
                "viewclass": "OneLineListItem", 
                "on_release": create_callback(self.set_categoria, item)
            })
        
        self.menu_categoria = MDDropdownMenu(
            caller=self.root.ids.entry_categoria,
            items=categoria_items,
            width_mult=4
        )
        
        # Menu para Filtro de Mês
        mes_atual = datetime.now().month
        self.mes_filtro = f"{mes_atual:02d}"
        
        mes_items = [{
            "text": "GERAL", 
            "viewclass": "OneLineListItem", 
            "on_release": create_callback(self.set_mes_filtro, "GERAL")
        }]
        
        for i in range(1, 13):
            mes_items.append({
                "text": f"{i:02d} - {self.get_nome_mes(i)}", 
                "viewclass": "OneLineListItem", 
                "on_release": create_callback(self.set_mes_filtro, f"{i:02d}")
            })
        
        self.menu_mes = MDDropdownMenu(
            caller=self.root.ids.topbar,
            items=mes_items,
            width_mult=4
        )

    def set_mes_filtro(self, mes):
        """Define o filtro de mês e atualiza a interface"""
        self.mes_filtro = mes
        self.menu_mes.dismiss()
        self.refresh_ui()

    def on_tipo_selected(self, tipo):
        # Atualiza automaticamente o sinal do valor baseado no tipo
        try:
            valor_text = self.root.ids.entry_valor.text
            if valor_text:
                valor = float(valor_text.replace(",", "."))
                if tipo == "DESPESA" and valor > 0:
                    self.root.ids.entry_valor.text = f"{-valor}"
                elif tipo == "RECEITA" and valor < 0:
                    self.root.ids.entry_valor.text = f"{abs(valor)}"
        except:
            pass

    def set_tipo(self, text):
        self.root.ids.entry_tipo.text = text
        self.menu_tipo.dismiss()
        self.on_tipo_selected(text)

    def set_meio(self, text):
        self.root.ids.entry_meio.text = text
        self.menu_meio.dismiss()

    def set_categoria(self, text):
        self.root.ids.entry_categoria.text = text
        self.menu_categoria.dismiss()

    def on_start(self):
        # Configuração inicial
        self.root.ids.nav_drawer.set_state("close")
        
        # Foca no campo de valor quando o menu abre
        def focus_valor_field(dt):
            if self.root.ids.nav_drawer.state == "open":
                self.root.ids.entry_valor.focus = True
        
        # Agenda o foco após a abertura do menu
        Clock.schedule_once(focus_valor_field, 0.3)

    def toggle_nav_drawer(self):
        drawer = self.root.ids.nav_drawer
        if drawer.state == "open":
            drawer.set_state("close")
            # Remove o foco de todos os campos
            for child in drawer.walk(restrict=True):
                if hasattr(child, 'focus'):
                    child.focus = False
        else:
            drawer.set_state("open")
            # Foca no campo de valor quando abre
            Clock.schedule_once(lambda dt: setattr(self.root.ids.entry_valor, 'focus', True), 0.1)

    def limpar_campos(self):
        self.root.ids.entry_valor.text = ""
        self.root.ids.entry_desc.text = ""

    def build(self):
        # decide path
        user = os.environ.get("USER", "USER")
        if platform == "android":
            try:
                from android.storage import app_storage_path
                base = app_storage_path()
                # Cria o diretório se não existir
                os.makedirs(base, exist_ok=True)
            except ImportError:
                base = os.path.join(os.path.expanduser("~"), "Documents")
        else:
            base = os.path.join(os.path.expanduser("~"), "Desktop")
        fname = f"PLANILHADEFINANCAS_{user}.json"
        self.data_file = os.path.join(base, fname)
        self.ensure_file_exists()
        self.load_data()
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Blue"
        root = Builder.load_string(KV)
        
        # FECHA O MENU HAMBURGUER INICIALMENTE
        Clock.schedule_once(lambda dt: root.ids.nav_drawer.set_state("close"), 0.1)
        
        # Cria os menus dropdown
        Clock.schedule_once(lambda dt: self.create_dropdown_menus(), 0.2)
        
        Clock.schedule_once(lambda dt: self.refresh_ui(), 0.3)
        return root

    def on_touch_down(self, touch):
        # Se o menu está aberto e o clique foi fora dele, feche o menu
        if self.root.ids.nav_drawer.state == "open":
            if not self.root.ids.nav_drawer.collide_point(*touch.pos):
                self.toggle_nav_drawer()
                return True  # Consumir o evento
        
        return super(TarkadAndroidApp, self).on_touch_down(touch)

    def ensure_file_exists(self):
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            if not os.path.exists(self.data_file):
                with open(self.data_file, "w", encoding="utf-8") as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("Erro ensure file:", e)

    def load_data(self):
        try:
            if not os.path.exists(self.data_file):
                self.ensure_file_exists()
                self.df = pd.DataFrame(columns=COLUMNS)
                return
            with open(self.data_file, "r", encoding="utf-8") as f:
                raw = f.read()
            if not raw.strip():
                self.df = pd.DataFrame(columns=COLUMNS)
                return
            data = json.loads(raw)
            if not isinstance(data, list):
                data = []
            if not data:
                self.df = pd.DataFrame(columns=COLUMNS)
                return
            df = pd.DataFrame(data)
            # ensure columns - SEM "PAGO"
            for col in COLUMNS:
                if col not in df.columns:
                    df[col] = ""  # Apenas string vazia para todas as colunas
            
            # convert types
            try:
                df["DATA"] = pd.to_datetime(df["DATA"]).dt.date
            except:
                df["DATA"] = pd.to_datetime(df["DATA"], errors="coerce").fillna(pd.Timestamp(date.today())).dt.date
            df["VALOR"] = pd.to_numeric(df["VALOR"], errors="coerce").fillna(0.0)
            self.df = df.reset_index(drop=True)
        except Exception as e:
            print("Erro load_data:", e)
            self.df = pd.DataFrame(columns=COLUMNS)

    def save_data(self):
        try:
            df_to_save = self.df.copy()
            df_to_save["DATA"] = df_to_save["DATA"].astype(str)
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(df_to_save.to_dict("records"), f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("Erro save_data:", e)

    def refresh_ui(self):
        self.refresh_list()
        self.draw_charts()
        self.update_totals()

    def refresh_list(self):
        tree_list = self.root.ids.tree_list
        tree_list.clear_widgets()
        
        if self.df is None or self.df.empty:
            return
        
        # Aplica filtro de mês se necessário
        if self.mes_filtro != "GERAL":
            try:
                mes_num = int(self.mes_filtro)
                df_filtrado = self.df.copy()
                df_filtrado['MES'] = pd.to_datetime(df_filtrado['DATA']).dt.month
                df_filtrado = df_filtrado[df_filtrado['MES'] == mes_num]
                df_sorted = df_filtrado.sort_values("DATA", ascending=False)
            except:
                df_sorted = self.df.sort_values("DATA", ascending=False)
        else:
            df_sorted = self.df.sort_values("DATA", ascending=False)
        
        for idx, row in df_sorted.iterrows():
            item = TreeItem()
            item.real_idx = idx  # Índice REAL no DataFrame
            item.data = pd.to_datetime(row["DATA"]).strftime("%d/%m/%Y")
            item.valor = format_currency(row["VALOR"])
            item.tipo = str(row.get("TIPO", ""))
            item.meio = str(row.get("MEIO", ""))
            item.descricao = str(row.get("DESCRICAO", ""))
            
            # Define cor baseada no tipo
            if item.tipo == "RECEITA":
                item.cor_texto = [0, 0.6, 0, 1]  # Verde
            else:
                item.cor_texto = [0.8, 0, 0, 1]  # Vermelho
            
            tree_list.add_widget(item)

    def update_totals(self):
        if self.df is None or self.df.empty:
            total = 0.0; receitas = 0.0; despesas = 0.0; corretora = 0.0
        else:
            # Aplica o mesmo filtro de mês nos totais
            if self.mes_filtro != "GERAL":
                try:
                    mes_num = int(self.mes_filtro)
                    df_filtrado = self.df.copy()
                    df_filtrado['MES'] = pd.to_datetime(df_filtrado['DATA']).dt.month
                    df = df_filtrado[df_filtrado['MES'] == mes_num]
                except:
                    df = self.df.copy()
            else:
                df = self.df.copy()
                
            total = df["VALOR"].sum()
            receitas = df[df["VALOR"]>0]["VALOR"].sum()
            despesas = abs(df[df["VALOR"]<0]["VALOR"].sum())
            corretora = 0.0
            for _, r in df.iterrows():
                cat = str(r.get("CATEGORIA","")).upper()
                v = float(r.get("VALOR",0.0))
                if cat == "DIVIDENDOS" and v>0:
                    corretora += v
                elif cat == "SAQUE DE DIVIDENDOS" and v<0:
                    corretora += v
        
        # update labels
        try:
            self.root.ids.lbl_total.text = f"TOTAL: {format_currency(total)}"
            self.root.ids.lbl_receitas.text = f"RECEITAS: {format_currency(receitas)}"
            self.root.ids.lbl_despesas.text = f"DESPESAS: {format_currency(despesas)}"
            self.root.ids.lbl_corr.text = f"CORRETORA: {format_currency(corretora)}"
        except Exception:
            pass

    def add_entry(self):
        try:
            dt_str = self.root.ids.entry_date.text.strip()
            dt = datetime.strptime(dt_str, "%d/%m/%Y").date()
            
            # Obter valores dos campos
            tipo = self.root.ids.entry_tipo.text
            meio = self.root.ids.entry_meio.text
            categoria = self.root.ids.entry_categoria.text
            
            val_raw = self.root.ids.entry_valor.text.strip().replace("R$","").replace(".","").replace(",","." )
            val = float(val_raw)
            desc = (self.root.ids.entry_desc.text or "")
            
            if tipo == "DESPESA":
                val = -abs(val)
            else:
                val = abs(val)

            # VERIFICA SE É CARTÃO DE CRÉDITO PARA PARCELAMENTO
            if meio == "CARTAO DE CRÉDITO" and tipo == "DESPESA":
                self.ask_parcelas(dt, val, tipo, meio, categoria, desc)
                return

            # Se não for cartão de crédito, adiciona normalmente
            new = {"DATA": dt, "VALOR": val, "TIPO": tipo, "MEIO": meio, "DESCRICAO": desc, "CATEGORIA": categoria}
            # Corrige o warning do pandas
            new_df = pd.DataFrame([new])
            # Garante que todas as colunas existam
            for col in COLUMNS:
                if col not in new_df.columns:
                    new_df[col] = "" if col != "VALOR" else 0.0
                    
            self.df = pd.concat([self.df, new_df], ignore_index=True)
            self.save_data()
            self.refresh_ui()
            
            # clear inputs
            self.root.ids.entry_valor.text = ""
            self.root.ids.entry_desc.text = ""
            
        except Exception as e:
            self.show_message("Erro ao adicionar: " + str(e))

    def ask_parcelas(self, dt, val, tipo, meio, cat, desc):
        """Dialog para perguntar quantidade de parcelas"""
        content = MDBoxLayout(orientation="vertical", spacing=dp(8), adaptive_height=True)
        
        q_field = MDTextField(
            hint_text=f"Parcelas para {format_currency(abs(val))} (ex: 3)", 
            input_filter="int",
            size_hint_y=None,
            height=dp(56)
        )
        
        content.add_widget(q_field)
        
        dialog = MDDialog(
            title="Quantas parcelas?", 
            type="custom", 
            content_cls=content,
            buttons=[
                MDFlatButton(text="CANCELAR", on_release=lambda x: dialog.dismiss()),
                MDRaisedButton(text="CONFIRMAR", on_release=lambda x: self._confirm_parcelas(dialog, q_field, dt, abs(val), tipo, meio, cat, desc))
            ]
        )
        dialog.open()

    def _confirm_parcelas(self, dialog, q_field, dt, valor_total, tipo, meio, cat, desc):
        try:
            q = int(q_field.text.strip())
            if q <= 0:
                self.show_message("Número de parcelas deve ser maior que zero")
                return
                
            valor_parcela = valor_total / q
            
            rows = []
            for i in range(q):
                # Adiciona 1 mês para cada parcela
                data_parcela = self.add_months(dt, i)
                
                rows.append({
                    "DATA": data_parcela,
                    "VALOR": -abs(valor_parcela),
                    "TIPO": tipo,
                    "MEIO": meio,
                    "DESCRICAO": f"{desc} (Parc {i+1}/{q})",
                    "CATEGORIA": cat
                })
            
            # Corrige o warning do pandas
            new_df = pd.DataFrame(rows)
            # Garante que todas as colunas existam
            for col in COLUMNS:
                if col not in new_df.columns:
                    new_df[col] = "" if col != "VALOR" else 0.0
            
            self.df = pd.concat([self.df, new_df], ignore_index=True)
            self.save_data()
            self.refresh_ui()
            
            dialog.dismiss()
            
            # Limpa os campos
            self.root.ids.entry_valor.text = ""
            self.root.ids.entry_desc.text = ""
            
            self.show_message(f"{q} parcelas de {format_currency(valor_parcela)} adicionadas!")
            
        except ValueError:
            self.show_message("Digite um número válido de parcelas")
        except Exception as e:
            self.show_message("Erro ao criar parcelas: " + str(e))

    def add_months(self, sourcedate, months):
        """Adiciona meses a uma data"""
        month = sourcedate.month - 1 + months
        year = sourcedate.year + month // 12
        month = month % 12 + 1
        day = min(sourcedate.day, calendar.monthrange(year, month)[1])
        return date(year, month, day)

    def remove_selected(self):
        # Remove first selected (we'll consider tapped item flagged via last_tapped)
        # Simplicity: remove last item in the list (or prompt for index). We'll open a selection dialog.
        if self.df is None or self.df.empty:
            return
        # quick dialog to ask index to remove
        content = MDBoxLayout(orientation="vertical", spacing=dp(8), adaptive_height=True)
        idx_field = MDTextField(hint_text="Índice (0 = mais recente)", input_filter="int")
        content.add_widget(idx_field)
        dialog = MDDialog(title="Remover Registro", type="custom", content_cls=content,
                          buttons=[MDFlatButton(text="CANCELAR", on_release=lambda x: dialog.dismiss()),
                                   MDRaisedButton(text="REMOVER", on_release=lambda x: self._confirm_remove(dialog, idx_field))])
        dialog.open()

    def _confirm_remove(self, dialog, idx_field):
        try:
            idx = int(idx_field.text.strip())
            # we show sorted by date desc when removing: map to original index
            df_sorted = self.df.copy().sort_values("DATA", ascending=False).reset_index()
            if idx < 0 or idx >= len(df_sorted):
                self.show_message("Índice inválido")
                return
            real_idx = int(df_sorted.loc[idx, "index"])
            self.df = self.df.drop(index=real_idx).reset_index(drop=True)
            self.save_data()
            self.refresh_ui()
            dialog.dismiss()
        except Exception as e:
            self.show_message("Erro remover: " + str(e))

    def show_date_picker(self, instance=None):
        """Mostra o date picker para selecionar data"""
        try:
            # Tenta obter a data atual do campo
            current_text = self.root.ids.entry_date.text
            if current_text:
                try:
                    current_date = datetime.strptime(current_text, "%d/%m/%Y").date()
                except:
                    current_date = datetime.now().date()
            else:
                current_date = datetime.now().date()
            
            date_dialog = MDDatePicker(year=current_date.year, month=current_date.month, day=current_date.day)
            date_dialog.bind(on_save=self.on_date_selected)
            date_dialog.open()
        except Exception as e:
            self.show_message(f"Erro: {str(e)}")

    def on_date_selected(self, instance, value, date_range):
        self.default_date_str = value.strftime("%d/%m/%Y")
        self.root.ids.entry_date.text = self.default_date_str

    def show_message(self, text):
        d = MDDialog(title="Mensagem", text=text, buttons=[MDFlatButton(text="OK", on_release=lambda x: d.dismiss())])
        d.open()

    def confirmar_exclusao(self, idx):
        """Confirma a exclusão de um registro"""
        content = MDBoxLayout(orientation="vertical", spacing=dp(10), adaptive_height=True)
        
        label = Label(
            text="Tem certeza que deseja excluir este registro?\nEsta ação não pode ser desfeita.",
            size_hint_y=None,
            height=dp(80),
            text_size=(None, None),
            halign="center",
            valign="middle"
        )
        content.add_widget(label)
        
        dialog = MDDialog(
            title="Confirmar Exclusão",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="CANCELAR", on_release=lambda x: dialog.dismiss()),
                MDRaisedButton(text="EXCLUIR", 
                             on_release=lambda x: self.excluir_registro(idx, dialog),
                             theme_text_color="Custom",
                             text_color=(1, 1, 1, 1),
                             md_bg_color=(0.8, 0, 0, 1))  # Vermelho para danger
            ]
        )
        dialog.open()

    def excluir_registro(self, idx, dialog):
        """Exclui o registro do DataFrame e salvas no JSON"""
        try:
            # idx já é o índice real no DataFrame
            self.df = self.df.drop(index=idx).reset_index(drop=True)
            self.save_data()
            
            # ATUALIZA A INTERFACE COMPLETAMENTE
            self.refresh_ui()  # Isso já chama refresh_list() e update_totals()
            
            dialog.dismiss()
            self.show_message("Registro excluído com sucesso!")
        except Exception as e:
            self.show_message(f"Erro ao excluir: {str(e)}")

    def open_edit_menu(self, idx):
        # menu com opções: Editar / Excluir
        content = MDList()
        items = [
            ("Editar", lambda x, i=idx: self.open_edit_dialog(i)),
            ("Excluir", lambda x, i=idx: self.confirmar_exclusao(i)),
        ]
        
        for text, callback in items:
            li = OneLineListItem(text=text)
            li.bind(on_release=callback)
            content.add_widget(li)
            
        dlg = MDDialog(title="Ações", type="custom", content_cls=content, size_hint=(0.8, None))
        dlg.open()

    def open_edit_menu_dropdown(self, field, items, field_type):
        """Abre menu dropdown para campos de edição"""
        menu_items = []
        for item in items:
            menu_items.append({
                "text": item, 
                "viewclass": "OneLineListItem", 
                "on_release": lambda x, item=item: self.set_edit_field(item, field_type, field)
            })
        
        menu = MDDropdownMenu(
            caller=field,
            items=menu_items,
            width_mult=4,
            max_height=dp(200)
        )
        menu.open()

    def set_edit_field(self, value, field_type, field):
        """Define valor do campo de edição"""
        field.text = value
        
        # Atualiza sinal do valor se for tipo
        if field_type == "tipo" and hasattr(self, 'edit_dialog_fields'):
            try:
                # Encontra o campo de valor nos campos de edição
                v_field = self.edit_dialog_fields[1]  # v_field é o segundo campo
                current_val = v_field.text
                if current_val:
                    val = float(current_val.replace(",", "."))
                    if value == "DESPESA" and val > 0:
                        v_field.text = f"{-val}"
                    elif value == "RECEITA" and val < 0:
                        v_field.text = f"{abs(val)}"
            except:
                pass

    def show_edit_date_picker(self, field, instance=None):
        """Mostra date picker para campo de edição"""
        try:
            current_text = field.text
            if current_text:
                try:
                    current_date = datetime.strptime(current_text, "%d/%m/%Y").date()
                except:
                    current_date = datetime.now().date()
            else:
                current_date = datetime.now().date()
            
            date_dialog = MDDatePicker(
                year=current_date.year, 
                month=current_date.month, 
                day=current_date.day
            )
            date_dialog.bind(on_save=lambda inst, val, range: self.on_edit_date_selected(val, field))
            date_dialog.open()
        except Exception as e:
            self.show_message(f"Erro: {str(e)}")

    def on_edit_date_selected(self, value, field):
        """Callback para seleção de data na edição"""
        field.text = value.strftime("%d/%m/%Y")

    def open_edit_dialog(self, idx):
        try:
            real_idx = idx
            r = self.df.loc[real_idx]

            # Layout vertical com scroll
            scroll = ScrollView(size_hint=(1, 1))
            content = MDBoxLayout(orientation="vertical", spacing=dp(15), padding=dp(10),
                                  size_hint_y=None)
            content.bind(minimum_height=content.setter("height"))

            # ===== CAMPOS =====
            d_field = MDTextField(
                text=pd.to_datetime(r["DATA"]).strftime("%d/%m/%Y"),
                hint_text="DATA",
                readonly=True,
                size_hint_y=None,
                height=dp(56)
            )
            d_field.bind(on_focus=lambda x: self.show_edit_date_picker(d_field))

            v_field = MDTextField(
                text=str(abs(r["VALOR"])),
                hint_text="VALOR (apenas números)",
                input_filter="float",
                size_hint_y=None,
                height=dp(56)
            )

            t_field = MDTextField(
                text=str(r.get("TIPO", "")),
                hint_text="TIPO",
                readonly=True,
                size_hint_y=None,
                height=dp(56)
            )
            t_field.bind(on_focus=lambda x: self.open_edit_menu_dropdown(t_field, self.TIPOS, "tipo") if x.focus else None)

            m_field = MDTextField(
                text=str(r.get("MEIO", "")),
                hint_text="MEIO",
                readonly=True,
                size_hint_y=None,
                height=dp(56)
            )
            m_field.bind(on_focus=lambda x: self.open_edit_menu_dropdown(m_field, self.MEIOS, "meio") if x.focus else None)

            c_field = MDTextField(
                text=str(r.get("CATEGORIA", "")),
                hint_text="CATEGORIA",
                readonly=True,
                size_hint_y=None,
                height=dp(56)
            )
            c_field.bind(on_focus=lambda x: self.open_edit_menu_dropdown(c_field, self.CATEGORIAS, "categoria") if x.focus else None)

            desc_field = MDTextField(
                text=str(r.get("DESCRICAO", "")),
                hint_text="DESCRIÇÃO",
                size_hint_y=None,
                height=dp(56),
                multiline=True
            )

            # Adiciona os campos no content
            for f in [d_field, v_field, t_field, m_field, c_field, desc_field]:
                content.add_widget(f)

            # ===== BOTÕES NO FINAL =====
            btn_box = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(56), spacing=dp(10))
            btn_cancel = MDFlatButton(
                text="CANCELAR",
                on_release=lambda x: dialog.dismiss()
            )
            btn_save = MDRaisedButton(
                text="SALVAR",
                on_release=lambda x: self._save_edited(
                    dialog, real_idx, d_field, v_field, t_field, m_field, c_field, desc_field
                )
            )
            btn_box.add_widget(btn_cancel)
            btn_box.add_widget(btn_save)

            content.add_widget(btn_box)

            # Scroll recebe o conteúdo
            scroll.add_widget(content)

            # ===== CRIA O DIALOG =====
            dialog = MDDialog(
                title="Editar Lançamento",
                type="custom",
                content_cls=scroll,
                size_hint=(0.95, 0.95)
            )
            dialog.open()

            # Guarda os campos para referência
            self.edit_dialog_fields = (d_field, v_field, t_field, m_field, c_field, desc_field)

        except Exception as e:
            self.show_message(f"Erro ao abrir edição: {str(e)}")

    def _save_edited(self, dialog, real_idx, d_field, v_field, t_field, m_field, c_field, desc_field):
        try:
            new_date = datetime.strptime(d_field.text.strip(), "%d/%m/%Y").date()
            new_val = float(str(v_field.text).strip().replace(",",".").replace("R$",""))
            new_tipo = t_field.text.strip().upper()
            new_meio = m_field.text.strip().upper()
            new_cat = c_field.text.strip().upper()
            new_desc = desc_field.text.strip()
            
            if new_tipo == "DESPESA":
                new_val = -abs(new_val)
            else:
                new_val = abs(new_val)
                
            # SE FOR CARTÃO DE CRÉDITO E A DESCRIÇÃO CONTIVER "PARC", PERGUNTA SOBRE PARCELAS
            if (new_meio == "CARTAO DE CRÉDITO" and new_tipo == "DESPESA" and 
                "parc" in new_desc.lower()):
                self.ask_edit_parcelas(dialog, real_idx, new_date, abs(new_val), new_tipo, new_meio, new_cat, new_desc)
                return
                
            self.df.loc[real_idx, "DATA"] = new_date
            self.df.loc[real_idx, "VALOR"] = new_val
            self.df.loc[real_idx, "TIPO"] = new_tipo
            self.df.loc[real_idx, "MEIO"] = new_meio
            self.df.loc[real_idx, "CATEGORIA"] = new_cat
            self.df.loc[real_idx, "DESCRICAO"] = new_desc
            
            self.save_data()
            self.refresh_ui()
            dialog.dismiss()
            self.show_message("Registro atualizado com sucesso!")
        except Exception as e:
            self.show_message("Erro ao salvar: " + str(e))

    def draw_charts(self):
        pass

    def on_stop(self):
        # Fecha os menus quando o app fechar
        if self.menu_tipo:
            self.menu_tipo.dismiss()
        if self.menu_meio:
            self.menu_meio.dismiss()
        if self.menu_categoria:
            self.menu_categoria.dismiss()
        if self.menu_mes:
            self.menu_mes.dismiss()

if __name__ == "__main__":
    TarkadAndroidApp().run()
