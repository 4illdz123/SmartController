import time

def process(state: dict) -> dict:
    if "_mode_second" not in state:
        state["_mode_second"] = False
        state["_last_toggle"] = time.time()

    # يشتغل فقط بالضغطة الواحدة على L3
    if state.get("l3", False):
        if time.time() - state["_last_toggle"] > 0.8:  # تأخير صغير
            state["right_x"] = 0.0 if state["_mode_second"] else -1.0
            state["_mode_second"] = not state["_mode_second"]
            state["_last_toggle"] = time.time()

    return state