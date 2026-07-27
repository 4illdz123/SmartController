# test_bridge.py

from core.input_reader import InputReader
from core.virtual_controller import VirtualController
from core.script_engine import ScriptEngine
import time

print("جاري تشغيل النظام الكامل...\n")

reader = InputReader()
virtual = VirtualController()
engine = ScriptEngine()

if not reader.is_connected():
    print("ما لقيت يد متصلة.")
    exit()

print(f"اليد: {reader.controller_name}")
engine.list_scripts()

# نفعّل السكربتات للتجربة

engine.enable("anti_recoil")
# engine.enable("rapid_fire")   # جرب هذا بعدين

print("النظام شغال... اضغط Ctrl+C للإيقاف\n")

try:
    while True:
        state = reader.get_state()
        state = engine.process(state)   # ← هنا السكربتات تشتغل
        virtual.update(state)
        time.sleep(0.001)
except KeyboardInterrupt:
    print("\nتم الإيقاف.")
    virtual.reset()
    reader.quit()