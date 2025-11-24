// ================================================================
// 1. グローバル関数として画数計算を公開
// ================================================================
function calcStrokeForString(str) {
  if (!str) return 0;

  const normalized = str.normalize("NFC");
  let total = 0;

  for (const ch of normalized) {
    const strokes = ALL_KANJI_MASTER[ch];
    if (strokes == null) {
      console.warn(`画数マスタに存在しない文字: ${ch}`);
      return 0;
    }
    total += strokes;
  }
  return total;
}
window.calcStrokeForString = calcStrokeForString;


// ================================================================
// 2. 五格計算処理
// ================================================================
function calcGokaku(familyName, givenName) {
  const familyStroke = calcStrokeForString(familyName);
  const givenStroke  = calcStrokeForString(givenName);

  const tenkaku = familyStroke;
  const chikaku = givenStroke;

  const seiLast  = familyName.slice(-1) || "";
  const meiFirst = givenName.charAt(0) || "";

  const jinkaku = seiLast && meiFirst
    ? calcStrokeForString(seiLast + meiFirst)
    : tenkaku + chikaku;

  const soukaku = tenkaku + chikaku;
  const gaikaku = soukaku - jinkaku;

  return { familyStroke, givenStroke, tenkaku, jinkaku, chikaku, gaikaku, soukaku };
}


// ================================================================
// 3. 吉凶判定（patterns.js）
// ================================================================
function judgeRank(strokes) {
  const info = LUCK_PATTERNS.total[strokes];
  return info || LUCK_PATTERNS.rankMeta.unknown;
}


// ================================================================
// 4. GA4：未捕捉エラー / Promiseエラー を一括で拾う
// ================================================================
window.onerror = function (message, source, lineno, colno, error) {
  try {
    if (typeof gtag === "function") {
      gtag("event", "js_error", {
        message: String(message),
        source: source || "",
        lineno: lineno || 0,
        colno: colno || 0,
        stack: error && error.stack 
          ? error.stack.substring(0, 500) 
          : ""
      });
    }
  } catch (_) {}
};

window.addEventListener("unhandledrejection", function (event) {
  try {
    if (typeof gtag === "function") {
      gtag("event", "js_unhandled_promise", {
        reason: String(event.reason),
        stack: event.reason && event.reason.stack
          ? event.reason.stack.substring(0, 500)
          : ""
      });
    }
  } catch (_) {}
});

// アプリ内部で任意エラーを送る用
function reportAppError(type, detail = "") {
  try {
    if (typeof gtag === "function") {
      gtag("event", "app_error", {
        error_type: type,
        detail: String(detail).substring(0, 500)
      });
    }
  } catch (_) {}
}


