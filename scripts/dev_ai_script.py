def process(state: dict) -> dict:
    state['buttons']['y'] = state['buttons']['triangle']
    state['buttons']['b'] = state['buttons']['circle']
    state['buttons']['a'] = state['buttons']['cross']
    state['buttons']['x'] = state['buttons']['square']
    return state