import os
from dotenv import load_dotenv
from google import genai

# تحميل المتغيرات من ملف .env
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(base_dir, ".env")
load_dotenv(dotenv_path=env_path)

class AIScriptGenerator:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.client = None
        
        if self.api_key:
            try:
                # التهيئة الصحيحة للمكتبة الجديدة
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"خطأ في تهيئة العميل: {e}")

    def generate_script(self, user_prompt: str) -> str:
        if not self.api_key or not self.client:
            return "# خطأ: لم يتم العثور على GEMINI_API_KEY. تأكد من إضافته في ملف .env"

        system_instruction = """
أنت محرك ذكاء اصطناعي متخصص في كتابة سكربتات تحكم ليد الألعاب (Controller Scripts).
وظيفتك إنشاء كود Python يحتوي حتماً على الدالة التالية:

def process(state: dict) -> dict:
    # تعديل الـ state هنا
    return state

قواعد مهمة جداً:
1. قم بإرجاع كود Python فقط! لا تضع أي شروحات، ولا تستخدم علامات Markdown مثل ```python أو ```.
2. أرجع الكود خاماً ليكون صالحاً للحفظ المباشر داخل ملف .py وتشغيله عبر exec أو import.
3. الـ dictionary المسمى `state` يحتوي على أزرار مثل: 'R2', 'L2', 'CROSS', 'SQUARE', 'TRIANGLE', 'CIRCLE', 'L1', 'R1', 'Y', 'X'.
4. اكتب كوداً نظيفاً، فعالاً، وبدون أخطاء بناء جملة (Syntax Errors).
"""

        try:
            # الموديل المعتمد والمتاح حالياً لجميع المشاريع
            response = self.client.models.generate_content(
                model='gemini-2.5-flash',
                contents=user_prompt,
                config={
                    'system_instruction': system_instruction,
                    'temperature': 0.2,
                }
            )

            code = response.text.strip()
            
            # تنظيف الكود من التنسيقات
            if code.startswith("```python"):
                code = code[9:]
            if code.startswith("```"):
                code = code[3:]
            if code.endswith("```"):
                code = code[:-3]

            return code.strip()

        except Exception as ex:
            print(f"خطأ أثناء التوليد: {ex}")
            return f"# حدث خطأ أثناء التوليد:\n# {ex}"