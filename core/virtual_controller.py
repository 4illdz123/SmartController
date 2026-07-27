# core/virtual_controller.py

from vgamepad import VX360Gamepad
import time

class VirtualController:
    def __init__(self):
        self.gamepad = VX360Gamepad()
        print("[VirtualController] Xbox controller created successfully")

    def update(self, state: dict):
        """
        state لازم يحتوي على:
        left_x, left_y, right_x, right_y  (من -1 إلى 1)
        l2, r2                            (من 0 إلى 1)
        buttons                           (dict فيه True/False)
        """

        # الستيكات
        self.gamepad.left_joystick_float(
            x_value_float=state.get("left_x", 0.0),
            y_value_float=state.get("left_y", 0.0)
        )
        self.gamepad.right_joystick_float(
            x_value_float=state.get("right_x", 0.0),
            y_value_float=state.get("right_y", 0.0)
        )

        # الزناد (L2 / R2)
        self.gamepad.left_trigger_float(value_float=state.get("l2", 0.0))
        self.gamepad.right_trigger_float(value_float=state.get("r2", 0.0))

        # الأزرار
        buttons = state.get("buttons", {})

        mapping = {
            "a": self.gamepad.press_button if buttons.get("cross") else self.gamepad.release_button,
            "b": self.gamepad.press_button if buttons.get("circle") else self.gamepad.release_button,
            "x": self.gamepad.press_button if buttons.get("square") else self.gamepad.release_button,
            "y": self.gamepad.press_button if buttons.get("triangle") else self.gamepad.release_button,
            "left_shoulder": self.gamepad.press_button if buttons.get("l1") else self.gamepad.release_button,
            "right_shoulder": self.gamepad.press_button if buttons.get("r1") else self.gamepad.release_button,
            "back": self.gamepad.press_button if buttons.get("share") else self.gamepad.release_button,
            "start": self.gamepad.press_button if buttons.get("options") else self.gamepad.release_button,
            "left_thumb": self.gamepad.press_button if buttons.get("l3") else self.gamepad.release_button,
            "right_thumb": self.gamepad.press_button if buttons.get("r3") else self.gamepad.release_button,
        }

        from vgamepad import XUSB_BUTTON

        button_map = {
            "a": XUSB_BUTTON.XUSB_GAMEPAD_A,
            "b": XUSB_BUTTON.XUSB_GAMEPAD_B,
            "x": XUSB_BUTTON.XUSB_GAMEPAD_X,
            "y": XUSB_BUTTON.XUSB_GAMEPAD_Y,
            "left_shoulder": XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER,
            "right_shoulder": XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
            "back": XUSB_BUTTON.XUSB_GAMEPAD_BACK,
            "start": XUSB_BUTTON.XUSB_GAMEPAD_START,
            "left_thumb": XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB,
            "right_thumb": XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB,
        }

        for name, btn in button_map.items():
            if buttons.get(self._reverse_map(name), False):
                self.gamepad.press_button(button=btn)
            else:
                self.gamepad.release_button(button=btn)

        # إرسال التحديث
        self.gamepad.update()

    def _reverse_map(self, xbox_name):
        reverse = {
            "a": "cross",
            "b": "circle",
            "x": "square",
            "y": "triangle",
            "left_shoulder": "l1",
            "right_shoulder": "r1",
            "back": "share",
            "start": "options",
            "left_thumb": "l3",
            "right_thumb": "r3",
        }
        return reverse.get(xbox_name, xbox_name)

    def reset(self):
        self.gamepad.reset()
        self.gamepad.update()