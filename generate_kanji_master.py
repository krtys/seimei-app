# generate_kanji_master.py
# 辞典の家: 常用漢字一覧（https://kanji.jitenon.jp/cat/joyo）
# を元に KANJI_MASTER を自動生成するスクリプト

import re
import requests
from bs4 import BeautifulSoup
from pathlib import Path

URL = "https://kanji.jitenon.jp/cat/joyo"

def zenkaku_to_hankaku_num(s: str) -> int:
    """'３' みたいな全角数字を int に変換する（'10' なども想定）"""
    table = str.maketrans("０１２３４５６７８９", "0123456789")
    return int(s.translate(table))

def fetch_kanji_strokes():
    resp = requests.get(URL)
    resp.encoding = resp.apparent_encoding  # 日本語の文字化け対策
    soup = BeautifulSoup(resp.text, "html.parser")

    kanji_to_strokes = {}

    # h3タグなどに「３画」「４画」…と書かれているのでそこを見る
    for heading in soup.find_all(["h2", "h3", "h4"]):
        text = heading.get_text(strip=True)
        m = re.match(r"([0-9０-９]+)画", text)
        if not m:
            continue

        strokes = zenkaku_to_hankaku_num(m.group(1))

        # 見出しの次に来る <ul> の中に漢字リンクが並んでいる想定
        ul = heading.find_next_sibling("ul")
        if not ul:
            continue

        for a in ul.find_all("a"):
            char = a.get_text(strip=True)
            # 一文字の漢字だけ採用
            if len(char) == 1:
                kanji_to_strokes[char] = strokes

    return kanji_to_strokes

def build_js(kanji_to_strokes: dict) -> str:
    # 漢字そのままの順番でもいいけど、
    # ここでは「画数→漢字」で並べておくと人間も見やすい
    items = sorted(
        kanji_to_strokes.items(),
        key=lambda x: (x[1], x[0])  # (画数, 漢字) でソート
    )

    lines = []
    lines.append("// 自動生成: 常用漢字の画数マスタ")
    lines.append("// 参照元: https://kanji.jitenon.jp/cat/joyo")
    lines.append("const KANJI_MASTER = {")
    for char, strokes in items:
        lines.append(f'  "{char}": {strokes},')
    lines.append("};")
    lines.append("")
    lines.append("export default KANJI_MASTER;")
    return "\n".join(lines)

def main():
    print("常用漢字の画数データを取得中...")
    kanji_to_strokes = fetch_kanji_strokes()
    print(f"取得した漢字の数: {len(kanji_to_strokes)}")

    js_code = build_js(kanji_to_strokes)

    # js/kanji_master.js に書き出し
    js_dir = Path("js")
    js_dir.mkdir(exist_ok=True)
    out_path = js_dir / "kanji_master.js"
    out_path.write_text(js_code, encoding="utf-8")
    print(f"書き出し完了: {out_path.resolve()}")

if __name__ == "__main__":
    main()
