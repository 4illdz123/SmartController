import time

last_press_time = 0.0
yy_stage = 0

def process(state: dict) -> dict:
    global last_press_time, yy_stage
    
    current_time = time.time()
    
    # فحص هل زر L3 مضغوط حالياً
    l3_pressed = state.get('L3', 0) > 0 or state.get('L_THUMB', 0) > 0

    # إذا رفع المستخدم إصبعه عن L3، قم بإلغاء التكرار فوراً
    if not l3_pressed:
        yy_stage = 0
        return state

    # إذا كان L3 مضغوطاً وابتدأت الدورة أو انتهت، ابدأ دورة YY جديدة
    if yy_stage == 0:
        yy_stage = 1
        last_press_time = current_time

    # المرحلة 1: ضغط Y الأولى
    if yy_stage == 1:
        state['Y'] = 1
        state['TRIANGLE'] = 1
        if current_time - last_press_time >= 0.04:
            yy_stage = 2
            last_press_time = current_time

    # المرحلة 2: إفلات الزر لفترة قصيرة
    elif yy_stage == 2:
        state['Y'] = 0
        state['TRIANGLE'] = 0
        if current_time - last_press_time >= 0.04:
            yy_stage = 3
            last_press_time = current_time

    # المرحلة 3: ضغط Y الثانية
    elif yy_stage == 3:
        state['Y'] = 1
        state['TRIANGLE'] = 1
        if current_time - last_press_time >= 0.04:
            yy_stage = 0  # العودة للمرحلة الأولى لإعادة الكرة طالما L3 مضغوط

    return state