# scripts/anti_recoil.py
# scripts/anti_recoil.py

# القوة الافتراضية (تقدر تغيرها من الواجهة)
RECOIL_STRENGTH = 0.12

def process(state: dict) -> dict:
    global RECOIL_STRENGTH

    if state.get("r2", 0) > 0.25:
        current_y = state.get("right_y", 0.0)
        # نطبق الأنتي ريكويل
        state["right_y"] = max(-1.0, min(1.0, current_y - RECOIL_STRENGTH))
    
    return state

def set_strength(value: float):
    
    global RECOIL_STRENGTH
    RECOIL_STRENGTH = max(0.0, min(0.3, value))  # نحدد من 0 إلى 0.3