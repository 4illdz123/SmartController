from core.input_reader import InputReader
import time

reader = InputReader()

if not reader.is_connected():
    print("صلّ اليد وجرب مرة ثانية")
else:
    print("يقرأ اليد بنجاح! حرك الستيكات...")
    print("اضغط Ctrl+C للإيقاف")

    try:
        while True:
            state = reader.get_state()
            print(f"LX:{state['left_x']:.2f} | LY:{state['left_y']:.2f} | RX:{state['right_x']:.2f} | RY:{state['right_y']:.2f} | R2:{state['r2']:.2f}", end="\r")
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\nتوقف")
        reader.quit()