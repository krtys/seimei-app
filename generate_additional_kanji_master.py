# generate_all_kanji_master.py
# kanji_master.js + additional_kanji_master.js をマージして
# 重複排除した all_kanji_master.js を生成するスクリプト

import re
from pathlib import Path


def load_js_kanji_map(path: str) -> dict:
    """
    JSファイルの ' "漢": 数字, ' 形式をすべて抽出して dict にする
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"{path} が見つかりません。")

    text = p.read_text(encoding="utf-8")

    # 例: "花": 7,
    pairs = re.findall(r'"(.)"\s*:\s*([0-9]+)', text)
    return {ch: int(strokes) for ch, strokes in pairs}


def build_js(kanji_map: dict) -> str:
    """
    JS のソースコードとして整形する
    """
    items = sorted(kanji_map.items(), key=lambda x: (x[1], x[0]))

    lines = []
    lines.append("// 自動生成: 常用＋追加漢字の統合マスタ")
    lines.append("const ALL_KANJI_MASTER = {")
    for ch, strokes in items:
        lines.append(f'  "{ch}": {strokes},')
    lines.append("};")
    lines.append("")
    lines.append("export default ALL_KANJI_MASTER;")
    return "\n".join(lines)


def main():
    print("既存 kanji_master.js を読込中…")
    base_map = load_js_kanji_map("js/kanji_master.js")
    print(f" - 読込: {len(base_map)}字")

    print("追加 additional_kanji_master.js を読込中…")
    add_map = load_js_kanji_map("js/additional_kanji_master.js")
    print(f" - 読込: {len(add_map)}字")

    # マージ（追加分が優先）
    merged = {**base_map, **add_map}
    print(f"統合後の総漢字数: {len(merged)}字")

    js_code = build_js(merged)

    out_path = Path("js") / "all_kanji_master.js"
    out_path.write_text(js_code, encoding="utf-8")
    print(f"書き出し完了: {out_path.resolve()}")


if __name__ == "__main__":
    main()
