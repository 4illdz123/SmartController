# scripts/double_yy.py

import time

def process(state: dict) -> dict:
    if "_yy_last" not in state:
        state["_yy_last"] = 0.0
        state["_yy_on"] = False

    buttons = state.get("buttons", {})
    l3 = buttons.get("l3", False)

    if l3:
        now = time.time()

        # كل 0.05 ثانية يغير حالة الزر
        if now - state["_yy_last"] >= 0.05:
            state["_yy_on"] = not state["_yy_on"]
            state["_yy_last"] = now

        buttons["triangle"] = state["_yy_on"]
    else:
        state["_yy_on"] = False
        state["_yy_last"] = 0.0

    state["buttons"] = buttons
    return state