// ================================================================
// 5. DOM Ready
// ================================================================
window.addEventListener("DOMContentLoaded", () => {
  const form            = document.getElementById("searchForm");
  const resultsSection  = document.getElementById("resultsSection");
  const resultsSummary  = document.getElementById("resultsSummary");
  const resultsContainer= document.getElementById("resultsContainer");

  // --------------------------------------------------------------
  // Submit（検索実行）
  // --------------------------------------------------------------
  form.addEventListener("submit", (e) => {
    e.preventDefault();

    const familyName   = document.getElementById("familyName").value.trim();
    const preferredKanjiInput = document.getElementById("preferredKanji").value.trim();
    const targetLuck   = document.getElementById("targetLuck").value;

    if (!familyName) {
      alert("苗字を入力してください。");
      return;
    }

    const familyStroke = calcStrokeForString(familyName);
    if (familyStroke === 0) {
      alert("苗字に対応していない漢字があります（画数マスタ不足）");
      reportAppError("stroke_master_missing", familyName);
      return;
    }

    const preferredKanjiList = preferredKanjiInput
      ? preferredKanjiInput.split(/\s+/).filter(Boolean)
      : [];

    const groups = generateNameGroups({
      familyName,
      familyStroke,
      preferredKanjiList,
      targetLuck
    });

    // ------------------------------------------------------------
    // GA4: サイト内検索イベント（ view_search_results ）
    // ------------------------------------------------------------
    try {
      if (typeof gtag === "function") {
        const parts = [];
        if (familyName) parts.push(`姓:${familyName}`);
        if (preferredKanjiInput) parts.push(`漢字:${preferredKanjiInput}`);
        if (targetLuck && targetLuck !== "all") {
          const luckLabel =
            targetLuck === "excellent" ? "大吉のみ" :
            targetLuck === "good" ? "吉以上" :
            "指定なし";
          parts.push(`運勢:${luckLabel}`);
        }
        const searchTerm = parts.join(" / ") || "(no term)";

        const totalResults = groups.reduce(
          (sum, g) => sum + g.candidates.length,
          0
        );

        gtag("event", "view_search_results", {
          search_term: searchTerm,
          result_count: totalResults,
          raw_family_name: familyName,
          raw_preferred_kanji: preferredKanjiInput,
          target_luck: targetLuck
        });
      }
    } catch (err) {
      console.warn("GA4検索イベント送信に失敗:", err);
      reportAppError("ga_search_event_failed", String(err));
    }

    renderResults(groups);
  });

  // --------------------------------------------------------------
  // 名前候補生成（既存）
  // --------------------------------------------------------------
  function generateNameGroups({ familyName, familyStroke, preferredKanjiList, targetLuck }) {
    const groups = [];

    const targetKanjiList =
      preferredKanjiList.length > 0
        ? [...new Set(preferredKanjiList)]
        : [null];

    targetKanjiList.forEach((targetKanji) => {
      let givenCandidates = [...GIVEN_NAME_MASTER];
      if (targetKanji) {
        givenCandidates = givenCandidates.filter((g) => g.includes(targetKanji));
      }

      const results = [];

      givenCandidates.forEach((given) => {
        const gk = calcGokaku(familyName, given);
        if (gk.givenStroke === 0) return;

        const totalLuck = judgeRank(gk.soukaku);

        if (targetLuck === "excellent" && totalLuck.rank !== "daikichi") return;
        if (targetLuck === "good" && !["daikichi", "kichi"].includes(totalLuck.rank)) return;

        results.push({
          familyName, givenName: given, ...gk,
          tenLuck: judgeRank(gk.tenkaku),
          jinLuck: judgeRank(gk.jinkaku),
          chiLuck: judgeRank(gk.chikaku),
          gaiLuck: judgeRank(gk.gaikaku),
          totalLuck
        });
      });

      results.sort((a, b) => {
        const diff = b.totalLuck.score - a.totalLuck.score;
        if (diff !== 0) return diff;
        return a.soukaku - b.soukaku;
      });

      groups.push({
        kanji: targetKanji,
        candidates: results.slice(0, 20)
      });
    });

    return groups;
  }


  // --------------------------------------------------------------
  // 結果生成（既存）
  // --------------------------------------------------------------
  function renderResults(groups) {
    resultsContainer.innerHTML = "";

    const totalCount = groups.reduce((sum, g) => sum + g.candidates.length, 0);
    resultsSummary.textContent = `合計${totalCount}件の候補を表示しています。`;
    resultsSection.hidden = false;

    groups.forEach((group) => {
      const section = document.createElement("section");
      section.className = "results-group";

      const title = document.createElement("h3");
      title.className = "results-group-title";
      title.textContent = group.kanji
        ? `「${group.kanji}」を使った名前の候補`
        : "名前の候補";

      const count = document.createElement("p");
      count.className = "results-group-count";
      count.textContent = `${group.candidates.length}件`;

      const tableWrapper = document.createElement("div");
      tableWrapper.className = "table-wrapper";

      const table = document.createElement("table");
      table.className = "results-table";

      table.innerHTML = `
        <thead>
          <tr>
            <th></th>
            <th>名前</th>
            <th>総画数</th>
            <th>運勢</th>
          </tr>
        </thead>
        <tbody></tbody>
      `;

      const tbody = table.querySelector("tbody");

      group.candidates.forEach((c) => {
        const tr = document.createElement("tr");
        tr.className = "result-row";

        const arrowCell = document.createElement("td");
        arrowCell.className = "arrow-cell";
        arrowCell.innerHTML = `<span class="arrow-icon">▶</span>`;

        const nameCell = document.createElement("td");
        nameCell.textContent = `${c.familyName} ${c.givenName}`;

        const strokeCell = document.createElement("td");
        strokeCell.textContent = c.soukaku;

        const luckCell = document.createElement("td");
        luckCell.className = `luck-label luck-${c.totalLuck.rank}`;
        luckCell.textContent = c.totalLuck.label;

        tr.appendChild(arrowCell);
        tr.appendChild(nameCell);
        tr.appendChild(strokeCell);
        tr.appendChild(luckCell);

        const detailTr = document.createElement("tr");
        detailTr.className = "detail-row";
        detailTr.style.display = "none";

        const detailTd = document.createElement("td");
        detailTd.colSpan = 4;
        detailTd.innerHTML = `
          <div class="detail-inline">
            <h4>${c.familyName} ${c.givenName} の五格</h4>
            <ul>
              <li>天格… ${c.tenkaku}画（${c.tenLuck.label}）</li>
              <li>人格… ${c.jinkaku}画（${c.jinLuck.label}）</li>
              <li>地格… ${c.chikaku}画（${c.chiLuck.label}）</li>
              <li>外格… ${c.gaikaku}画（${c.gaiLuck.label}）</li>
              <li>総格… ${c.soukaku}画（${c.totalLuck.label}）</li>
            </ul>
          </div>
        `;
        detailTr.appendChild(detailTd);

        tr.addEventListener("click", () => {
          const icon = arrowCell.querySelector(".arrow-icon");
          const isOpen = detailTr.style.display === "table-row";
          detailTr.style.display = isOpen ? "none" : "table-row";
          icon.textContent = isOpen ? "▶" : "▼";
        });

        tbody.appendChild(tr);
        tbody.appendChild(detailTr);
      });

      tableWrapper.appendChild(table);
      section.appendChild(title);
      section.appendChild(count);
      section.appendChild(tableWrapper);
      resultsContainer.appendChild(section);
    });
  }
});
