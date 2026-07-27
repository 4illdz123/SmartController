import flet as ft
from core.input_reader import InputReader
from core.virtual_controller import VirtualController
from core.script_engine import ScriptEngine
import threading
import time
import os

class App:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "SmartController - IDE"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 0
        self.page.window.width = 960
        self.page.window.height = 680
        self.page.window.resizable = False
        self.page.bgcolor = "#0f0f0f"

        self.reader = InputReader()
        self.virtual = VirtualController()
        self.engine = ScriptEngine()

        self.running = False
        self.thread = None
        self.current_script_editing = None

        self.build_ui()

    def build_ui(self):
        # --- 1. عناصر الشاشة الرئيسية (Dashboard) ---
        self.title = ft.Text("DualSenseX Pro", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_400)
        self.subtitle = ft.Text("DualShock 4 / DualSense → Xbox Virtual Controller", size=13, color=ft.Colors.GREY_400)

        self.status_text = ft.Text("غير متصل", size=15, color=ft.Colors.RED_400)
        self.controller_name = ft.Text("", size=12, color=ft.Colors.GREY_500)

        self.start_btn = ft.ElevatedButton(
            "تشغيل النظام",
            icon=ft.Icons.PLAY_ARROW_ROUNDED,
            bgcolor=ft.Colors.GREEN_700,
            color=ft.Colors.WHITE,
            on_click=self.toggle_system,
            width=200,
            height=45,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8))
        )

        # ملاحظة حالة التطوير (تم إصلاح الحدود لمنع أي خطأ)
        self.dev_badge = ft.Container(
            content=ft.Column(
                [
                    ft.Row(
                        [
                            ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=ft.Colors.ORANGE_400, size=16),
                            ft.Text("تنبيه تطويري", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_400),
                        ],
                        spacing=6
                    ),
                    ft.Text(
                        "هذه واجهة قيد التطوير - وليست حتى نسخة ألفا.",
                        size=12,
                        color=ft.Colors.GREY_400,
                    )
                ],
                spacing=4
            ),
            padding=10,
            bgcolor="#221a0f",
            border_radius=8,
            border=ft.Border(
                top=ft.BorderSide(1, ft.Colors.ORANGE_900),
                bottom=ft.BorderSide(1, ft.Colors.ORANGE_900),
                left=ft.BorderSide(1, ft.Colors.ORANGE_900),
                right=ft.BorderSide(1, ft.Colors.ORANGE_900)
            )
        )

        self.scripts_column = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)

        # حاوي الشاشة الرئيسية
        self.dashboard_view = ft.Container(
            padding=20,
            content=ft.Column(
                [
                    self.title,
                    self.subtitle,
                    ft.Container(height=10),
                    ft.Row(
                        [
                            # اللوحة اليسرى: التحكم والملاحظة
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Text("حالة اليد", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                        self.status_text,
                                        self.controller_name,
                                        ft.Container(height=10),
                                        self.start_btn,
                                        ft.Container(height=20),
                                        self.dev_badge,
                                    ],
                                    spacing=6,
                                ),
                                padding=20, bgcolor="#1a1a1a", border_radius=12, width=300
                            ),
                            # اللوحة اليمنى: السكربتات
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Text("السكربتات المتاحة", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                        ft.Container(height=5),
                                        self.scripts_column,
                                    ],
                                    expand=True,
                                ),
                                padding=20, bgcolor="#1a1a1a", border_radius=12, expand=True, height=480
                            ),
                        ],
                        spacing=15, expand=True
                    )
                ],
                expand=True
            )
        )

        # --- 2. عناصر شاشة المحرّر (Editor View) ---
        self.editor_file_title = ft.Text("script.py", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.CYAN_300)
        
        self.code_editor = ft.TextField(
            multiline=True,
            expand=True,
            text_size=14,
            bgcolor="#121212",
            color="#A9B7C6",
            cursor_color=ft.Colors.CYAN_400,
            border_color="#2A2A2A",
            focused_border_color=ft.Colors.CYAN_500,
            content_padding=15,
        )

        # حاوي شاشة المحرر
        self.editor_view = ft.Container(
            visible=False,
            padding=15,
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Row(
                                    [
                                        ft.IconButton(
                                            icon=ft.Icons.ARROW_BACK_ROUNDED,
                                            icon_color=ft.Colors.WHITE,
                                            tooltip="رجوع للقائمة الرئيسية",
                                            on_click=self.close_editor
                                        ),
                                        ft.Icon(ft.Icons.CODE_ROUNDED, color=ft.Colors.CYAN_400, size=20),
                                        self.editor_file_title,
                                    ],
                                    spacing=10
                                ),
                                ft.ElevatedButton(
                                    "حفظ وتطبيق",
                                    icon=ft.Icons.SAVE_ROUNDED,
                                    bgcolor=ft.Colors.CYAN_700,
                                    color=ft.Colors.WHITE,
                                    on_click=self.save_script_from_editor,
                                    style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=6))
                                )
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        padding=10
                    ),
                    ft.Container(
                        content=self.code_editor,
                        expand=True,
                        border_radius=8,
                    )
                ],
                expand=True
            )
        )

        self.page.add(
            ft.Stack(
                [
                    self.dashboard_view,
                    self.editor_view
                ],
                expand=True
            )
        )

        self.refresh_scripts_ui()
        self.update_connection_status()

    def open_editor_page(self, script_name):
        self.current_script_editing = script_name
        file_path = os.path.join("scripts", f"{script_name}.py")

        code_content = ""
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                code_content = f.read()

        self.editor_file_title.value = f"scripts/{script_name}.py"
        self.code_editor.value = code_content
        
        self.dashboard_view.visible = False
        self.editor_view.visible = True
        self.page.update()

    def close_editor(self, e):
        self.dashboard_view.visible = True
        self.editor_view.visible = False
        self.current_script_editing = None
        self.page.update()

    def save_script_from_editor(self, e):
        if not self.current_script_editing:
            return

        script_name = self.current_script_editing
        file_path = os.path.join("scripts", f"{script_name}.py")

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.code_editor.value)

            if hasattr(self.engine, 'reload_script'):
                self.engine.reload_script(script_name)

            self.refresh_scripts_ui()
            
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"تم حفظ السكربت {script_name}.py وتطبيقه بنجاح!"),
                bgcolor=ft.Colors.GREEN_800
            )
            self.page.snack_bar.open = True
            self.page.update()

        except Exception as ex:
            print(f"خطأ أثناء الحفظ: {ex}")

    def refresh_scripts_ui(self):
        self.scripts_column.controls.clear()

        if not self.engine.loaded_scripts:
            self.scripts_column.controls.append(
                ft.Text("ما في سكربتات محملة", color=ft.Colors.GREY_500, size=14)
            )
        else:
            for name in self.engine.loaded_scripts:
                is_enabled = name in self.engine.enabled_scripts

                switch = ft.Switch(
                    value=is_enabled,
                    active_color=ft.Colors.CYAN_400,
                    on_change=lambda e, n=name: self.toggle_script(n, e.control.value)
                )

                edit_btn = ft.IconButton(
                    icon=ft.Icons.CODE_ROUNDED,
                    icon_color=ft.Colors.CYAN_400,
                    tooltip="فتح في المحرر",
                    on_click=lambda e, n=name: self.open_editor_page(n)
                )

                row = ft.Container(
                    content=ft.Row(
                        [
                            ft.Text(name, size=14, expand=True, color=ft.Colors.WHITE),
                            edit_btn,
                            switch
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=8,
                    bgcolor="#252525",
                    border_radius=8,
                )
                self.scripts_column.controls.append(row)

        self.page.update()

    def toggle_script(self, name, value):
        if value:
            self.engine.enable(name)
        else:
            self.engine.disable(name)

    def update_connection_status(self):
        if self.reader.is_connected():
            self.status_text.value = "متصل"
            self.status_text.color = ft.Colors.GREEN_400
            self.controller_name.value = self.reader.controller_name or ""
        else:
            self.status_text.value = "غير متصل"
            self.status_text.color = ft.Colors.RED_400
            self.controller_name.value = ""
        self.page.update()

    def toggle_system(self, e):
        if not self.running:
            self.start_system()
        else:
            self.stop_system()

    def start_system(self):
        if not self.reader.is_connected():
            self.status_text.value = "صلّ اليد أولاً !"
            self.status_text.color = ft.Colors.ORANGE_400
            self.page.update()
            return

        self.running = True
        self.start_btn.text = "إيقاف النظام"
        self.start_btn.bgcolor = ft.Colors.RED_700
        self.start_btn.icon = ft.Icons.STOP_ROUNDED
        self.page.update()

        self.thread = threading.Thread(target=self.run_loop, daemon=True)
        self.thread.start()

    def stop_system(self):
        self.running = False
        self.start_btn.text = "تشغيل النظام"
        self.start_btn.bgcolor = ft.Colors.GREEN_700
        self.start_btn.icon = ft.Icons.PLAY_ARROW_ROUNDED
        self.virtual.reset()
        self.page.update()

    def run_loop(self):
        while self.running:
            try:
                state = self.reader.get_state()
                state = self.engine.process(state)
                self.virtual.update(state)
                time.sleep(0.001)
            except Exception as e:
                print(f"خطأ في الحلقة: {e}")
                time.sleep(0.1)

def main(page: ft.Page):
    App(page)