// js/patterns.js
// 五格の吉凶パターン定義（1〜50画）

window.LUCK_PATTERNS = (function () {
  // ランク定義
  const rankMeta = {
    daikichi: { rank: "daikichi", label: "大吉", score: 4 },
    kichi: { rank: "kichi", label: "吉", score: 3 },
    chukichi: { rank: "chukichi", label: "中吉", score: 2 },
    suekichi: { rank: "suekichi", label: "末吉", score: 1 },
    kyo: { rank: "kyo", label: "凶", score: 0 },
    unknown: { rank: "unknown", label: "判定外", score: 0 }
  };

  // stroke数 → ランク情報
  const total = {};

  const assign = (strokes, meta) => {
    total[strokes] = meta;
  };

  // 1〜50画までを網羅
  // ※だいたい「強め（大吉）」「良い（吉）」「まずまず（中吉・末吉）」「弱い（凶）」が
  //   バランス良く散るように割り振り

  const daikichiList = [
    3, 5, 6, 7, 8,
    11, 13, 15, 16,
    24, 31, 33, 35, 37,
    41, 45, 47
  ];

  const kichiList = [
    1, 9, 10,
    17, 21, 23, 25, 29,
    39, 43, 49
  ];

  const chukichiList = [
    18, 26, 32, 36, 40, 44
  ];

  const suekichiList = [
    4, 14, 22, 28, 30, 34, 38, 42, 46, 48
  ];

  const kyoList = [
    2, 12, 19, 20, 27, 50
  ];

  daikichiList.forEach((s) => assign(s, rankMeta.daikichi));
  kichiList.forEach((s) => assign(s, rankMeta.kichi));
  chukichiList.forEach((s) => assign(s, rankMeta.chukichi));
  suekichiList.forEach((s) => assign(s, rankMeta.suekichi));
  kyoList.forEach((s) => assign(s, rankMeta.kyo));

  // 念のための安全装置：
  // 1〜50のうち、どこにも入っていない画数があれば「末吉」で埋める
  for (let s = 1; s <= 50; s++) {
    if (!total[s]) {
      total[s] = rankMeta.suekichi;
    }
  }

  return {
    rankMeta,
    total
  };
})();
