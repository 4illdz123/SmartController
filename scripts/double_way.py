import time

def process(state: dict) -> dict:
    if "_double_way" not in state:
        state["_double_way"] = False
        state["_last_toggle"] = time.time()
        state["_count"] = 0

    # يشتغل فقط بالضغطة الواحدة على L3
    if state.get("l3", False):
        now = time.time()
        if now - state["_last_toggle"] > 0.4:
            state["_count"] += 1
            if state["_count"] <= 6:  # 3 دورات كاملة
                state["right_x"] = 0.0 if state["_double_way"] else -1.0
                state["_double_way"] = not state["_double_way"]
            else:
                state["right_x"] = 0.0
                state["_count"] = 0
                state["_double_way"] = False
            state["_last_toggle"] = now

    return state