import requests
from bs4 import BeautifulSoup
import re
from pathlib import Path

# =========================
# パス設定
# =========================
BASE_DIR = Path(__file__).resolve().parent           # /Users/.../seimei-app
JS_DIR = BASE_DIR / "js"                             # /Users/.../seimei-app/js
OUTPUT_FILE = JS_DIR / "given_names.js"              # 出力先

START_YEAR = 2005
END_YEAR = 2025

# -------------------------
# 名前のバリデーション
# -------------------------
def is_valid_name(name: str) -> bool:
    # 前後と中の空白を削除
    name = re.sub(r"\s+", "", name.strip())

    # 文字数 1〜4 だけ採用（長すぎるのは除外）
    if len(name) < 1 or len(name) > 4:
        return False

    # すべて漢字（CJK）に限定（ひらがな・カタカナだけの名前は除外）
    if not all("\u4e00" <= ch <= "\u9fff" for ch in name):
        return False

    return True


# -------------------------
# HTML テーブルから名前を抜く
# -------------------------
def extract_from_table(table):
    result = []
    rows = table.select("tbody tr")
    for tr in rows:
        tds = tr.select("td")
        if len(tds) < 2:
            continue
        raw = tds[1].decode_contents()
        # 「颯太<br><span class=...」の部分から <br> より前だけ取り出す
        name = raw.split("<br>")[0].strip()
        # 念のためタグ除去
        name = re.sub(r"<.*?>", "", name)
        name = name.strip()
        if name:
            result.append(name)
    return result


# -------------------------
# 1ページ分をスクレイピング
# -------------------------
def extract_names_from_page(url):
    try:
        res = requests.get(url, timeout=10)
    except Exception as e:
        print(f"  ❌ リクエストエラー: {url} ({e})")
        return []

    if res.status_code != 200:
        print(f"  ❌ {res.status_code} {url}")
        return []

    soup = BeautifulSoup(res.text, "html.parser")
    tables = soup.select("table.tbl_ranking")
    if not tables:
        print(f"  （tbl_ranking なし）{url}")
        return []

    names = []
    for table in tables:
        names.extend(extract_from_table(table))
    print(f"  ✅ {url} → {len(names)}件取得")
    return names


# -------------------------
# 年ごとの URL を組み立て
# -------------------------
def build_urls_for_year(year):
    urls = []
    pages = ["", "?page=2", "?page=3", "?page=4", "?page=5"]

    # 〜2017年
    if year <= 2017:
        base = f"https://st.benesse.ne.jp/ninshin/name/{year}/name-ranking/"
        for p in pages:
            urls.append(base + p)

    # 2018〜2024年
    elif year <= 2024:
        for gender in ["boy", "girl"]:
            base = f"https://st.benesse.ne.jp/ninshin/name/{year}/{gender}/name-ranking/"
            for p in pages:
                urls.append(base + p)
    # 2025年
    else:
        for gender in ["boy", "girl"]:
            base = f"https://st.benesse.ne.jp/ninshin/name/{gender}/name-ranking/"
            for p in pages:
                urls.append(base + p)

    return urls


# -------------------------
# メイン処理
# -------------------------
def main():
    print("BASE_DIR =", BASE_DIR)
    print("JS_DIR   =", JS_DIR)
    print("OUTPUT   =", OUTPUT_FILE)

    all_names = set()

    for year in range(START_YEAR, END_YEAR + 1):
        print(f"\n▶ {year} 年")
        for url in build_urls_for_year(year):
            names = extract_names_from_page(url)
            for n in names:
                all_names.add(n)

    print(f"\n総取得件数（重複除去後）: {len(all_names)}")

    # ゆるくフィルタ
    filtered = sorted({n for n in all_names if is_valid_name(n)})

    print(f"フィルタ後件数: {len(filtered)}")
    print("フィルタ後サンプル:", filtered[:30])

    # もしフィルタ結果が 0 件なら、フィルタを無視して全部出す
    if not filtered:
        print("⚠ フィルタ後が 0 件だったので、フィルタを無視して全データを書き出します。")
        filtered = sorted(all_names)

    # js ディレクトリを確実に作る
    JS_DIR.mkdir(parents=True, exist_ok=True)

    lines = []
    lines.append("// 自動生成：たまひよ名前ランキング（2005-2025）")
    lines.append("window.GIVEN_NAME_MASTER = [")
    for n in filtered:
        safe_name = n.replace('"', '\\"')
        lines.append(f'  "{safe_name}",')
    lines.append("];")

    OUTPUT_FILE.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n✅ 出力完了: {OUTPUT_FILE.absolute()}")


if __name__ == "__main__":
    main()
