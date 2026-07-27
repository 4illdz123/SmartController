from vgamepad import VX360Gamepad
import time

print("Creating virtual Xbox controller...")
gamepad = VX360Gamepad()
print("Success! Virtual controller created.")

# نجرب نحرك الستيك شوي
gamepad.left_joystick_float(x_value_float=0.5, y_value_float=0.0)
gamepad.update()
time.sleep(1)

gamepad.reset()
gamepad.update()
print("Test finished.")