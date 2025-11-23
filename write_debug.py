from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
JS_DIR = BASE_DIR / "js"
TARGET = JS_DIR / "given_names_test.txt"

print("BASE_DIR =", BASE_DIR)
print("JS_DIR   =", JS_DIR)
print("TARGET   =", TARGET)
print("TARGET exists before write:", TARGET.exists())

try:
    JS_DIR.mkdir(parents=True, exist_ok=True)
    TARGET.write_text("hello\n", encoding="utf-8")
    print("WRITE SUCCESS")
except Exception as e:
    print("WRITE ERROR:", e)

print("TARGET exists after write:", TARGET.exists())
print("Actual absolute path:", TARGET.resolve())
