import re
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
JS_DIR = BASE_DIR / "js"

FILE_GENERATED = JS_DIR / "given_names_generated.js"
FILE_CLEANED = JS_DIR / "given_names_cleaned.js"
FILE_OUTPUT = JS_DIR / "given_names.js"


def extract_array(js_text: str) -> list:
    """
    JSファイル内の [ "...", ... ] の配列部分だけを抽出して Python list にする。
    """
    # 最初の配列を抽出（複数あっても最初のを使う）
    m = re.search(r"\[\s*([\s\S]*?)\s*\]", js_text)
    if not m:
        raise ValueError("JS内に配列リテラルが見つかりません")

    array_body = m.group(1)

    # JSの "xxx", の列を全部抜き出す
    names = re.findall(r'"([^"]+)"', array_body)
    return names


def main():
    # 読み込み
    gen_text = FILE_GENERATED.read_text(encoding="utf-8")
    cleaned_text = FILE_CLEANED.read_text(encoding="utf-8")

    gen_list = extract_array(gen_text)
    cleaned_list = extract_array(cleaned_text)

    print(f"generated: {len(gen_list)} 件")
    print(f"cleaned  : {len(cleaned_list)} 件")

    # マージ + 重複削除（保持順は genereted -> cleaned の順）
    merged = list(dict.fromkeys(gen_list + cleaned_list))

    print(f"merged   : {len(merged)} 件")

    # JSとして出力
    out_js = "const GIVEN_NAMES = [\n"
    for n in merged:
        out_js += f'  "{n}",\n'
    out_js += "];\n\n"
    out_js += 'if (typeof window !== "undefined") {\n'
    out_js += "  window.GIVEN_NAMES = GIVEN_NAMES;\n"
    out_js += "}\n"

    FILE_OUTPUT.write_text(out_js, encoding="utf-8")

    print("書き込み完了:", FILE_OUTPUT)


if __name__ == "__main__":
    main()
