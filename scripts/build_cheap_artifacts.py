#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import statistics
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CORPUS_PATH = ROOT / "corpus" / "cheap_corpus.md"
ARTIFACTS_DIR = ROOT / "artifacts"
ENTRY_SPLIT_RE = re.compile(r"^(\d{4})\s*$", flags=re.M)
INLINE_LABEL_RE = re.compile(r"^(?P<label>[^：:\n]{1,24})[：:]\s*")

CHEAP_PUSH_MOVES = {
    "反例對照",
    "數字換算",
    "荒謬類比",
    "邏輯反打",
    "風險收益比較",
}

REASONING_PATTERNS: dict[str, dict[str, Any]] = {
    "反例打臉": {
        "core_question": "對方的理由如果成立，是否會被更成熟、更強的反例直接打臉？",
        "evidence_types": ["對手說法", "反例", "品牌或案例對照", "邏輯反問"],
    },
    "荒謬成本換算": {
        "core_question": "這個要求如果真的落地，會燒掉多少時間、人力、金錢或行政成本？",
        "evidence_types": ["數字", "時間", "人力估算", "成本", "流程細節"],
    },
    "誘因白話拆解": {
        "core_question": "表面說法背後，真正驅動這件事的是誰的誘因、風險與算計？",
        "evidence_types": ["原始說法", "角色關係", "權責", "利益結構", "白話翻譯"],
    },
    "歷史國際映射": {
        "core_question": "歷史或國外是否有更清楚的對照案例，可以校正讀者直覺？",
        "evidence_types": ["歷史事件", "國外案例", "制度差異", "時間脈絡"],
    },
    "情境推演判斷": {
        "core_question": "如果把角色習性與現實限制放進去，最可能發生的劇本是哪個？",
        "evidence_types": ["角色習性", "前例", "版本分支", "情境限制"],
    },
    "風險收益審判": {
        "core_question": "如果這個指控或行動是真的，對當事人的風險與收益比例合理嗎？",
        "evidence_types": ["風險", "收益", "角色地位", "代價", "行動規模"],
    },
    "抽象議題翻成生活常識": {
        "core_question": "如果把抽象政策或制度翻成日常語言，哪裡一看就不對勁？",
        "evidence_types": ["制度機制", "日常場景", "生活化類比", "使用者處境"],
    },
    "先定調再追責": {
        "core_question": "這件事最該先被怎麼定調，然後責任應該落到誰身上？",
        "evidence_types": ["事件摘要", "責任角色", "價值判斷", "情緒語言"],
    },
}

ROUTES: dict[str, dict[str, Any]] = {
    "先拋說法再反例拆解": {
        "rhythm": "Hook -> 爭議說法 -> 反例連發 -> 邏輯反打 -> 判決",
        "must_include_moves": ["明確定調", "引用對手說法", "反例對照", "邏輯反打"],
        "opening_move": "爭議說法開場",
    },
    "先摘要再翻成白話": {
        "rhythm": "Hook -> 新聞摘要 -> 白話翻譯 -> 誘因拆解 -> 反諷收尾",
        "must_include_moves": ["新聞摘要", "白話翻譯", "動機拆解", "邏輯反打", "收尾反諷"],
        "opening_move": "摘要開場",
    },
    "先算帳再放大荒謬": {
        "rhythm": "Hook -> 關鍵數字 -> 成本換算 -> 畫面化類比 -> 判決",
        "must_include_moves": ["數字換算", "流程展開", "荒謬類比", "結論"],
        "opening_move": "數字開場",
    },
    "先拉外部案例再映射當下": {
        "rhythm": "Hook -> 歷史/國外案例 -> 對照差異 -> 拉回本案 -> 判決",
        "must_include_moves": ["歷史映射", "國外對照", "反例對照", "回扣當下", "結論"],
        "opening_move": "外部案例開場",
    },
    "先列劇本再收斂判斷": {
        "rhythm": "Hook -> 多版本推演 -> 劇本篩選 -> 最可能結果 -> 補刀",
        "must_include_moves": ["情境推演", "版本比較", "機率判斷", "邏輯反打", "收尾補刀"],
        "opening_move": "劇本開場",
    },
    "先定調再往上追責": {
        "rhythm": "Hook -> 情緒定調 -> 事件責任 -> 上層結構/政治責任 -> 結尾判決",
        "must_include_moves": ["明確定調", "責任指派", "結構上升", "邏輯反打", "道德判決"],
        "opening_move": "定調開場",
    },
    "先驗證可置信性再下判決": {
        "rhythm": "Hook -> 指控摘要 -> 風險收益比較 -> 常識檢驗 -> 判決",
        "must_include_moves": ["指控摘要", "風險收益比較", "常識檢驗", "結論"],
        "opening_move": "可信度檢驗開場",
    },
}

