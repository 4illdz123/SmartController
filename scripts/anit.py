# scripts/anti_recoil.py
# Anti-Recoil احترافي

RECOIL_STRENGTH = 0.09          # القوة العمودية (جرب من 0.05 إلى 0.15)
HORIZONTAL_COMP = 0.015         # تعويض يمين/يسار بسيط (اختياري)
ACTIVATION_THRESHOLD = 0.20     # متى يبدأ يشتغل (قيمة R2)

def process(state: dict) -> dict:
    global RECOIL_STRENGTH, HORIZONTAL_COMP

    r2 = state.get("r2", 0.0)

    if r2 > ACTIVATION_THRESHOLD:
        # القوة تزيد شوي مع قوة الضغط على الزناد
        strength = RECOIL_STRENGTH * (0.7 + (r2 * 0.3))

        # أنتي ريكويل عمودي
        current_y = state.get("right_y", 0.0)
        state["right_y"] = max(-1.0, min(1.0, current_y - strength))

        # تعويض أفقي بسيط (اختياري)
        current_x = state.get("right_x", 0.0)
        state["right_x"] = max(-1.0, min(1.0, current_x - HORIZONTAL_COMP))

    return state

def set_strength(value: float):
    global RECOIL_STRENGTH
    RECOIL_STRENGTH = max(0.0, min(0.25, float(value)))