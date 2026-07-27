# scripts/rapid_fire.py

import time

# إعدادات الرابيد فاير
FIRE_RATE = 20          # عدد الطلقات في الثانية (جرب من 10 إلى 20)
last_shot_time = 0

def process(state: dict) -> dict:
    global last_shot_time

    r2_value = state.get("r2", 0.0)

    if r2_value > 0.15:  # إذا ضغطت الزناد
        current_time = time.time()
        interval = 1.0 / FIRE_RATE

        if current_time - last_shot_time >= interval:
            state["r2"] = 1.0          # اضغط الزناد بقوة
            last_shot_time = current_time
        else:
            state["r2"] = 0.0          # ارفع الزناد
    else:
        state["r2"] = 0.0
        last_shot_time = 0

    return state