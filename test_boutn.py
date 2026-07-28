# test_buttons.py

import pygame
import time

pygame.init()
pygame.joystick.init()

if pygame.joystick.get_count() == 0:
    print("ما في يد متصلة")
    exit()

joy = pygame.joystick.Joystick(0)
joy.init()

print(f"اليد: {joy.get_name()}")
print(f"عدد الأزرار: {joy.get_numbuttons()}")
print(f"عدد المحاور: {joy.get_numaxes()}")
print(f"عدد الـ Hats: {joy.get_numhats()}")
print("\nاضغط أي زر في اليد... (Ctrl+C للإيقاف)\n")

try:
    while True:
        pygame.event.pump()

        # الأزرار
        for i in range(joy.get_numbuttons()):
            if joy.get_button(i):
                print(f"زر رقم {i} مضغوط")

        # الـ D-Pad (Hat)
        for i in range(joy.get_numhats()):
            hat = joy.get_hat(i)
            if hat != (0, 0):
                print(f"Hat {i}: {hat}")

        time.sleep(0.05)

except KeyboardInterrupt:
    print("\nتوقف")
    pygame.quit()