#!/usr/bin/env python3
"""
台湾華語の読み（ピンイン）用の小さな辞書 JSON を作る。
Build a small pinyin dictionary (JSON) for Taiwanese Mandarin.

使い方 / Usage:
    python3 -I tools/make_pinyin_json.py <cedict_1_0_ts_utf-8_mdbg.txt> <Unihan_Readings.txt> Pinyin.json

元データ / Sources:
    - CC-CEDICT  https://www.mdbg.net/chinese/dictionary?page=cc-cedict
      CC BY-SA 4.0。作った JSON も CC BY-SA 4.0 になる。
    - Unihan     https://www.unicode.org/Public/UCD/latest/ucd/Unihan.zip
      Unicode License V3。

作る JSON:
    {
      "sources": {...},                        元データの出典・版・日付
      "chars": { "乾": "gān", ... },           1文字の標準の読み（台湾で好まれる読み）
      "words": { "乾坤": "qián kūn", ... },    2文字以上の単語の読み（1文字ずつの読みと違うものだけ）
      "multi": { "乾": ["gān", "qián"], ... }  読みが複数ある字（先頭が標準の読み）
    }

決め方:
    1. 1文字の読み：Unihan の kMandarin。値が2つあるときは2つ目（台湾で好まれる読み）。
       kMandarin がない字は、CC-CEDICT の1文字の項目の最初の読み。
    2. 単語の読み：CC-CEDICT の繁体字の見出し（2文字以上）。
       - 固有名詞（大文字で始まる読み）や「variant of」は使わない。
       - 同じ見出しが複数あるときは、説明（意味）の数がいちばん多いもの。
         同じ数なら辞書で先に出てくるもの（例：便宜は pián yi、好吃は hǎo chī）。
       - 「Taiwan pr. [...]」が単独の説明として書かれていれば、その読みをそのまま使う
         （例：垃圾 → lè sè）。
       - それ以外は、軽声（声調のない音節）を台湾式に直す：その字の1文字の読みに置き換える
         （例：謝謝 xiè xie → xiè xiè、東西 dōng xi → dōng xī）。
         ただし、台湾でも軽く読む助詞・接尾語（NEUTRAL_KEEP）は軽声のまま。
       - 1文字ずつの読みと同じになる単語は、JSON を小さくするため入れない。
    3. 読みが複数ある字：Unihan の kMandarin と kHanyuPinyin の読みのうち、
       CC-CEDICT の見出しで実際にその字の読みとして使われているものが2つ以上ある字。
       軽声だけの読み（頭の tou など、同じ音で声調のある読みもあるもの）は数えない。
"""

import datetime
import json
import re
import sys
import unicodedata

# 台湾でも軽声のまま読む助詞・接尾語
# 的 了 嗎 呢 吧 啊 著 們 ＋ 文末の助詞（麼 呀 啦 嘛 喔 哦 囉）＋ 名詞の接尾語の 子（桌子・孩子）
# ＋ r 化の 兒（場兒 chǎng r。ér にすると別の音節になってしまうため）
NEUTRAL_KEEP = set("的了嗎呢吧啊著們麼呀啦嘛喔哦囉子兒")

TONE_MARKS = {
    "a": "āáǎàa", "e": "ēéěèe", "i": "īíǐìi",
    "o": "ōóǒòo", "u": "ūúǔùu", "ü": "ǖǘǚǜü",
}


def numbered_to_marked(syllable: str) -> str:
    """'gan1' → 'gān'、'lu:4' → 'lǜ'、'xie5' → 'xie'"""
    s = syllable.lower().replace("u:", "ü").replace("v", "ü")
    m = re.fullmatch(r"([a-zü]+)([1-5])", s)
    if not m:
        return s
    body, tone = m.group(1), int(m.group(2))
    if tone == 5:
        return body
    # 声調記号を付ける母音：a か e があればそれ、ou なら o、それ以外は最後の母音
    if "a" in body:
        index = body.index("a")
    elif "e" in body:
        index = body.index("e")
    elif "ou" in body:
        index = body.index("o")
    else:
        index = max(body.rfind(v) for v in "iouü")
        if index < 0:
            return body  # 母音なし（m, ng など）
    vowel = body[index]
    return body[:index] + TONE_MARKS[vowel][tone - 1] + body[index + 1:]