TOPICS: dict[str, dict[str, Any]] = {
    "topic/design_branding": {
        "display_name": "設計品牌",
        "definition": "LOGO、字體、品牌改版、識別系統、文化記憶相關題材。",
        "common_materials": ["對手說法", "品牌對照", "歷史沿革", "改版成本"],
    },
    "topic/traffic_governance": {
        "display_name": "交通治理",
        "definition": "道路設計、行人安全、交通工程、駕駛責任與設施治理。",
        "common_materials": ["道路設計機制", "事故場景", "責任歸屬", "外部制度對照"],
    },
    "topic/partisan_attack": {
        "display_name": "政黨攻防",
        "definition": "甩鍋、雙標、側翼話術、立場翻轉、政治標籤與攻防。",
        "common_materials": ["原話", "時間序列", "雙標反例", "風向操作材料"],
    },
    "topic/public_governance": {
        "display_name": "公共治理",
        "definition": "政策設計、法規、行政流程、治理邏輯與預算執行。",
        "common_materials": ["政策原文", "流程", "成本數字", "官方說法"],
    },
    "topic/international_security": {
        "display_name": "國際安全",
        "definition": "外交、戰爭、領導人行為、地緣政治與安全威脅判讀。",
        "common_materials": ["歷史前例", "國外案例", "角色習性", "外交限制"],
    },
    "topic/tech_media_ai": {
        "display_name": "科技媒體AI",
        "definition": "AI 工具、平台風向、查核、截圖對帳與科技迷因。",
        "common_materials": ["截圖", "查核材料", "工具輸出", "平台語境"],
    },
    "topic/lifestyle_consumer": {
        "display_name": "生活消費",
        "definition": "旅遊、飲食、抽菸、價格、生活體驗與文化習慣比較。",
        "common_materials": ["價格", "生活場景", "體驗差異", "國外案例"],
    },
    "topic/history_counterfactual": {
        "display_name": "歷史反事實",
        "definition": "歷史人物評價、史觀修正、正史與小說落差、反事實推演。",
        "common_materials": ["史料", "正史對照", "反事實條件", "現代類比"],
    },
}

TOPIC_MATCHERS: list[tuple[str, str, list[str]]] = [
    ("topic/design_branding", r"台電|中油|于右任|聶永真|LOGO|logo|字體|識別|市旗|府徽|品牌", ["logo_or_branding"]),
    ("topic/traffic_governance", r"庇護島|人行道|斑馬線|行人|路肩|違停|車禍|駕駛|機車道", ["traffic_scene"]),
    ("topic/partisan_attack", r"民進黨|國民黨|立委|大內宣|甩鍋|側翼|青鳥|小草|罷免", ["partisan_attack"]),
    ("topic/public_governance", r"補助|修法|NCC|勞動部|政府|政策|市府|立法院|法規|預算", ["policy_governance"]),
    ("topic/international_security", r"烏克蘭|俄羅斯|川普|伊朗|北約|韓國|尹錫悅|美國|德國|捷克|外交|軍演", ["international_security"]),
    ("topic/tech_media_ai", r"AI|ChatGPT|Gemini|Grok|假訊息|查核|梗圖|截圖|threads|Thread", ["tech_media"]),
    ("topic/lifestyle_consumer", r"國旅|公園|日本自駕|瘦瘦針|咖啡|按摩|抽菸|菸蒂|菜單|旅遊", ["lifestyle_consumer"]),
    ("topic/history_counterfactual", r"二戰|正史|三國|黃忠|魯肅|曹真|蘇軾|諾貝爾文學獎|演義|如果二戰", ["history_counterfactual"]),
]

