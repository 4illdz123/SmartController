import os
import importlib.util
import time

class ScriptEngine:
    def __init__(self, scripts_folder="scripts"):
        self.scripts_folder = scripts_folder
        self.loaded_scripts = {}   # name -> module
        self.enabled_scripts = set()  # أسماء السكربتات المفعلة
        self.load_all_scripts()

    def load_all_scripts(self):
        """يحمل كل ملفات الـ .py الموجودة في مجلد scripts"""
        if not os.path.exists(self.scripts_folder):
            os.makedirs(self.scripts_folder)
            print(f"[ScriptEngine] تم إنشاء مجلد {self.scripts_folder}")
            return

        for filename in os.listdir(self.scripts_folder):
            if filename.endswith(".py") and not filename.startswith("_"):
                script_name = filename[:-3]  # نشيل .py
                self.load_script(script_name)

    def load_script(self, script_name: str):
        """يحمل سكربت واحد"""
        path = os.path.join(self.scripts_folder, f"{script_name}.py")
        if not os.path.exists(path):
            print(f"[ScriptEngine] الملف غير موجود: {path}")
            return False

        try:
            # استخدام اسم فريد بالكامل للموديل حتى يسهل للذاكرة إعادة استيراده (Hot Reload)
            spec = importlib.util.spec_from_file_location(f"scripts.{script_name}", path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if not hasattr(module, "process"):
                print(f"[ScriptEngine] السكربت {script_name} ما فيه دالة process()")
                return False

            self.loaded_scripts[script_name] = module
            print(f"[ScriptEngine] تم تحميل السكربت: {script_name}")
            return True
        except Exception as e:
            print(f"[ScriptEngine] خطأ في تحميل {script_name}: {e}")
            return False

    def reload_script(self, script_name: str):
        """إعادة تحميل (Hot-Reload) لسكربت معين بعد تعديل كوده من الواجهة"""
        print(f"[ScriptEngine] جاري إعادة تحميل السكربت: {script_name}...")
        
        # حفظ حالة التفعيل السابقة (إذا كان مفعل أو متوقف)
        was_enabled = script_name in self.enabled_scripts
        
        # إعادة التحميل
        success = self.load_script(script_name)
        
        if success and was_enabled:
            self.enabled_scripts.add(script_name)
            
        return success

    def reload_all_scripts(self):
        """إعادة تحميل كافة السكربتات"""
        currently_enabled = set(self.enabled_scripts)
        self.loaded_scripts.clear()
        self.load_all_scripts()
        # إعادة التفعيل للسكربتات التي كانت مفعلة
        self.enabled_scripts = currently_enabled.intersection(set(self.loaded_scripts.keys()))

    def enable(self, script_name: str):
        if script_name in self.loaded_scripts:
            self.enabled_scripts.add(script_name)
            print(f"[ScriptEngine] تم تفعيل: {script_name}")
        else:
            print(f"[ScriptEngine] السكربت غير موجود: {script_name}")

    def disable(self, script_name: str):
        self.enabled_scripts.discard(script_name)
        print(f"[ScriptEngine] تم إيقاف: {script_name}")

    def toggle(self, script_name: str):
        if script_name in self.enabled_scripts:
            self.disable(script_name)
        else:
            self.enable(script_name)

    def process(self, state: dict) -> dict:
        """
        يمرر الحالة على كل السكربتات المفعلة بالترتيب
        """
        for name in list(self.enabled_scripts):
            try:
                script = self.loaded_scripts[name]
                state = script.process(state)
            except Exception as e:
                print(f"[ScriptEngine] خطأ أثناء تشغيل {name}: {e}")
        return state

    def list_scripts(self):
        print("\nالسكربتات المتاحة:")
        for name in self.loaded_scripts:
            status = "مفعل" if name in self.enabled_scripts else "متوقف"
            print(f"  - {name} [{status}]")
        print()