# ui/main_window.py

import flet as ft
from core.input_reader import InputReader
from core.virtual_controller import VirtualController
from core.script_engine import ScriptEngine
import threading
import time

class App:
    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "DualSenseX Pro"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 20
        self.page.window.width = 920
        self.page.window.height = 670
        self.page.window.resizable = False
        self.page.bgcolor = "#0f0f0f"

        self.reader = InputReader()
        self.virtual = VirtualController()
        self.engine = ScriptEngine()

        self.running = False
        self.thread = None

        self.build_ui()

    def build_ui(self):
        self.title = ft.Text(
            "DualSenseX Pro",
            size=34,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.CYAN_400
        )

        self.subtitle = ft.Text(
            "DualShock 4 / DualSense → Xbox Virtual Controller",
            size=14,
            color=ft.Colors.GREY_400
        )

        self.status_text = ft.Text("غير متصل", size=16, color=ft.Colors.RED_400)
        self.controller_name = ft.Text("", size=13, color=ft.Colors.GREY_500)

        self.start_btn = ft.ElevatedButton(
            "تشغيل النظام",
            icon=ft.Icons.PLAY_ARROW_ROUNDED,
            bgcolor=ft.Colors.GREEN_700,
            color=ft.Colors.WHITE,
            on_click=self.toggle_system,
            width=200,
            height=48,
            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10))
        )

        self.recoil_text = ft.Text("قوة الـ Anti-Recoil: 0.08", size=14, color=ft.Colors.CYAN_200)

        self.recoil_slider = ft.Slider(
            min=0.0,
            max=0.25,
            divisions=25,
            value=0.08,
            label="{value}",
            active_color=ft.Colors.CYAN_400,
            thumb_color=ft.Colors.CYAN_200,
            on_change=self.on_recoil_change,
            width=230
        )

        self.scripts_column = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)

        self.page.add(
            ft.Column(
                [
                    self.title,
                    self.subtitle,
                    ft.Container(height=15),
                    ft.Row(
                        [
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Text("حالة اليد", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                        self.status_text,
                                        self.controller_name,
                                        ft.Container(height=10),
                                        self.start_btn,
                                        ft.Container(height=25),
                                        ft.Text("إعدادات Anti-Recoil", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                        ft.Container(height=8),
                                        self.recoil_text,
                                        self.recoil_slider,
                                    ],
                                    spacing=6,
                                ),
                                padding=22,
                                bgcolor="#1a1a1a",
                                border_radius=14,
                                width=310,
                            ),
                            ft.Container(
                                content=ft.Column(
                                    [
                                        ft.Text("السكربتات المتاحة", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                        ft.Container(height=8),
                                        self.scripts_column,
                                    ],
                                    expand=True,
                                ),
                                padding=22,
                                bgcolor="#1a1a1a",
                                border_radius=14,
                                expand=True,
                                height=480,
                            ),
                        ],
                        spacing=20,
                        expand=True,
                    ),
                ],
                expand=True,
            )
        )

        self.refresh_scripts_ui()
        self.update_connection_status()

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

                row = ft.Container(
                    content=ft.Row(
                        [
                            ft.Text(name, size=15, expand=True, color=ft.Colors.WHITE),
                            switch
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=14,
                    bgcolor="#252525",
                    border_radius=10,
                )
                self.scripts_column.controls.append(row)

        self.page.update()

    def toggle_script(self, name, value):
        if value:
            self.engine.enable(name)
        else:
            self.engine.disable(name)

    def on_recoil_change(self, e):
        value = round(float(e.control.value), 3)
        self.recoil_text.value = f"قوة الـ Anti-Recoil: {value}"

        if "anti_recoil" in self.engine.loaded_scripts:
            try:
                self.engine.loaded_scripts["anti_recoil"].set_strength(value)
            except Exception as ex:
                print(f"خطأ في تحديث قوة الريكويل: {ex}")

        self.page.update()

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