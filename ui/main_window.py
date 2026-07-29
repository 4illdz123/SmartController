# ui/main_window.py

import os
import threading
import time
import flet as ft

from core.input_reader import InputReader
from core.virtual_controller import VirtualController
from core.script_engine import ScriptEngine
from ai.script_generator import AIScriptGenerator
from utils.sounds import ensure_sounds, play
from core.particles_engine import PygameEngine


class App:

    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "DualSenseX Pro - Beta"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 0
        self.page.window.width = 980
        self.page.window.height = 760
        self.page.window.resizable = True
        self.page.bgcolor = "#0a0a0a"

        ensure_sounds()

        # Core logic setup
        self.reader = InputReader()
        self.virtual = VirtualController()
        self.engine = ScriptEngine()

        try:
            self.ai_generator = AIScriptGenerator()
        except Exception:
            self.ai_generator = None

        self.running = False
        self.thread = None
        self.current_script_editing = None
        self._status_running = True
        self.button_indicators = {}
        self.drawer_open = False

        # Setup Pygame Particles Engine
        self.particles_engine = PygameEngine(
            self.page.window.width, self.page.window.height
        )

        # Image background container for particles
        self.bg_image = ft.Image(
            src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=",
            fit="cover",
            expand=True,
        )

        self.page.on_resized = self._on_page_resize

        self.build_ui()

        # Background threads
        threading.Thread(target=self._status_updater, daemon=True).start()
        threading.Thread(target=self._pygame_loop, daemon=True).start()

        self.page.run_thread(self._show_main_after_splash)

    def _on_mouse_hover(self, e):
        """إضافة جسيمات عند حركة الماوس"""
        pos_x = getattr(e, "x", getattr(e, "local_x", 0))
        pos_y = getattr(e, "y", getattr(e, "local_y", 0))
        if self.particles_engine and (pos_x or pos_y):
            self.particles_engine.add_particles(pos_x, pos_y)

    def _on_page_resize(self, e):
        if self.particles_engine:
            self.particles_engine.resize(self.page.width, self.page.height)

    def _pygame_loop(self):
        while self._status_running:
            try:
                if self.particles_engine:
                    frame_bytes = self.particles_engine.render_frame_bytes()
                    b64_str = ft.base64.b64encode(frame_bytes).decode("utf-8")
                    self.bg_image.src_base64 = b64_str
                    self.page.update()
            except Exception:
                pass
            time.sleep(1 / 30)

    def _btn(self, key, label, width=52, height=32):
        c = ft.Container(
            content=ft.Text(
                label,
                size=11,
                color=ft.Colors.WHITE,
                text_align=ft.TextAlign.CENTER,
            ),
            width=width,
            height=height,
            bgcolor="#1f1f1f",
            border_radius=8,
            alignment=ft.Alignment.CENTER,
            animate=ft.Animation(100, ft.AnimationCurve.EASE_OUT),
            border=ft.Border(
                left=ft.BorderSide(1, "#333"),
                right=ft.BorderSide(1, "#333"),
                top=ft.BorderSide(1, "#333"),
                bottom=ft.BorderSide(1, "#333"),
            ),
        )
        self.button_indicators[key] = c
        return c

    def build_ui(self):
        # ===== SPLASH VIEW =====
        self.splash_view = ft.Container(
            visible=True,
            expand=True,
            bgcolor="#0a0a0a",
            alignment=ft.Alignment.CENTER,
            content=ft.Column(
                [
                    ft.Text(
                        "DualSenseX Pro",
                        size=44,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.CYAN_400,
                    ),
                    ft.Text("Created by 4ill", size=14, color=ft.Colors.GREY_500),
                    ft.Container(height=30),
                    ft.ProgressRing(
                        color=ft.Colors.CYAN_400, width=30, height=30
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        )

        # ===== CONTROLLER PREVIEW =====
        face = ft.Row(
            [
                self._btn("square", "□"),
                self._btn("triangle", "△"),
                self._btn("circle", "○"),
                self._btn("cross", "✕"),
            ],
            spacing=8,
            alignment=ft.MainAxisAlignment.CENTER,
        )
        shoulders = ft.Row(
            [self._btn("l1", "L1", 64), self._btn("r1", "R1", 64)],
            spacing=50,
            alignment=ft.MainAxisAlignment.CENTER,
        )
        triggers = ft.Row(
            [self._btn("l2", "L2", 64), self._btn("r2", "R2", 64)],
            spacing=50,
            alignment=ft.MainAxisAlignment.CENTER,
        )
        meta = ft.Row(
            [self._btn("share", "Share", 68), self._btn("options", "Opt", 68)],
            spacing=25,
            alignment=ft.MainAxisAlignment.CENTER,
        )
        sticks = ft.Row(
            [self._btn("l3", "L3", 56, 56), self._btn("r3", "R3", 56, 56)],
            spacing=60,
            alignment=ft.MainAxisAlignment.CENTER,
        )
        dpad = ft.Column(
            [
                self._btn("dpad_up", "↑", 44, 30),
                ft.Row(
                    [
                        self._btn("dpad_left", "←", 44, 30),
                        self._btn("dpad_right", "→", 44, 30),
                    ],
                    spacing=6,
                ),
                self._btn("dpad_down", "↓", 44, 30),
            ],
            spacing=4,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

        self.status_text = ft.Text(
            "Disconnected", size=14, color=ft.Colors.RED_400
        )
        self.controller_name = ft.Text("", size=12, color=ft.Colors.GREY_500)

        self.start_btn = ft.ElevatedButton(
            "START SYSTEM",
            icon=ft.Icons.PLAY_ARROW_ROUNDED,
            bgcolor=ft.Colors.CYAN_700,
            color=ft.Colors.WHITE,
            on_click=self.toggle_system,
            width=260,
            height=50,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=12)),
        )

        controller_card = ft.Container(
            padding=20,
            bgcolor="#121212",
            border_radius=16,
            width=480,
            content=ft.Column(
                [
                    ft.Text(
                        "Controller Live Preview",
                        size=15,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.CYAN_300,
                    ),
                    ft.Row(
                        [self.status_text, self.controller_name],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    ft.Container(height=10),
                    shoulders,
                    triggers,
                    ft.Container(height=10),
                    face,
                    ft.Container(height=10),
                    meta,
                    ft.Container(height=10),
                    sticks,
                    ft.Container(height=10),
                    dpad,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
            ),
        )

        # ===== SCRIPTS DRAWER =====
        self.scripts_column = ft.Column(
            spacing=10, scroll=ft.ScrollMode.AUTO, expand=True
        )

        self.add_script_btn = ft.FloatingActionButton(
            icon=ft.Icons.ADD_ROUNDED,
            bgcolor=ft.Colors.CYAN_600,
            foreground_color=ft.Colors.WHITE,
            mini=True,
            on_click=self.go_to_creation_page,
        )

        self.scripts_drawer_panel = ft.Container(
            width=320,
            bgcolor="#141414",
            padding=15,
            border=ft.Border(left=ft.BorderSide(1, "#222")),
            offset=ft.Offset(1, 0),
            animate_offset=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Row(
                                [
                                    ft.Icon(
                                        ft.Icons.FOLDER_OPEN_ROUNDED,
                                        color=ft.Colors.CYAN_400,
                                        size=22,
                                    ),
                                    ft.Text(
                                        "Scripts Manager",
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.WHITE,
                                    ),
                                ],
                                spacing=8,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.CLOSE_ROUNDED,
                                icon_color=ft.Colors.GREY_400,
                                on_click=self.toggle_drawer,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Divider(color="#252525"),
                    self.scripts_column,
                    ft.Container(height=10),
                    ft.Row(
                        [self.add_script_btn],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                ],
                expand=True,
            ),
        )

        header = ft.Row(
            [
                ft.Row(
                    [
                        ft.Text(
                            "DualSenseX Pro",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.CYAN_400,
                        ),
                        ft.Container(
                            content=ft.Text(
                                "BETA",
                                size=10,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.CYAN_200,
                            ),
                            bgcolor="#0e3a3a",
                            padding=ft.Padding.symmetric(
                                vertical=4, horizontal=8
                            ),
                            border_radius=12,
                        ),
                    ],
                    spacing=10,
                ),
                ft.IconButton(
                    icon=ft.Icons.FOLDER_SPECIAL_ROUNDED,
                    icon_color=ft.Colors.CYAN_400,
                    icon_size=28,
                    on_click=self.toggle_drawer,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        # ===== MAIN DASHBOARD =====
        main_content = ft.Container(
            padding=20,
            expand=True,
            on_hover=self._on_mouse_hover,  # التقاط حركة الماوس للجسيمات
            content=ft.Column(
                [
                    header,
                    ft.Text(
                        "AI Script Controller System - Created by 4ill",
                        size=12,
                        color=ft.Colors.GREY_500,
                    ),
                    ft.Container(height=20),
                    ft.Column(
                        [
                            self.start_btn,
                            ft.Container(height=15),
                            controller_card,
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        expand=True,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True,
            ),
        )

        drawer_wrapper = ft.Row(
            controls=[self.scripts_drawer_panel],
            alignment=ft.MainAxisAlignment.END,
            expand=True,
        )

        self.dashboard_view = ft.Container(
            visible=False,
            expand=True,
            content=ft.Stack(
                [
                    main_content,
                    drawer_wrapper,
                ],
                expand=True,
            ),
        )

        # ===== CREATION VIEW =====
        self.manual_name_input = ft.TextField(
            label="Script Name", bgcolor="#121212", border_color="#2A2A2A"
        )
        self.ai_name_input = ft.TextField(
            label="AI Script Name",
            value="dev_ai_script",
            bgcolor="#121212",
            border_color="#2A2A2A",
        )
        self.ai_prompt_input = ft.TextField(
            label="Script Description",
            multiline=True,
            min_lines=3,
            bgcolor="#121212",
            border_color="#2A2A2A",
        )

        self.creation_view = ft.Container(
            visible=False,
            padding=25,
            on_hover=self._on_mouse_hover,
            content=ft.Column([
                ft.Row([
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK_ROUNDED,
                        icon_color=ft.Colors.WHITE,
                        on_click=self.go_to_dashboard,
                    ),
                    ft.Text(
                        "Add New Script",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.CYAN_400,
                    ),
                ]),
                ft.Row(
                    [
                        ft.Container(
                            padding=16,
                            bgcolor="#121212",
                            border_radius=12,
                            expand=True,
                            content=ft.Column([
                                ft.Text(
                                    "Manual Creation",
                                    weight=ft.FontWeight.BOLD,
                                ),
                                self.manual_name_input,
                                ft.ElevatedButton(
                                    "Create",
                                    on_click=self.create_manual_script,
                                    bgcolor=ft.Colors.CYAN_800,
                                    color=ft.Colors.WHITE,
                                ),
                            ]),
                        ),
                        ft.Container(
                            padding=16,
                            bgcolor="#121212",
                            border_radius=12,
                            expand=True,
                            content=ft.Column([
                                ft.Text(
                                    "Generate with AI Engine",
                                    weight=ft.FontWeight.BOLD,
                                ),
                                self.ai_name_input,
                                self.ai_prompt_input,
                                ft.ElevatedButton(
                                    "Generate",
                                    on_click=self.create_ai_script,
                                    bgcolor=ft.Colors.CYAN_700,
                                    color=ft.Colors.WHITE,
                                ),
                            ]),
                        ),
                    ],
                    spacing=12,
                ),
            ]),
        )

        # ===== EDITOR VIEW =====
        self.editor_file_title = ft.Text(
            "script.py",
            size=16,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.CYAN_300,
        )
        self.code_editor = ft.TextField(
            multiline=True,
            expand=True,
            text_size=14,
            bgcolor="#121212",
            color="#A9B7C6",
            border_color="#2A2A2A",
            content_padding=12,
        )
        self.editor_view = ft.Container(
            visible=False,
            padding=15,
            on_hover=self._on_mouse_hover,
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Row([
                                ft.IconButton(
                                    icon=ft.Icons.ARROW_BACK_ROUNDED,
                                    icon_color=ft.Colors.WHITE,
                                    on_click=self.go_to_dashboard,
                                ),
                                self.editor_file_title,
                            ]),
                            ft.ElevatedButton(
                                "Save Script",
                                icon=ft.Icons.SAVE_ROUNDED,
                                bgcolor=ft.Colors.CYAN_700,
                                color=ft.Colors.WHITE,
                                on_click=self.save_script_from_editor,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    self.code_editor,
                ],
                expand=True,
            ),
        )

        # ROOT STACK
        self.page.add(
            ft.Stack(
                [
                    self.bg_image,
                    self.splash_view,
                    self.dashboard_view,
                    self.creation_view,
                    self.editor_view,
                ],
                expand=True,
            )
        )

        self.refresh_scripts_ui()
        self.update_connection_status()

    def _show_main_after_splash(self):
        time.sleep(1.8)
        self.splash_view.visible = False
        self.dashboard_view.visible = True
        play("start")
        self.page.update()

    def toggle_drawer(self, e=None):
        play("click")
        self.drawer_open = not self.drawer_open
        self.scripts_drawer_panel.offset = ft.Offset(
            0 if self.drawer_open else 1, 0
        )
        self.page.update()

    def _update_button_lights(self, state: dict):
        buttons = state.get("buttons", {})
        for key, control in self.button_indicators.items():
            if key in ("l2", "r2"):
                active = state.get(key, 0) > 0.2
            else:
                active = bool(buttons.get(key, False))

            control.bgcolor = "#00bcd4" if active else "#1f1f1f"
        try:
            self.page.update()
        except Exception:
            pass

    def go_to_dashboard(self, e=None):
        play("click")
        self.creation_view.visible = False
        self.editor_view.visible = False
        self.dashboard_view.visible = True
        self.page.update()

    def go_to_creation_page(self, e=None):
        play("click")
        self.dashboard_view.visible = False
        self.editor_view.visible = False
        self.creation_view.visible = True
        self.page.update()

    def open_editor_page(self, script_name):
        play("click")
        self.current_script_editing = script_name
        path = os.path.join("scripts", f"{script_name}.py")
        code = (
            open(path, encoding="utf-8").read() if os.path.exists(path) else ""
        )
        self.editor_file_title.value = f"scripts/{script_name}.py"
        self.code_editor.value = code
        self.dashboard_view.visible = False
        self.creation_view.visible = False
        self.editor_view.visible = True
        self.page.update()

    def create_manual_script(self, e):
        name = (self.manual_name_input.value or "").strip().replace(".py", "")
        if not name:
            return
        os.makedirs("scripts", exist_ok=True)
        path = os.path.join("scripts", f"{name}.py")
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write("def process(state: dict) -> dict:\n    return state\n")
        play("toggle")
        self.refresh_scripts_ui()
        self.open_editor_page(name)

    def create_ai_script(self, e):
        if not self.ai_generator:
            return
        name = (
            (self.ai_name_input.value or "dev_ai_script")
            .strip()
            .replace(".py", "")
        )
        prompt = (self.ai_prompt_input.value or "").strip()
        if not prompt:
            return
        code = self.ai_generator.generate_script(prompt)
        os.makedirs("scripts", exist_ok=True)
        with open(
            os.path.join("scripts", f"{name}.py"), "w", encoding="utf-8"
        ) as f:
            f.write(code)
        play("toggle")
        self.refresh_scripts_ui()
        self.open_editor_page(name)

    def delete_script(self, script_name):
        self.engine.disable(script_name)
        self.engine.loaded_scripts.pop(script_name, None)
        path = os.path.join("scripts", f"{script_name}.py")
        if os.path.exists(path):
            os.remove(path)
        play("click")
        self.refresh_scripts_ui()

    def save_script_from_editor(self, e):
        if not self.current_script_editing:
            return
        path = os.path.join("scripts", f"{self.current_script_editing}.py")
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.code_editor.value or "")
        if hasattr(self.engine, "reload_script"):
            self.engine.reload_script(self.current_script_editing)
        play("toggle")
        self.refresh_scripts_ui()

    def refresh_scripts_ui(self):
        self.scripts_column.controls.clear()
        if os.path.exists("scripts"):
            for f in os.listdir("scripts"):
                if f.endswith(".py") and not f.startswith("__"):
                    name = f[:-3]
                    if (
                        name not in self.engine.loaded_scripts
                        and hasattr(self.engine, "load_script")
                    ):
                        self.engine.load_script(name)

        for name in list(self.engine.loaded_scripts.keys()):
            enabled = name in self.engine.enabled_scripts
            row = ft.Container(
                padding=10,
                bgcolor="#1d1d1d",
                border_radius=10,
                content=ft.Row([
                    ft.Icon(
                        ft.Icons.CODE_ROUNDED, color=ft.Colors.CYAN_400, size=18
                    ),
                    ft.Text(
                        f"{name}.py", expand=True, size=12, color=ft.Colors.WHITE
                    ),
                    ft.IconButton(
                        icon=ft.Icons.EDIT_ROUNDED,
                        icon_color=ft.Colors.CYAN_400,
                        icon_size=18,
                        on_click=lambda e, n=name: self.open_editor_page(n),
                    ),
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_color=ft.Colors.RED_400,
                        icon_size=18,
                        on_click=lambda e, n=name: self.delete_script(n),
                    ),
                    ft.Switch(
                        value=enabled,
                        active_color=ft.Colors.CYAN_400,
                        on_change=lambda e, n=name: self.toggle_script(
                            n, e.control.value
                        ),
                    ),
                ]),
            )
            self.scripts_column.controls.append(row)
        self.page.update()

    def toggle_script(self, name, value):
        play("toggle")
        if value:
            self.engine.enable(name)
        else:
            self.engine.disable(name)

    def update_connection_status(self):
        try:
            if self.reader.is_connected():
                self.status_text.value = "Connected"
                self.status_text.color = ft.Colors.GREEN_400
                self.controller_name.value = self.reader.controller_name or ""
            else:
                self.status_text.value = "Disconnected"
                self.status_text.color = ft.Colors.RED_400
                self.controller_name.value = ""
            self.page.update()
        except Exception:
            pass

    def _status_updater(self):
        while self._status_running:
            self.update_connection_status()
            time.sleep(1.2)

    def toggle_system(self, e):
        if not self.running:
            self.start_system()
        else:
            self.stop_system()

    def start_system(self):
        if not self.reader.is_connected():
            self.status_text.value = "Connect Controller First"
            self.status_text.color = ft.Colors.ORANGE_400
            self.page.update()
            return
        play("start")
        self.running = True
        self.start_btn.text = "STOP SYSTEM"
        self.start_btn.bgcolor = ft.Colors.RED_700
        self.page.update()
        self.thread = threading.Thread(target=self.run_loop, daemon=True)
        self.thread.start()

    def stop_system(self):
        play("click")
        self.running = False
        self.start_btn.text = "START SYSTEM"
        self.start_btn.bgcolor = ft.Colors.CYAN_700
        self.virtual.reset()
        self.page.update()

    def run_loop(self):
        while self.running:
            try:
                state = self.reader.get_state()
                state = self.engine.process(state)
                self.virtual.update(state)

                self._update_button_lights(state)

                time.sleep(0.01)
            except Exception as e:
                print("Loop Error:", e)
                time.sleep(0.1)


def main(page: ft.Page):
    App(page)


if __name__ == "__main__":
    ft.app(target=main)