TOPIC_CLUSTER_RULES: list[tuple[str, str]] = [
    ("cluster/design_branding", r"台電|中油|于右任|聶永真|台灣電力公司|LOGO|logo|鼎泰豐"),
    ("cluster/traffic_governance", r"庇護島|人行道|斑馬線|行人|路肩|違停|車禍|高雄汽車撞行人"),
    ("cluster/partisan_attack", r"民進黨|國民黨|立委|大內宣|甩鍋|側翼|青鳥|小草"),
    ("cluster/public_governance", r"補助|修法|NCC|勞動部|政府|政策|市府|立法院"),
    ("cluster/international_security", r"烏克蘭|俄羅斯|川普|伊朗|北約|韓國|美國|德國|捷克"),
    ("cluster/history_counterfactual", r"二戰|正史|三國|黃忠|魯肅|曹真|蘇軾|諾貝爾文學獎"),
    ("cluster/lifestyle_consumer", r"國旅|公園|日本自駕|瘦瘦針|咖啡|按摩|抽菸|菸蒂"),
    ("cluster/tech_media_ai", r"AI|ChatGPT|Gemini|Grok|台積電|梗圖|假訊息|查核"),
]


def normalize_text(text: str) -> str:
    text = text.replace("\u200e", "")
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def load_entries() -> list[dict[str, Any]]:
    text = CORPUS_PATH.read_text()
    parts = ENTRY_SPLIT_RE.split(text)
    entries: list[dict[str, Any]] = []
    for i in range(1, len(parts), 2):
        entry_id = parts[i]
        raw_text = parts[i + 1].strip()
        clean_text = normalize_text(raw_text)
        entries.append(
            {
                "entry_id": entry_id,
                "source_family": "cheap_corpus_markdown",
                "char_count": len(clean_text),
                "raw_text": raw_text,
                "clean_text": clean_text,
                "low_confidence_flag": raw_text.startswith("這張相片來自一則貼文"),
            }
        )
    return entries


def section_lines(text: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.strip()]


def first_hook(text: str) -> str:
    lines = section_lines(text)
    return lines[0] if lines else ""


def clean_hook(text: str) -> str:
    hook = first_hook(text).strip()
    return INLINE_LABEL_RE.sub("", hook).strip()


def has_any(text: str, patterns: list[str]) -> bool:
    return any(pattern in text for pattern in patterns)


def count_numbers(text: str) -> int:
    return len(re.findall(r"\d+(?:[.,]\d+)?", text))


def infer_topic_cluster(text: str) -> str:
    if text.startswith("這張相片來自一則貼文"):
        return "cluster/unavailable_placeholder"
    for cluster_id, pattern in TOPIC_CLUSTER_RULES:
        if re.search(pattern, text, flags=re.I):
            return cluster_id
    hook = clean_hook(text)
    hook = re.sub(r"[^\w\u4e00-\u9fff]+", "_", hook)[:32].strip("_")
    return f"cluster/{hook or 'uncategorized'}"


def infer_topic_tags(text: str, topic_cluster_id: str) -> tuple[list[str], list[str]]:
    topic_tags: list[str] = []
    topic_signals: list[str] = []
    for topic_id, pattern, signals in TOPIC_MATCHERS:
        if re.search(pattern, text, flags=re.I):
            topic_tags.append(topic_id)
            topic_signals.extend(signals)
    if topic_tags:
        deduped_tags = list(dict.fromkeys(topic_tags))
        deduped_signals = list(dict.fromkeys(topic_signals))
        return deduped_tags, deduped_signals

    cluster_fallback = {
        "cluster/design_branding": "topic/design_branding",
        "cluster/traffic_governance": "topic/traffic_governance",
        "cluster/partisan_attack": "topic/partisan_attack",
        "cluster/public_governance": "topic/public_governance",
        "cluster/international_security": "topic/international_security",
        "cluster/tech_media_ai": "topic/tech_media_ai",
        "cluster/lifestyle_consumer": "topic/lifestyle_consumer",
        "cluster/history_counterfactual": "topic/history_counterfactual",
    }
    fallback = cluster_fallback.get(topic_cluster_id, "topic/public_governance")
    return [fallback], ["cluster_fallback"]