def is_neutral(syllable: str) -> bool:
    """CC-CEDICT の番号つきピンインで軽声（5）か"""
    return syllable.endswith("5")


def strip(s: str) -> str:
    """声調記号を外す"""
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def is_han(ch: str) -> bool:
    name = unicodedata.name(ch, "")
    return "CJK UNIFIED IDEOGRAPH" in name or "CJK COMPATIBILITY IDEOGRAPH" in name


def read_unihan(path):
    """kMandarin と kHanyuPinyin、ファイルの版と日付を読む"""
    mandarin, hanyu = {}, {}
    meta = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("#"):
                m = re.match(r"# Date: (\S+)", line)
                if m:
                    meta["date"] = m.group(1)
                m = re.match(r"# Unicode Version (\S+)", line)
                if m:
                    meta["version"] = m.group(1)
                continue
            if not line.strip():
                continue
            code, field, value = line.rstrip("\n").split("\t", 2)
            ch = chr(int(code[2:], 16))
            if field == "kMandarin":
                mandarin[ch] = value.split()
            elif field == "kHanyuPinyin":
                readings = []
                for part in value.split():
                    readings += part.split(":", 1)[1].split(",")
                hanyu[ch] = readings
    return mandarin, hanyu, meta


ENTRY = re.compile(r"^(\S+) (\S+) \[([^\]]*)\] /(.*)/$")
TAIWAN = re.compile(r"^Taiwan pr\. \[([^\]]+)\]$")


def read_cedict(path):
    """繁体字 → [(番号つき読みの音節リスト, 説明のリスト)]、ファイルの日付と項目数"""
    entries = {}
    meta = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.startswith("#"):
                m = re.match(r"#! (date|entries)=(\S+)", line)
                if m:
                    meta[m.group(1)] = m.group(2)
                continue
            m = ENTRY.match(line.strip())
            if not m:
                continue
            trad, _simp, pinyin, defs = m.groups()
            entries.setdefault(trad, []).append((pinyin.split(), defs.split("/")))
    return entries, meta


