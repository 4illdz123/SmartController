def process(state: dict) -> dict:
    if 'l3_pressed' not in state:
        state['l3_pressed'] = False
        state['y_pressed_time'] = 0

    if state['buttons']['l3'] and not state['l3_pressed']:
        state['l3_pressed'] = True
        state['y_pressed_time'] = 0
    elif not state['buttons']['l3'] and state['l3_pressed']:
        state['l3_pressed'] = False

    if state['l3_pressed']:
        state['y_pressed_time'] += 1 / 60  #假设帧率为60
        if state['y_pressed_time'] < 0.5:
            state['buttons']['y'] = True
        else:
            state['buttons']['y'] = False
        if state['y_pressed_time'] >= 1:
            state['y_pressed_time'] = 0
            state['buttons']['y'] = False

    return state