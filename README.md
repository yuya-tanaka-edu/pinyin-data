# pinyin-data

台湾華語（台湾で使われている中国語・繁体字）の読み（ピンイン）を決めるための、小さな辞書データです。
CC-CEDICT と Unihan を加工して作っています。

A small dictionary for producing pinyin readings of Taiwanese Mandarin (Traditional Chinese),
adapted from CC-CEDICT and the Unihan Database.

[日本語](#日本語) ・ [English](#english)

---

## 日本語

### 中身

| ファイル | 内容 | ライセンス |
|---|---|---|
| `Pinyin.json` | 辞書データ（約380KB） | CC BY-SA 4.0（Unihan 由来の部分は Unicode License V3 も） |
| `tools/make_pinyin_json.py` | `Pinyin.json` を作る Python スクリプト | MIT |
| `LICENSE` | 上のライセンスの全文 | — |

### Pinyin.json の形

```json
{
  "sources": { "cedict": {...}, "unihan": {...}, "license": "...", "generated": "2026-11-01" },
  "chars": { "乾": "gān", ... },
  "words": { "乾坤": "qián kūn", "謝謝": "xiè xiè", ... },
  "multi": { "乾": ["gān", "qián"], ... }
}
```

- `chars`：1文字の標準の読み（台湾で好まれる読み）。11,685字
- `words`：2文字以上の単語の読み。`chars` の読みを1文字ずつ並べたものと違う単語だけを入れている。7,619語
- `multi`：読みが複数ある字。先頭が標準の読み。678字
- 読みは声調記号つきのピンインで、音節ごとに半角スペースで区切っています

使い方の例：文の頭から「`words` にある一番長い単語」を当てはめ、当てはまらない字は `chars` の読みを使います。

### 元データ

| データ | 出典 | 版・日付 | ライセンス |
|---|---|---|---|
| CC-CEDICT | MDBG<br>https://www.mdbg.net/chinese/dictionary?page=cc-cedict | 2026-10-31T01:52:43Z（125,330項目） | CC BY-SA 4.0 |
| Unihan Database（`Unihan_Readings.txt` の kMandarin・kHanyuPinyin） | Unicode, Inc.<br>https://www.unicode.org/Public/UCD/latest/ucd/Unihan.zip | Unicode 18.0.0（2026-07-31） | Unicode License V3 |

CC-CEDICT は CEDICT（Copyright (C) 1997, 1998 Paul Andrew Denisowski）をもとにしています。

### どう加工したか

1. **1文字の読み**：Unihan の kMandarin を使います。値が2つあるときは、2つ目（台湾で好まれる読み）を使います。kMandarin がない字は、CC-CEDICT の1文字の項目の最初の読みを使います。
2. **単語の読み**：CC-CEDICT の繁体字の見出しのうち、2文字以上で、すべて漢字のものを使います。
   - 固有名詞（読みが大文字で始まるもの）と「variant of」の項目は使いません。
   - 同じ見出しが複数あるときは、説明（意味）の数がいちばん多いものを選びます。同じ数なら先に出てくるものを選びます（例：便宜 → pián yí）。
   - 「Taiwan pr. [...]」が単独の説明として書かれていれば、その読みをそのまま使います（例：垃圾 → lè sè）。
   - それ以外は、**軽声（声調のない音節）を台湾式に直します**。その字の1文字の読みに置き換えます（例：謝謝 xiè xie → xiè xiè、東西 dōng xi → dōng xī）。
   - ただし、台湾でも軽く読む次の字は軽声のままにします：的 了 嗎 呢 吧 啊 著 們 麼 呀 啦 嘛 喔 哦 囉 子 兒（兒は r 化の r）。
   - 番号つきピンイン（例：gan1）を、声調記号つきピンイン（例：gān）に直しています。
3. **読みが複数ある字**：Unihan の kMandarin と kHanyuPinyin の読みのうち、CC-CEDICT の見出しで実際にその字の読みとして使われているものが2つ以上ある字です。軽声だけの読み（頭の tou など、同じ音で声調のある読みもあるもの）は数えません。

自動で作ったデータなので、台湾での実際の読みと違うことがあります。

### 作り直し方

Python 3.9 以上が必要です（標準ライブラリだけで動きます）。

```bash
curl -LO https://www.mdbg.net/chinese/export/cedict/cedict_1_0_ts_utf-8_mdbg.txt.gz
gunzip cedict_1_0_ts_utf-8_mdbg.txt.gz
curl -LO https://www.unicode.org/Public/UCD/latest/ucd/Unihan.zip
unzip Unihan.zip Unihan_Readings.txt
python3 -I tools/make_pinyin_json.py cedict_1_0_ts_utf-8_mdbg.txt Unihan_Readings.txt Pinyin.json
```

元データの版が変わると、`Pinyin.json` の中身も変わります。使った版と日付は、`Pinyin.json` の `sources` に記録されます。

### ライセンス

- `Pinyin.json` は **CC BY-SA 4.0** です（元の CC-CEDICT が CC BY-SA 4.0 のため）。Unihan 由来の部分には **Unicode License V3** も適用されます。
- `Pinyin.json` を使ったり配ったりするときは、次の3つを示してください。
  - 出典（CC-CEDICT〔MDBG〕と Unihan〔Unicode, Inc.〕）
  - 加工したデータであること
  - ライセンス（CC BY-SA 4.0）とそのリンク
- `Pinyin.json` を加工して配るときは、CC BY-SA 4.0（またはその互換ライセンス）にしてください。
- `tools/make_pinyin_json.py` は MIT ライセンスです。
- 全文は [LICENSE](LICENSE) にあります。このデータは無保証です。

---

## English

### Contents

| File | Description | License |
|---|---|---|
| `Pinyin.json` | Dictionary data (about 380 KB) | CC BY-SA 4.0 (portions derived from Unihan are also subject to the Unicode License V3) |
| `tools/make_pinyin_json.py` | Python script that builds `Pinyin.json` | MIT |
| `LICENSE` | Full texts of the licenses above | — |

### Format of Pinyin.json

```json
{
  "sources": { "cedict": {...}, "unihan": {...}, "license": "...", "generated": "2026-11-01" },
  "chars": { "乾": "gān", ... },
  "words": { "乾坤": "qián kūn", "謝謝": "xiè xiè", ... },
  "multi": { "乾": ["gān", "qián"], ... }
}
```

- `chars`: default reading of each character (the reading preferred in Taiwan). 11,685 characters.
- `words`: readings of words of two or more characters. Only words whose reading differs from the per-character readings in `chars` are included. 7,619 words.
- `multi`: characters with two or more readings. The default reading comes first. 678 characters.
- Readings are tone-marked pinyin, one syllable per space-separated token.

Example of use: from the start of a sentence, match the longest word found in `words`; for characters that don't match a word, use `chars`.

### Sources

| Data | Source | Version / date | License |
|---|---|---|---|
| CC-CEDICT | MDBG<br>https://www.mdbg.net/chinese/dictionary?page=cc-cedict | 2026-10-31T01:52:43Z (125,330 entries) | CC BY-SA 4.0 |
| Unihan Database (kMandarin and kHanyuPinyin in `Unihan_Readings.txt`) | Unicode, Inc.<br>https://www.unicode.org/Public/UCD/latest/ucd/Unihan.zip | Unicode 18.0.0 (2026-07-31) | Unicode License V3 |

CC-CEDICT references CEDICT, Copyright (C) 1997, 1998 Paul Andrew Denisowski.

### How the data was adapted

1. **Character readings**: taken from Unihan kMandarin. When kMandarin has two values, the second one (preferred in Taiwan) is used. Characters without kMandarin use the first reading of their single-character entry in CC-CEDICT.
2. **Word readings**: taken from CC-CEDICT traditional headwords that have two or more characters, all of them Han characters.
   - Proper nouns (readings starting with a capital letter) and "variant of" entries are skipped.
   - When a headword has several entries, the one with the most definitions is chosen. On a tie, the first one is chosen (e.g. 便宜 → pián yí).
   - If a standalone definition "Taiwan pr. [...]" is present, that reading is used as is (e.g. 垃圾 → lè sè).
   - Otherwise, **neutral-tone syllables are changed to the Taiwanese style**: each one is replaced with the character's default reading (e.g. 謝謝 xiè xie → xiè xiè, 東西 dōng xi → dōng xī).
   - The following characters, which are read with a neutral tone in Taiwan as well, are kept as is: 的 了 嗎 呢 吧 啊 著 們 麼 呀 啦 嘛 喔 哦 囉 子 兒 (兒 as the erhua "r").
   - Numbered pinyin (e.g. gan1) is converted to tone-marked pinyin (e.g. gān).
3. **Characters with several readings**: characters that have two or more readings from Unihan kMandarin and kHanyuPinyin which are actually used for that character in CC-CEDICT headwords. A toneless reading is not counted when the same syllable also appears with a tone (e.g. tou for 頭).

This data is generated automatically and may differ from actual readings used in Taiwan.

### How to rebuild

Requires Python 3.9 or later (standard library only).

```bash
curl -LO https://www.mdbg.net/chinese/export/cedict/cedict_1_0_ts_utf-8_mdbg.txt.gz
gunzip cedict_1_0_ts_utf-8_mdbg.txt.gz
curl -LO https://www.unicode.org/Public/UCD/latest/ucd/Unihan.zip
unzip Unihan.zip Unihan_Readings.txt
python3 -I tools/make_pinyin_json.py cedict_1_0_ts_utf-8_mdbg.txt Unihan_Readings.txt Pinyin.json
```

The output changes when the source data changes. The versions and dates used are recorded in `sources` in `Pinyin.json`.

### License

- `Pinyin.json` is licensed under **CC BY-SA 4.0**, because CC-CEDICT is licensed under CC BY-SA 4.0. Portions derived from Unihan are also subject to the **Unicode License V3**.
- When you use or share `Pinyin.json`, please give:
  - credit to the sources (CC-CEDICT by MDBG, and Unihan by Unicode, Inc.),
  - a notice that the data has been modified,
  - the license (CC BY-SA 4.0) and a link to it.
- If you share adapted versions of `Pinyin.json`, license them under CC BY-SA 4.0 (or a compatible license).
- `tools/make_pinyin_json.py` is licensed under the MIT License.
- See [LICENSE](LICENSE) for the full texts. This data is provided without warranty.