def infer_reasoning_pattern(entry: dict[str, Any]) -> str:
    text = entry["clean_text"]
    numbers = count_numbers(text)
    plain_language = has_any(text, ["翻成白話", "簡單說", "意思是", "所以邏輯是"])
    scenario = has_any(text, ["版本一", "版本二", "版本三", "如果", "會怎樣", "高機率", "最可能"])
    strong_scenario = has_any(text, ["版本一", "版本二", "版本三", "高機率", "最可能", "能走多遠", "如果二戰", "如果高市大贏", "如果高市大敗"])
    history = has_any(text, ["正史", "歷史上", "二戰", "日本", "美國", "越南", "烏克蘭", "韓國", "德國", "捷克", "蘇軾"])
    counterexample = has_any(text, ["反觀", "先不說", "還有同樣", "如果", "怎麼不", "哪", "表示："])
    risk_reward = has_any(text, ["風險", "收益", "核爆", "值得", "代價"])
    incentives = has_any(text, ["大內宣", "甩鍋", "護航", "凝聚共識", "暫緩", "沒有關係", "其實", "因為"])
    moral = has_any(text, ["可悲", "爛", "豈有此理", "離譜", "噁", "可惡", "瘋子"])
    public_mechanics = has_any(text, ["人行道", "庇護島", "檢查", "逐顆", "政策", "制度", "工程"])

    if plain_language and incentives:
        return "誘因白話拆解"
    if strong_scenario:
        return "情境推演判斷"
    if numbers >= 4 and has_any(text, ["多少錢", "費用", "薪資", "工作", "公噸", "逐顆", "成本"]):
        return "荒謬成本換算"
    if history and has_any(text, ["反觀", "歷史", "正史", "日本", "美國", "越南", "烏克蘭", "韓國"]):
        return "歷史國際映射"
    if risk_reward:
        return "風險收益審判"
    if scenario:
        return "情境推演判斷"
    if counterexample:
        return "反例打臉"
    if public_mechanics or plain_language:
        return "抽象議題翻成生活常識"
    if moral or entry["char_count"] <= 220:
        return "先定調再追責"
    return "抽象議題翻成生活常識"


def infer_primary_route(text: str, reasoning_pattern: str) -> str:
    mapping = {
        "反例打臉": "先拋說法再反例拆解",
        "荒謬成本換算": "先算帳再放大荒謬",
        "誘因白話拆解": "先摘要再翻成白話",
        "歷史國際映射": "先拉外部案例再映射當下",
        "情境推演判斷": "先列劇本再收斂判斷",
        "風險收益審判": "先驗證可置信性再下判決",
        "先定調再追責": "先定調再往上追責",
        "抽象議題翻成生活常識": "先摘要再翻成白話",
    }
    return mapping.get(reasoning_pattern, "先摘要再翻成白話")


def infer_secondary_route(text: str, primary_route: str) -> str | None:
    if primary_route != "先算帳再放大荒謬" and count_numbers(text) >= 4:
        return "先算帳再放大荒謬"
    if primary_route != "先摘要再翻成白話" and has_any(text, ["翻成白話", "簡單說", "意思是"]):
        return "先摘要再翻成白話"
    if primary_route != "先拉外部案例再映射當下" and has_any(text, ["日本", "美國", "歷史上", "正史", "反觀"]):
        return "先拉外部案例再映射當下"
    return None


def infer_post_type(entry: dict[str, Any], reasoning_pattern: str) -> str:
    paragraph_count = len(section_lines(entry["clean_text"]))
    char_count = entry["char_count"]
    if char_count <= 180:
        return "短打定調"
    if reasoning_pattern == "荒謬成本換算":
        return "數字算帳文"
    if reasoning_pattern == "情境推演判斷":
        return "情境推演文"
    if reasoning_pattern == "歷史國際映射" and char_count >= 500:
        return "歷史映射長文"
    if paragraph_count >= 5:
        return "多段拆解"
    return "單段評論"


