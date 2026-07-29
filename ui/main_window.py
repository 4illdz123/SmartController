# ui/main_window.py
import os
import time
import threading
import flet as ft

from core.input_reader import InputReader
from core.virtual_controller import VirtualController
from core.script_engine import ScriptEngine
from utils.sounds import ensure_sounds, play

try:
    from ai.script_generator import generate_script_from_prompt
except ImportError:
    def generate_script_from_prompt(prompt: str) -> str:
        return f"# AI Script: {prompt}\ndef process(state):\n    return state"

TRANSLATIONS = {
    "ar": {
        "title": "DualSenseX Pro",
        "subtitle": "نظام إدارة سكربتات التحكم",
        "ai_banner": "AI Script Controller System",
        "start": "تشغيل النظام",
        "stop": "إيقاف النظام",
        "connected": "متصل",
        "disconnected": "غير متصل",
        "scripts_manager": "إدارة السكربتات",
        "create_combo": "إنشاء كومبو تفاعلي",
        "add_manual": "إضافة سكربت يدوياً",
        "add_ai": "إنشاء سكربت بالـ AI",
        "combo_title": "صانع الكومبو التفاعلي",
        "combo_name": "اسم الكومبو",
        "trigger_btn": "زر التفعيل",
        "trigger_mode": "طريقة التفعيل",
        "mode_hold": "ضغط مستمر (Hold)",
        "mode_press": "ضغطة واحدة (Press)",
        "add_step": "إضافة زر للتسلسل",
        "delay_ms": "التأخير (ملي ثانية)",
        "save_combo": "حفظ السكربت",
        "editor_title": "محرر السكربت اليدوي",
        "script_file_name": "اسم ملف السكربت",
        "ai_editor_title": "مولد السكربتات بالذكاء الاصطناعي",
        "ai_prompt_hint": "اكتب فكرة السكربت هنا...",
        "generate_ai": "توليد السكربت",
        "save": "حفظ",
        "lang_btn": "English"
    },
    "en": {
        "title": "DualSenseX Pro",
        "subtitle": "Controller Script System",
        "ai_banner": "AI Script Controller System",
        "start": "START SYSTEM",
        "stop": "STOP SYSTEM",
        "connected": "Connected",
        "disconnected": "Disconnected",
        "scripts_manager": "Scripts Manager",
        "create_combo": "Visual Combo Creator",
        "add_manual": "Add Script Manually",
        "add_ai": "Create AI Script",
        "combo_title": "Visual Combo Creator",
        "combo_name": "Combo Name",
        "trigger_btn": "Trigger Button",
        "trigger_mode": "Activation Mode",
        "mode_hold": "Hold",
        "mode_press": "Press Once",
        "add_step": "Add Sequence Button",
        "delay_ms": "Delay (ms)",
        "save_combo": "Save Combo Script",
        "editor_title": "Manual Script Editor",
        "script_file_name": "Script File Name",
        "ai_editor_title": "AI Script Generator",
        "ai_prompt_hint": "Type your script idea here...",
        "generate_ai": "Generate Script",
        "save": "Save",
        "lang_btn": "عربي"
    }
}

AVAILABLE_BUTTONS = ["cross", "circle", "square", "triangle", "l1", "r1", "l2", "r2", "l3", "r3", "dpad_up", "dpad_down", "dpad_left", "dpad_right"]

