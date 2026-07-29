# Combo Script: my_combo
import time

def process(state: dict) -> dict:
    buttons = state.get("buttons", {})
    is_triggered = False

    if "r2" in ["l2", "r2"]:
        is_triggered = state.get("r2", 0) > 0.5
    else:
        is_triggered = buttons.get("r2", False)

    if is_triggered:
        sequence = [('cross', 50), ('l2', 50), ('circle', 50)]
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