def infer_argument_moves(text: str, reasoning_pattern: str) -> list[str]:
    moves: list[str] = ["明確定調"]
    if has_any(text, ["說：", "原話", "根據", "新聞", "報導"]):
        moves.append("引用對手說法")
    if has_any(text, ["反觀", "先不說", "還有同樣", "例子", "如果台電的字叫難印"]):
        moves.append("反例對照")
    if count_numbers(text) >= 3:
        moves.append("數字換算")
    if has_any(text, ["翻成白話", "簡單說", "意思是", "所以邏輯是"]):
        moves.append("白話翻譯")
    if has_any(text, ["怎麼", "那重要嗎", "如果", "說不過去", "邏輯是"]):
        moves.append("邏輯反打")
    if has_any(text, ["因為", "其實", "甩鍋", "護航", "大內宣", "想要"]):
        moves.append("動機拆解")
    if has_any(text, ["日本", "美國", "德國", "越南", "歷史上", "正史", "二戰", "韓國"]):
        if has_any(text, ["日本", "美國", "德國", "越南", "韓國"]):
            moves.append("國外對照")
        if has_any(text, ["歷史上", "正史", "二戰"]):
            moves.append("歷史映射")
    if has_any(text, ["風險", "收益", "代價"]):
        moves.append("風險收益比較")
    if has_any(text, ["就像", "像", "想像一下", "婚禮", "地獄"]):
        moves.append("荒謬類比")
    if has_any(text, ["版本一", "版本二", "如果", "會怎樣"]):
        moves.append("情境推演")
    if reasoning_pattern == "先定調再追責":
        moves.append("道德判決")
    moves.append("收尾反諷")
    return list(dict.fromkeys(moves))


def infer_required_evidence_types(reasoning_pattern: str, argument_moves: list[str]) -> list[str]:
    evidence = list(REASONING_PATTERNS[reasoning_pattern]["evidence_types"])
    if "數字換算" in argument_moves and "數字" not in evidence:
        evidence.append("數字")
    if "國外對照" in argument_moves and "國外案例" not in evidence:
        evidence.append("國外案例")
    if "歷史映射" in argument_moves and "歷史事件" not in evidence:
        evidence.append("歷史事件")
    if "情境推演" in argument_moves and "版本分支" not in evidence:
        evidence.append("版本分支")
    return evidence


def infer_angle_statement(text: str, reasoning_pattern: str) -> str:
    hook = clean_hook(text)[:28] or "這個事件"
    templates = {
        "反例打臉": f"把「{hook}」當成待驗證說法，透過更強反例證明原本理由站不住腳。",
        "荒謬成本換算": f"把「{hook}」換算成人力、時間或金額，讓荒謬成本變得可感。",
        "誘因白話拆解": f"把「{hook}」翻成白話，指出表面說法背後真正運作的是誰的誘因與風險。",
        "歷史國際映射": f"用歷史或國外案例重新校正「{hook}」的判斷標尺。",
        "情境推演判斷": f"把「{hook}」拆成多個劇本，挑出最符合角色習性與現實限制的版本。",
        "風險收益審判": f"檢驗「{hook}」這個敘事是否符合行動者的風險收益比。",
        "抽象議題翻成生活常識": f"把「{hook}」翻成日常語言，讓制度問題不再停留在抽象層次。",
        "先定調再追責": f"先替「{hook}」定調，再把責任往真正該負責的角色身上推上去。",
    }
    return templates[reasoning_pattern]


def infer_hook_type(text: str) -> str:
    hook = first_hook(text)
    if count_numbers(hook) >= 1:
        return "number_hook"
    if "新聞" in hook or "說" in hook:
        return "claim_hook"
    if "？" in hook or "?" in hook:
        return "question_hook"
    return "angle_hook"


def infer_claim_target(text: str, topic_tags: list[str]) -> str:
    if "topic/partisan_attack" in topic_tags:
        return "政黨或政治人物"
    if "topic/public_governance" in topic_tags:
        return "政府部門或制度"
    if "topic/design_branding" in topic_tags:
        return "品牌或設計決策者"
    if "topic/traffic_governance" in topic_tags:
        return "交通主管機關或工程設計"
    if "topic/international_security" in topic_tags:
        return "國際領導人或外交策略"
    if "topic/tech_media_ai" in topic_tags:
        return "媒體、平台或AI工具"
    if "topic/lifestyle_consumer" in topic_tags:
        return "業者、消費習慣或生活文化"
    if "topic/history_counterfactual" in topic_tags:
        return "歷史人物、史觀或既定印象"
    return "事件核心對象"


