# core/virtual_controller.py

from vgamepad import VX360Gamepad, XUSB_BUTTON

class VirtualController:
    def __init__(self):
        self.gamepad = VX360Gamepad()
        print("[VirtualController] Xbox controller created successfully")

    def update(self, state: dict):
        # الستيكات
        self.gamepad.left_joystick_float(
            x_value_float=state.get("left_x", 0.0),
            y_value_float=state.get("left_y", 0.0)
        )
        self.gamepad.right_joystick_float(
            x_value_float=state.get("right_x", 0.0),
            y_value_float=state.get("right_y", 0.0)
        )

        # الزناد
        self.gamepad.left_trigger_float(value_float=state.get("l2", 0.0))
        self.gamepad.right_trigger_float(value_float=state.get("r2", 0.0))

        # الأزرار
        buttons = state.get("buttons", {})

        button_map = {
            "cross":      XUSB_BUTTON.XUSB_GAMEPAD_A,
            "circle":     XUSB_BUTTON.XUSB_GAMEPAD_B,
            "square":     XUSB_BUTTON.XUSB_GAMEPAD_X,
            "triangle":   XUSB_BUTTON.XUSB_GAMEPAD_Y,
            "l1":         XUSB_BUTTON.XUSB_GAMEPAD_LEFT_SHOULDER,
            "r1":         XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_SHOULDER,
            "share":      XUSB_BUTTON.XUSB_GAMEPAD_BACK,
            "options":    XUSB_BUTTON.XUSB_GAMEPAD_START,
            "l3":         XUSB_BUTTON.XUSB_GAMEPAD_LEFT_THUMB,
            "r3":         XUSB_BUTTON.XUSB_GAMEPAD_RIGHT_THUMB,
            "dpad_up":    XUSB_BUTTON.XUSB_GAMEPAD_DPAD_UP,
            "dpad_down":  XUSB_BUTTON.XUSB_GAMEPAD_DPAD_DOWN,
            "dpad_left":  XUSB_BUTTON.XUSB_GAMEPAD_DPAD_LEFT,
            "dpad_right": XUSB_BUTTON.XUSB_GAMEPAD_DPAD_RIGHT,
        }

        for name, btn in button_map.items():
            if buttons.get(name, False):
                self.gamepad.press_button(button=btn)
            else:
                self.gamepad.release_button(button=btn)

        self.gamepad.update()

    def reset(self):
        self.gamepad.reset()
        self.gamepad.update()