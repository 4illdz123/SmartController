# ai/script_generator.py

from groq import Groq
from dotenv import load_dotenv
import os

# يحمل المتغيرات من ملف .env
load_dotenv()

class AIScriptGenerator:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")

        if not self.api_key:
            print("[AI] تحذير: ما لقيت GROQ_API_KEY في ملف .env")
            self.client = None
        else:
            self.client = Groq(api_key=self.api_key)

        self.system_prompt = """
أنت مساعد متخصص في كتابة سكربتات بايثون لتطبيق SmartController.
التطبيق يقرأ يد DualShock/DualSense ويحولها ليد Xbox افتراضية.

كل سكربت لازم يحتوي على دالة واحدة فقط بهذا الشكل:

def process(state: dict) -> dict:
    # الكود هنا
    return state

محتويات state:
- left_x, left_y, right_x, right_y  (من -1 إلى 1)
- l2, r2                            (من 0 إلى 1)
- buttons                           (dict فيه True/False)
  الأزرار المتاحة: cross, circle, square, triangle, l1, r1, l3, r3, share, options, dpad_up, dpad_down, dpad_left, dpad_right

اكتب الكود فقط بدون شرح وبدون ```python.
"""

    def generate_script(self, user_prompt: str) -> str:
        if not self.client:
            return '''# فشل التوليد: مفتاح API غير موجود
# ضع مفتاحك في ملف .env بهذا الشكل:
# GROQ_API_KEY=gsk_xxxxxxxxx

def process(state: dict) -> dict:
    return state
'''

        try:
            response = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.4,
                max_tokens=1024
            )

            code = response.choices[0].message.content.strip()

            # تنظيف الكود لو رجع داخل ```
            if "```" in code:
                parts = code.split("```")
                for part in parts:
                    clean = part.strip()
                    if clean.startswith("python"):
                        clean = clean[6:].strip()
                    if "def process" in clean:
                        code = clean
                        break

            return code.strip()

        except Exception as e:
            print(f"[AI] خطأ: {e}")
            return f'''# فشل التوليد
# الخطأ: {e}

def process(state: dict) -> dict:
    return state
'''