def main():
    cedict_path, unihan_path, out_path = sys.argv[1:4]
    mandarin, hanyu, unihan_meta = read_unihan(unihan_path)
    cedict, cedict_meta = read_cedict(cedict_path)

    # 1. 1文字の標準の読み
    chars = {}
    for ch, values in mandarin.items():
        chars[ch] = values[1] if len(values) > 1 else values[0]
    for trad, items in cedict.items():
        if len(trad) == 1 and is_han(trad) and trad not in chars:
            for syllables, _ in items:
                if len(syllables) == 1 and not syllables[0][0].isupper():
                    chars[trad] = numbered_to_marked(syllables[0])
                    break

    # CC-CEDICT の繁体字に出てくる字
    used_chars = {ch for trad in cedict for ch in trad if is_han(ch)}

    # 2. 単語の読み
    words = {}
    taiwan_count = 0
    neutral_changed = 0
    for trad, items in cedict.items():
        if len(trad) < 2 or not all(is_han(ch) for ch in trad):
            continue
        candidates = []
        for syllables, defs in items:
            if len(syllables) != len(trad):
                continue  # 字と音節が1対1でないもの（記号入りなど）は使わない
            if syllables[0][0].isupper():
                continue  # 固有名詞
            if any(d.startswith(("variant of", "old variant of", "erhua variant of")) for d in defs):
                continue
            taiwan = None
            for d in defs:
                t = TAIWAN.match(d)
                if t and len(t.group(1).split()) == len(trad):
                    taiwan = t.group(1).split()
                    break
            meanings = [d for d in defs if d and not d.startswith(("CL:", "Taiwan pr."))]
            candidates.append((syllables, taiwan, len(meanings)))
        if not candidates:
            continue

        # 説明の数がいちばん多いもの（同点なら先に出てきたもの）
        syllables, taiwan, _ = max(candidates, key=lambda c: c[2])
        if taiwan:
            # 「Taiwan pr.」の読みはそのまま使う
            marked = [numbered_to_marked(s) for s in taiwan]
            taiwan_count += 1
        else:
            marked = []
            changed = False
            for ch, syl in zip(trad, syllables):
                if is_neutral(syl) and ch not in NEUTRAL_KEEP and ch in chars:
                    # 軽声を台湾式に：その字の1文字の読みにする
                    marked.append(chars[ch])
                    changed = changed or chars[ch] != numbered_to_marked(syl)
                else:
                    marked.append(numbered_to_marked(syl))
            neutral_changed += changed

        default = [chars.get(ch, "") for ch in trad]
        if marked != default:
            words[trad] = " ".join(marked)

    # 3. 読みが複数ある字
    # CC-CEDICT の見出し（固有名詞・variant を除く）で、各字が実際にどう読まれているか
    used_readings = {}
    for trad, items in cedict.items():
        for syllables, defs in items:
            if len(syllables) != len(trad) or syllables[0][0].isupper():
                continue
            if any(d.startswith(("variant of", "old variant of")) for d in defs):
                continue
            for ch, syl in zip(trad, syllables):
                if is_han(ch):
                    used_readings.setdefault(ch, set()).add(numbered_to_marked(syl))

    multi = {}
    for ch in sorted(used_chars):
        readings = []
        for r in mandarin.get(ch, []) + hanyu.get(ch, []):
            if r not in readings and r in used_readings.get(ch, set()):
                readings.append(r)
        # 軽声だけの読み（声調なし）は、同じ音で声調のある読みがあれば数えない
        readings = [r for r in readings
                    if not (strip(r) == r and any(strip(o) == r and o != r for o in readings))]
        if len(readings) >= 2:
            # 標準の読みを先頭に
            first = chars.get(ch)
            if first in readings:
                readings.remove(first)
                readings.insert(0, first)
            multi[ch] = readings

    used_default = {ch: r for ch, r in chars.items() if ch in used_chars}
    data = {
        "sources": {
            "cedict": {
                "name": "CC-CEDICT",
                "publisher": "MDBG",
                "url": "https://www.mdbg.net/chinese/dictionary?page=cc-cedict",
                "license": "CC BY-SA 4.0",
                "licenseURL": "https://creativecommons.org/licenses/by-sa/4.0/",
                "date": cedict_meta.get("date", ""),
                "entries": cedict_meta.get("entries", ""),
            },
            "unihan": {
                "name": "Unihan Database",
                "publisher": "Unicode, Inc.",
                "url": "https://www.unicode.org/charts/unihan.html",
                "license": "Unicode License V3",
                "licenseURL": "https://www.unicode.org/license.txt",
                "version": unihan_meta.get("version", ""),
                "date": unihan_meta.get("date", ""),
            },
            "license": "CC BY-SA 4.0 (this file). Portions derived from Unihan are also subject to the Unicode License V3.",
            "generated": datetime.date.today().isoformat(),
        },
        "chars": used_default,
        "words": words,
        "multi": multi,
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
    print(f"chars={len(used_default)} words={len(words)} "
          f"(Taiwan pr. {taiwan_count}, neutral tone changed {neutral_changed}) multi={len(multi)}")
    print(f"CC-CEDICT date={cedict_meta.get('date')} entries={cedict_meta.get('entries')} / "
          f"Unihan {unihan_meta.get('version')} date={unihan_meta.get('date')}")


if __name__ == "__main__":
    main()
