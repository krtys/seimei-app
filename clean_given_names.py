import re
from pathlib import Path

# -------------------------
# 設定（jsフォルダの下を読む）
# -------------------------
BASE_DIR = Path("/Users/yushi.kurita/Documents/seimei-app")
JS_DIR = BASE_DIR / "js"

INPUT_FILE = JS_DIR / "given_names.js"
OUTPUT_FILE = JS_DIR / "given_names_cleaned.js"

# -------------------------
# JSファイルから名前だけ抽出
# -------------------------

def extract_names(js_text: str):
    """
    JS内の "名前" をすべて抽出して返す
    """
    candidates = re.findall(r'"([^"]+)"', js_text)
    cleaned = []

    for name in candidates:
        name = name.strip()
        if not name:
            continue
        cleaned.append(name)

    return cleaned

# -------------------------
# 重複排除
# -------------------------

def remove_duplicates(name_list):
    seen = set()
    unique = []
    for name in name_list:
        if name not in seen:
            unique.append(name)
            seen.add(name)
    return unique

# -------------------------
# JS形式で書き込み
# -------------------------

def write_output(names, outfile: Path):
    with outfile.open("w", encoding="utf-8") as f:
        f.write("const GIVEN_NAME_MASTER = [\n")
        for name in names:
            f.write(f'  "{name}",\n')
        f.write("];\n\nexport default GIVEN_NAME_MASTER;\n")

# -------------------------
# メイン処理
# -------------------------

def main():
    print(f"読み込みファイル: {INPUT_FILE}")

    if not INPUT_FILE.exists():
        print("❌ エラー: given_names.js が存在しません")
        return

    js_text = INPUT_FILE.read_text(encoding="utf-8")

    names = extract_names(js_text)
    print(f"抽出件数: {len(names)}")

    names_unique = remove_duplicates(names)
    print(f"重複排除後: {len(names_unique)} 件")

    write_output(names_unique, OUTPUT_FILE)
    print(f"✅ 出力完了: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