def infer_evidence_shape(text: str) -> list[str]:
    shapes: list[str] = []
    if count_numbers(text) >= 2:
        shapes.append("numbers")
    if has_any(text, ["說：", "原話", "根據", "新聞", "報導"]):
        shapes.append("quoted_statement")
    if has_any(text, ["反觀", "先不說", "還有同樣", "表示："]):
        shapes.append("counterexample")
    if has_any(text, ["歷史上", "正史", "二戰"]):
        shapes.append("historical_case")
    if has_any(text, ["日本", "美國", "德國", "越南", "韓國", "伊朗"]):
        shapes.append("international_case")
    if has_any(text, ["版本一", "版本二", "如果", "會怎樣", "高機率"]):
        shapes.append("scenario_branches")
    if has_any(text, ["人行道", "房租", "學費", "便利商店", "生活", "辦公室"]):
        shapes.append("daily_scene")
    deduped = list(dict.fromkeys(shapes))
    if not deduped:
        deduped.append("plain_claim")
    return deduped


def infer_cheap_push_moves(
    argument_moves: list[str],
    reasoning_pattern: str,
    evidence_shape: list[str],
) -> list[str]:
    cheap_push_moves = [move for move in argument_moves if move in CHEAP_PUSH_MOVES]

    if "國外對照" in argument_moves or "歷史映射" in argument_moves or "counterexample" in evidence_shape:
        cheap_push_moves.append("反例對照")
    if reasoning_pattern == "反例打臉":
        cheap_push_moves.append("反例對照")
    if "白話翻譯" in argument_moves or "動機拆解" in argument_moves:
        cheap_push_moves.append("邏輯反打")
    if reasoning_pattern in {"先定調再追責", "抽象議題翻成生活常識", "情境推演判斷"}:
        cheap_push_moves.append("邏輯反打")
    if reasoning_pattern == "歷史國際映射":
        cheap_push_moves.append("反例對照")

    return list(dict.fromkeys(cheap_push_moves))


def infer_opening_move(route_id: str) -> str:
    return ROUTES[route_id]["opening_move"]


def infer_rhythm_pattern(route_id: str) -> str:
    return ROUTES[route_id]["rhythm"]


def infer_closing_style(text: str) -> str:
    ending = "\n".join(section_lines(text)[-3:])
    if has_any(ending, ["希望", "應該", "照抄", "要怎麼做"]):
        return "制度呼籲"
    if has_any(ending, ["簡單說", "翻成白話", "其實"]):
        return "白話判決"
    if has_any(ending, ["可悲", "爛", "豈有此理", "瘋子"]):
        return "道德譴責"
    if "？" in ending or "?" in ending:
        return "反問補刀"
    return "反諷收尾"