class App:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "DualSenseX Pro"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 0
        self.page.window.width = 860
        self.page.window.height = 660
        self.page.window.resizable = True
        self.page.bgcolor = "#0a0c10"

        ensure_sounds()

        self.lang = "ar"
        self.reader = InputReader()
        self.virtual = VirtualController()
        self.engine = ScriptEngine()

        self.running = False
        self.thread = None
        self.current_script_editing = None
        self._status_running = True
        self.drawer_open = False
        self.combo_sequence = []

        self.build_ui()
        threading.Thread(target=self._status_updater, daemon=True).start()
        self.page.run_thread(self._show_main_after_splash)

    def t(self, key):
        return TRANSLATIONS[self.lang].get(key, key)

    def toggle_language(self, e=None):
        play("click")
        self.lang = "en" if self.lang == "ar" else "ar"
        self.update_ui_texts()

    def update_ui_texts(self):
        self.txt_title.value = self.t("title")
        self.txt_subtitle.value = self.t("subtitle")
        self.txt_ai_banner.value = self.t("ai_banner")
        self.btn_lang.text = self.t("lang_btn")
        self.start_btn.text = self.t("stop") if self.running else self.t("start")
        self.txt_scripts_mgr.value = self.t("scripts_manager")
        
        self.btn_open_combo.text = self.t("create_combo")
        
        # تحديث نصوص القائمة المنسدلة بشكل صحيح
        self.item_manual_text.value = self.t("add_manual")
        self.item_ai_text.value = self.t("add_ai")
        
        self.editor_title_txt.value = self.t("editor_title")
        self.manual_filename_input.label = self.t("script_file_name")
        self.btn_save_editor.text = self.t("save")

        self.ai_title_txt.value = self.t("ai_editor_title")
        self.ai_filename_input.label = self.t("script_file_name")
        self.ai_prompt_input.hint_text = self.t("ai_prompt_hint")
        self.btn_generate_ai.text = self.t("generate_ai")
        
        self.txt_combo_title.value = self.t("combo_title")
        self.combo_name_input.label = self.t("combo_name")
        self.trigger_dropdown.label = self.t("trigger_btn")
        self.trigger_mode_dropdown.label = self.t("trigger_mode")
        self.trigger_mode_dropdown.options = [
            ft.dropdown.Option("hold", self.t("mode_hold")),
            ft.dropdown.Option("press", self.t("mode_press"))
        ]
        self.step_btn_dropdown.label = self.t("add_step")
        self.step_delay_input.label = self.t("delay_ms")
        self.btn_save_combo.text = self.t("save_combo")

        self.page.update()

    def build_ui(self):
        # Splash
        self.splash_view = ft.Container(
            visible=True, expand=True, bgcolor="#0a0c10", alignment=ft.Alignment.CENTER,
            content=ft.Column(
                [
                    ft.Text("DualSenseX Pro", size=36, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_400),
                    ft.Text("Created by 4ill", size=12, color=ft.Colors.GREY_500),
                    ft.Container(height=15),
                    ft.ProgressRing(color=ft.Colors.CYAN_400, width=24, height=24)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER
            )
        )

        # Main Controls
        self.status_text = ft.Text("Disconnected", size=13, color=ft.Colors.GREY_500)
        self.controller_name = ft.Text("", size=12, color=ft.Colors.GREY_600)
        self.txt_ai_banner = ft.Text(self.t("ai_banner"), size=14, color=ft.Colors.GREY_400, weight=ft.FontWeight.W_500)

        self.start_btn = ft.ElevatedButton(
            self.t("start"), icon=ft.Icons.PLAY_ARROW_ROUNDED,
            bgcolor=ft.Colors.CYAN_700, color=ft.Colors.WHITE,
            on_click=self.toggle_system, width=220, height=44,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))
        )

        # Drawer / Scripts
        self.scripts_column = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)

        self.btn_open_combo = ft.ElevatedButton(
            self.t("create_combo"), icon=ft.Icons.TUNE_ROUNDED,
            bgcolor=ft.Colors.CYAN_700, color=ft.Colors.WHITE,
            on_click=self.go_to_combo_creator, width=270
        )

        # تجهيز كائنات النص لتحديث اللغة لاحقاً
        self.item_manual_text = ft.Text(self.t("add_manual"))
        self.item_ai_text = ft.Text(self.t("add_ai"))

        # قائمة زر (+) المنسدلة بعد التعديل وتصحيح استخدام content
        self.item_add_manual = ft.PopupMenuItem(
            content=self.item_manual_text,
            icon=ft.Icons.CODE_ROUNDED,
            on_click=self.open_new_manual_script
        )
        self.item_add_ai = ft.PopupMenuItem(
            content=self.item_ai_text,
            icon=ft.Icons.AUTO_AWESOME_ROUNDED,
            on_click=self.go_to_ai_generator
        )

        self.plus_menu_button = ft.PopupMenuButton(
            icon=ft.Icons.ADD_ROUNDED,
            icon_color=ft.Colors.CYAN_400,
            tooltip="إضافة سكربت",
            items=[
                self.item_add_manual,
                self.item_add_ai,
            ]
        )

        self.txt_scripts_mgr = ft.Text(self.t("scripts_manager"), size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)

        self.scripts_drawer_panel = ft.Container(
            width=300, bgcolor="#111318", padding=15,
            border=ft.Border(left=ft.BorderSide(1, "#222")),
            offset=ft.Offset(1, 0), animate_offset=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
            content=ft.Column([
                ft.Row([
                    ft.Row([ft.Icon(ft.Icons.FOLDER_OPEN_ROUNDED, color=ft.Colors.CYAN_400, size=20), self.txt_scripts_mgr], spacing=8),
                    ft.Row([
                        self.plus_menu_button,
                        ft.IconButton(icon=ft.Icons.CLOSE_ROUNDED, icon_color=ft.Colors.GREY_400, on_click=self.toggle_drawer)
                    ], spacing=0)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(color="#222"),
                self.scripts_column,
                ft.Divider(color="#222"),
                ft.Column([
                    self.btn_open_combo
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            ], expand=True)
        )

        # Header
        self.txt_title = ft.Text(self.t("title"), size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_400)
        self.txt_subtitle = ft.Text(self.t("subtitle"), size=12, color=ft.Colors.GREY_500)
        self.btn_lang = ft.OutlinedButton(self.t("lang_btn"), on_click=self.toggle_language)

        header = ft.Row([
            ft.Row([self.txt_title, self.btn_lang], spacing=12),
            ft.IconButton(icon=ft.Icons.FOLDER_SPECIAL_ROUNDED, icon_color=ft.Colors.CYAN_400, icon_size=28, on_click=self.toggle_drawer)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        main_content = ft.Container(
            padding=20, expand=True,
            content=ft.Column([
                header,
                self.txt_subtitle,
                ft.Container(height=40),
                ft.Column([
                    self.txt_ai_banner,
                    ft.Container(height=10),
                    self.start_btn,
                    ft.Container(height=15),
                    ft.Row([self.status_text, self.controller_name], spacing=8, alignment=ft.MainAxisAlignment.CENTER)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, expand=True)
        )

        self.dashboard_view = ft.Container(
            visible=False, expand=True,
            content=ft.Stack([main_content, ft.Row([self.scripts_drawer_panel], alignment=ft.MainAxisAlignment.END, expand=True)], expand=True)
        )

        # ===== 1. MANUAL CODE EDITOR VIEW =====
        self.manual_filename_input = ft.TextField(label=self.t("script_file_name"), value="custom_script", bgcolor="#121212", width=200)
        self.code_editor = ft.TextField(multiline=True, expand=True, bgcolor="#121212", text_size=13, color="#A9B7C6")
        self.editor_title_txt = ft.Text(self.t("editor_title"), size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_300)
        self.btn_save_editor = ft.ElevatedButton(self.t("save"), icon=ft.Icons.SAVE_ROUNDED, bgcolor=ft.Colors.CYAN_700, color=ft.Colors.WHITE, on_click=self.save_script_from_editor)

        self.editor_view = ft.Container(
            visible=False, padding=20,
            content=ft.Column([
                ft.Row([
                    ft.Row([
                        ft.IconButton(icon=ft.Icons.ARROW_BACK_ROUNDED, icon_color=ft.Colors.WHITE, on_click=self.go_to_dashboard),
                        self.editor_title_txt
                    ]),
                    ft.Row([self.manual_filename_input, self.btn_save_editor], spacing=10)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                self.code_editor
            ], expand=True)
        )

        # ===== 2. AI GENERATOR VIEW =====
        self.ai_title_txt = ft.Text(self.t("ai_editor_title"), size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_300)
        self.ai_filename_input = ft.TextField(label=self.t("script_file_name"), value="ai_script", bgcolor="#121212", width=220)
        self.ai_prompt_input = ft.TextField(
            hint_text=self.t("ai_prompt_hint"), multiline=True, expand=True, bgcolor="#121212"
        )
        self.btn_generate_ai = ft.ElevatedButton(
            self.t("generate_ai"), icon=ft.Icons.AUTO_AWESOME_ROUNDED,
            bgcolor=ft.Colors.CYAN_700, color=ft.Colors.WHITE,
            on_click=self.handle_ai_script_generation
        )
        self.ai_gen_view = ft.Container(
            visible=False, padding=20,
            content=ft.Column([
                ft.Row([
                    ft.IconButton(icon=ft.Icons.ARROW_BACK_ROUNDED, icon_color=ft.Colors.WHITE, on_click=self.go_to_dashboard),
                    self.ai_title_txt
                ]),
                self.ai_filename_input,
                self.ai_prompt_input,
                ft.Row([self.btn_generate_ai], alignment=ft.MainAxisAlignment.END)
            ], spacing=12, expand=True)
        )

        # ===== 3. VISUAL COMBO CREATOR VIEW =====
        self.txt_combo_title = ft.Text(self.t("combo_title"), size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_400)
        self.combo_name_input = ft.TextField(label=self.t("combo_name"), value="my_combo", bgcolor="#121212")
        
        self.trigger_dropdown = ft.Dropdown(
            label=self.t("trigger_btn"), value="r2",
            options=[ft.dropdown.Option(b) for b in AVAILABLE_BUTTONS], bgcolor="#121212"
        )
        self.trigger_mode_dropdown = ft.Dropdown(
            label=self.t("trigger_mode"), value="hold",
            options=[ft.dropdown.Option("hold", self.t("mode_hold")), ft.dropdown.Option("press", self.t("mode_press"))],
            bgcolor="#121212"
        )
        self.step_btn_dropdown = ft.Dropdown(
            label=self.t("add_step"), value="cross",
            options=[ft.dropdown.Option(b) for b in AVAILABLE_BUTTONS], bgcolor="#121212", expand=True
        )
        self.step_delay_input = ft.TextField(label=self.t("delay_ms"), value="50", width=120, bgcolor="#121212")
        self.sequence_list_ui = ft.Column(spacing=6, scroll=ft.ScrollMode.AUTO, height=180)

        self.btn_save_combo = ft.ElevatedButton(
            self.t("save_combo"), icon=ft.Icons.SAVE_ROUNDED,
            bgcolor=ft.Colors.CYAN_700, color=ft.Colors.WHITE,
            on_click=self.generate_and_save_combo
        )

        self.combo_view = ft.Container(
            visible=False, padding=20,
            content=ft.Column([
                ft.Row([
                    ft.IconButton(icon=ft.Icons.ARROW_BACK_ROUNDED, icon_color=ft.Colors.WHITE, on_click=self.go_to_dashboard),
                    self.txt_combo_title
                ]),
                ft.Row([self.combo_name_input, self.trigger_dropdown, self.trigger_mode_dropdown], spacing=10),
                ft.Divider(color="#222"),
                ft.Row([
                    self.step_btn_dropdown,
                    self.step_delay_input,
                    ft.ElevatedButton("+", on_click=self.add_step_to_sequence, bgcolor=ft.Colors.CYAN_600, color=ft.Colors.WHITE)
                ], spacing=10),
                ft.Container(content=self.sequence_list_ui, bgcolor="#14171f", padding=10, border_radius=8, expand=True),
                ft.Row([self.btn_save_combo], alignment=ft.MainAxisAlignment.END)
            ], expand=True)
        )

        self.page.add(ft.Stack([
            self.splash_view,
            self.dashboard_view,
            self.editor_view,
            self.ai_gen_view,
            self.combo_view
        ], expand=True))
        self.refresh_scripts_ui()

    def _show_main_after_splash(self):
        time.sleep(1.2)
        self.splash_view.visible = False
        self.dashboard_view.visible = True
        play("start")
        self.page.update()

    def toggle_drawer(self, e=None):
        play("click")
        self.drawer_open = not self.drawer_open
        self.scripts_drawer_panel.offset = ft.Offset(0 if self.drawer_open else 1, 0)
        self.page.update()

    def go_to_dashboard(self, e=None):
        play("click")
        self.combo_view.visible = False
        self.editor_view.visible = False
        self.ai_gen_view.visible = False
        self.dashboard_view.visible = True
        self.page.update()

    def go_to_combo_creator(self, e=None):
        play("click")
        self.combo_sequence.clear()
        self._refresh_sequence_ui()
        self.dashboard_view.visible = False
        self.combo_view.visible = True
        self.page.update()

    def open_new_manual_script(self, e=None):
        play("click")
        self.current_script_editing = None
        self.manual_filename_input.value = "custom_script"
        self.code_editor.value = '''# Manual Script Template
def process(state: dict) -> dict:
    return state
'''
        self.dashboard_view.visible = False
        self.editor_view.visible = True
        self.page.update()

    def go_to_ai_generator(self, e=None):
        play("click")
        self.ai_filename_input.value = "ai_script"
        self.ai_prompt_input.value = ""
        self.dashboard_view.visible = False
        self.ai_gen_view.visible = True
        self.page.update()

    def handle_ai_script_generation(self, e=None):
        play("click")
        name = (self.ai_filename_input.value or "ai_script").strip().replace(".py", "")
        prompt = self.ai_prompt_input.value or ""

        generated_code = generate_script_from_prompt(prompt)

        os.makedirs("scripts", exist_ok=True)
        with open(os.path.join("scripts", f"{name}.py"), "w", encoding="utf-8") as f:
            f.write(generated_code)

        play("toggle")
        self.refresh_scripts_ui()
        self.go_to_dashboard()

    def add_step_to_sequence(self, e):
        btn = self.step_btn_dropdown.value
        try:
            delay = int(self.step_delay_input.value)
        except ValueError:
            delay = 50
        self.combo_sequence.append((btn, delay))
        play("click")
        self._refresh_sequence_ui()

    def remove_step_from_sequence(self, idx):
        if 0 <= idx < len(self.combo_sequence):
            self.combo_sequence.pop(idx)
            play("click")
            self._refresh_sequence_ui()

    def _refresh_sequence_ui(self):
        self.sequence_list_ui.controls.clear()
        for idx, (btn, delay) in enumerate(self.combo_sequence):
            row = ft.Container(
                padding=8, bgcolor="#1d222e", border_radius=6,
                content=ft.Row([
                    ft.Text(f"{idx+1}. Button: {btn.upper()} (Hold: {delay}ms)", color=ft.Colors.WHITE, expand=True),
                    ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color=ft.Colors.RED_400, on_click=lambda e, i=idx: self.remove_step_from_sequence(i))
                ])
            )
            self.sequence_list_ui.controls.append(row)
        self.page.update()

    def generate_and_save_combo(self, e):
        name = (self.combo_name_input.value or "combo").strip().replace(".py", "")
        trigger = self.trigger_dropdown.value

        code = f'''# Combo Script: {name}
import time

def process(state: dict) -> dict:
    buttons = state.get("buttons", {{}})
    is_triggered = False

    if "{trigger}" in ["l2", "r2"]:
        is_triggered = state.get("{trigger}", 0) > 0.5
    else:
        is_triggered = buttons.get("{trigger}", False)

    if is_triggered:
        sequence = {self.combo_sequence}
        for btn, delay in sequence:
            if btn in ["l2", "r2"]:
                state[btn] = 1.0
            else:
                buttons[btn] = True
            time.sleep(delay / 1000.0)
            if btn in ["l2", "r2"]:
                state[btn] = 0.0
            else:
                buttons[btn] = False

    return state
'''
        os.makedirs("scripts", exist_ok=True)
        with open(os.path.join("scripts", f"{name}.py"), "w", encoding="utf-8") as f:
            f.write(code)

        play("toggle")
        self.refresh_scripts_ui()
        self.go_to_dashboard()

    def open_editor_page(self, script_name):
        play("click")
        self.current_script_editing = script_name
        self.manual_filename_input.value = script_name
        path = os.path.join("scripts", f"{script_name}.py")
        code = open(path, encoding="utf-8").read() if os.path.exists(path) else ""
        self.code_editor.value = code
        self.dashboard_view.visible = False
        self.editor_view.visible = True
        self.page.update()

    def save_script_from_editor(self, e):
        name = (self.manual_filename_input.value or "custom_script").strip().replace(".py", "")
        path = os.path.join("scripts", f"{name}.py")
        os.makedirs("scripts", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.code_editor.value or "")
        play("toggle")
        self.refresh_scripts_ui()
        self.go_to_dashboard()

    def delete_script(self, script_name):
        self.engine.disable(script_name)
        self.engine.loaded_scripts.pop(script_name, None)
        path = os.path.join("scripts", f"{script_name}.py")
        if os.path.exists(path):
            os.remove(path)
        play("click")
        self.refresh_scripts_ui()

    def refresh_scripts_ui(self):
        self.scripts_column.controls.clear()
        if os.path.exists("scripts"):
            for f in os.listdir("scripts"):
                if f.endswith(".py") and not f.startswith("__"):
                    name = f[:-3]
                    if name not in self.engine.loaded_scripts and hasattr(self.engine, 'load_script'):
                        self.engine.load_script(name)

        for name in list(self.engine.loaded_scripts.keys()):
            enabled = name in self.engine.enabled_scripts
            row = ft.Container(
                padding=8, bgcolor="#1d222e", border_radius=8,
                content=ft.Row([
                    ft.Icon(ft.Icons.CODE_ROUNDED, color=ft.Colors.CYAN_400, size=16),
                    ft.Text(f"{name}.py", expand=True, size=12, color=ft.Colors.WHITE),
                    ft.IconButton(icon=ft.Icons.EDIT_ROUNDED, icon_color=ft.Colors.CYAN_400, icon_size=16, on_click=lambda e, n=name: self.open_editor_page(n)),
                    ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color=ft.Colors.RED_400, icon_size=16, on_click=lambda e, n=name: self.delete_script(n)),
                    ft.Switch(value=enabled, active_color=ft.Colors.CYAN_400, on_change=lambda e, n=name: self.toggle_script(n, e.control.value))
                ])
            )
            self.scripts_column.controls.append(row)
        self.page.update()

    def toggle_script(self, name, value):
        play("toggle")
        if value:
            self.engine.enable(name)
        else:
            self.engine.disable(name)

    def _status_updater(self):
        while self._status_running:
            try:
                if self.reader.is_connected():
                    self.status_text.value = self.t("connected")
                    self.status_text.color = ft.Colors.GREEN_400
                    self.controller_name.value = self.reader.controller_name or ""
                else:
                    self.status_text.value = self.t("disconnected")
                    self.status_text.color = ft.Colors.GREY_500
                    self.controller_name.value = ""
                self.page.update()
            except Exception:
                pass
            time.sleep(1.2)

    def toggle_system(self, e):
        if not self.running:
            if not self.reader.is_connected():
                return
            play("start")
            self.running = True
            self.start_btn.text = self.t("stop")
            self.start_btn.bgcolor = ft.Colors.RED_700
            self.thread = threading.Thread(target=self.run_loop, daemon=True)
            self.thread.start()
        else:
            play("click")
            self.running = False
            self.start_btn.text = self.t("start")
            self.start_btn.bgcolor = ft.Colors.CYAN_700
            self.virtual.reset()
        self.page.update()

    def run_loop(self):
        while self.running:
            try:
                raw_state = self.reader.get_state()
                processed_state = self.engine.process(raw_state)
                self.virtual.update(processed_state)
                time.sleep(0.01)
            except Exception:
                time.sleep(0.1)

def main(page: ft.Page):
    App(page)

if __name__ == "__main__":
    ft.app(target=main)