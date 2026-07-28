# core/input_reader.py

import pygame

class InputReader:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()

        self.joystick = None
        self.controller_name = None
        self._try_connect()

    def _try_connect(self):
        """يحاول الاتصال باليد"""
        pygame.joystick.quit()
        pygame.joystick.init()

        if pygame.joystick.get_count() == 0:
            self.joystick = None
            self.controller_name = None
            return False

        try:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            self.controller_name = self.joystick.get_name()
            print(f"[InputReader] تم اكتشاف اليد: {self.controller_name}")
            return True
        except Exception as e:
            print(f"[InputReader] خطأ في الاتصال: {e}")
            self.joystick = None
            self.controller_name = None
            return False

    def is_connected(self) -> bool:
        # نتحقق باستمرار
        if self.joystick is None:
            return self._try_connect()

        try:
            # نتحقق إن اليد لسا موجودة
            _ = self.joystick.get_name()
            return True
        except:
            self.joystick = None
            self.controller_name = None
            return self._try_connect()

    def get_state(self) -> dict:
        if not self.is_connected():
            return self._empty_state()

        try:
            pygame.event.pump()

            left_x = self.joystick.get_axis(0)
            left_y = -self.joystick.get_axis(1)
            right_x = self.joystick.get_axis(2)
            right_y = -self.joystick.get_axis(3)

            try:
                l2 = (self.joystick.get_axis(4) + 1) / 2
                r2 = (self.joystick.get_axis(5) + 1) / 2
            except:
                l2 = 0.0
                r2 = 0.0

            buttons = {
                "cross":      self.joystick.get_button(0),
                "circle":     self.joystick.get_button(1),
                "square":     self.joystick.get_button(2),
                "triangle":   self.joystick.get_button(3),
                "share":      self.joystick.get_button(4),
                "ps":         self.joystick.get_button(5),
                "options":    self.joystick.get_button(6),
                "l3":         self.joystick.get_button(7),
                "r3":         self.joystick.get_button(8),
                "l1":         self.joystick.get_button(9),
                "r1":         self.joystick.get_button(10),
                "dpad_up":    self.joystick.get_button(11),
                "dpad_down":  self.joystick.get_button(12),
                "dpad_left":  self.joystick.get_button(13),
                "dpad_right": self.joystick.get_button(14),
                "touchpad":   self.joystick.get_button(15) if self.joystick.get_numbuttons() > 15 else False,
            }

            def apply_deadzone(value, deadzone=0.08):
                return value if abs(value) > deadzone else 0.0

            return {
                "left_x": apply_deadzone(left_x),
                "left_y": apply_deadzone(left_y),
                "right_x": apply_deadzone(right_x),
                "right_y": apply_deadzone(right_y),
                "l2": max(0.0, min(1.0, l2)),
                "r2": max(0.0, min(1.0, r2)),
                "buttons": buttons,
                "controller_name": self.controller_name
            }
        except Exception:
            self.joystick = None
            self.controller_name = None
            return self._empty_state()

    def _empty_state(self):
        return {
            "left_x": 0.0,
            "left_y": 0.0,
            "right_x": 0.0,
            "right_y": 0.0,
            "l2": 0.0,
            "r2": 0.0,
            "buttons": {},
            "controller_name": None
        }

    def quit(self):
        try:
            pygame.quit()
        except:
            pass