def annotate(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    annotated: list[dict[str, Any]] = []
    for entry in entries:
        text = entry["clean_text"]
        topic_cluster_id = infer_topic_cluster(text)
        topic_tags, topic_signals = infer_topic_tags(text, topic_cluster_id)
        reasoning_pattern = infer_reasoning_pattern(entry)
        primary_route = infer_primary_route(text, reasoning_pattern)
        secondary_route = infer_secondary_route(text, primary_route)
        argument_moves = infer_argument_moves(text, reasoning_pattern)
        evidence_shape = infer_evidence_shape(text)
        cheap_push_moves = infer_cheap_push_moves(argument_moves, reasoning_pattern, evidence_shape)
        annotated.append(
            {
                **entry,
                "topic_cluster_id": topic_cluster_id,
                "topic_tags": topic_tags,
                "topic_signals": topic_signals,
                "post_type": infer_post_type(entry, reasoning_pattern),
                "reasoning_pattern": reasoning_pattern,
                "thinking_pattern": reasoning_pattern,
                "primary_route": primary_route,
                "route_id": primary_route,
                "secondary_route": secondary_route,
                "angle_statement": infer_angle_statement(text, reasoning_pattern),
                "argument_moves": argument_moves,
                "cheap_push_moves": cheap_push_moves,
                "required_evidence_types": infer_required_evidence_types(reasoning_pattern, argument_moves),
                "hook_type": infer_hook_type(text),
                "claim_target": infer_claim_target(text, topic_tags),
                "evidence_shape": evidence_shape,
                "opening_move": infer_opening_move(primary_route),
                "rhythm_pattern": infer_rhythm_pattern(primary_route),
                "closing_style": infer_closing_style(text),
            }
        )
    return annotated


def build_summary(entries: list[dict[str, Any]]) -> dict[str, Any]:
    reasoning_counts = Counter(entry["reasoning_pattern"] for entry in entries)
    route_counts = Counter(entry["primary_route"] for entry in entries)
    cluster_counts = Counter(entry["topic_cluster_id"] for entry in entries)
    topic_counts = Counter(tag for entry in entries for tag in entry["topic_tags"])
    high_confidence = [entry for entry in entries if not entry["low_confidence_flag"]]
    char_counts = [entry["char_count"] for entry in entries]
    topic_count_dist = Counter(len(entry["topic_tags"]) for entry in entries)
    return {
        "source_path": str(CORPUS_PATH.relative_to(ROOT)),
        "entry_count": len(entries),
        "high_confidence_count": len(high_confidence),
        "low_confidence_count": len(entries) - len(high_confidence),
        "char_count": {
            "min": min(char_counts),
            "median": statistics.median(char_counts),
            "max": max(char_counts),
        },
        "topic_count_distribution": dict(sorted(topic_count_dist.items())),
        "reasoning_pattern_distribution": reasoning_counts.most_common(),
        "route_distribution": route_counts.most_common(),
        "topic_distribution": topic_counts.most_common(),
        "topic_clusters": cluster_counts.most_common(15),
    }


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_analysis_markdown(summary: dict[str, Any]) -> None:
    reasoning_lines = "\n".join(
        f"- `{name}`: {count} 篇" for name, count in summary["reasoning_pattern_distribution"]
    )
    route_lines = "\n".join(
        f"- `{name}`: {count} 篇" for name, count in summary["route_distribution"]
    )
    topic_lines = "\n".join(
        f"- `{name}`: {count} 篇" for name, count in summary["topic_distribution"]
    )
    cluster_lines = "\n".join(
        f"- `{name}`: {count} 篇" for name, count in summary["topic_clusters"][:10]
    )
    md = f"""# Cheap Corpus Analysis

## Snapshot
- 語料檔：`{summary["source_path"]}`
- 總篇數：`{summary["entry_count"]}`
- 高信心樣本：`{summary["high_confidence_count"]}`
- 低信心樣本：`{summary["low_confidence_count"]}`
- 字數範圍：`{summary["char_count"]["min"]}` ~ `{summary["char_count"]["max"]}`
- 字數中位數：`{summary["char_count"]["median"]}`

## Reasoning-First View
- 主幹不是題材分類，而是先看思考模式，再看鋪文 route，最後用 topic tags 做題材適配。
- 單篇 topic 數量分布：`{summary["topic_count_distribution"]}`

## Reasoning Patterns
{reasoning_lines}

## Routes
{route_lines}

## Topics
{topic_lines}

## Topic Clusters
{cluster_lines}
"""
    (ARTIFACTS_DIR / "cheap_corpus_analysis.md").write_text(md)


def main() -> None:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    entries = load_entries()
    annotated = annotate(entries)
    summary = build_summary(annotated)
    write_jsonl(ARTIFACTS_DIR / "cheap_corpus_records.jsonl", annotated)
    write_json(
        ARTIFACTS_DIR / "cheap_taxonomy.json",
        {
            "reasoning_patterns": REASONING_PATTERNS,
            "routes": ROUTES,
            "topics": TOPICS,
        },
    )
    write_json(ARTIFACTS_DIR / "cheap_corpus_summary.json", summary)
    write_analysis_markdown(summary)


if __name__ == "__main__":
    main()
