#!/usr/bin/env python3
"""Cut-in-Meter マネタイズ戦略 PPTX 生成スクリプト"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.oxml.ns import qn
from lxml import etree

# ============================================================
# カラーパレット
# ============================================================
C_NAVY    = RGBColor(0x0F, 0x27, 0x4D)
C_BLUE    = RGBColor(0x25, 0x63, 0xEB)
C_BLUE_L  = RGBColor(0xDB, 0xEA, 0xFE)
C_GREEN   = RGBColor(0x15, 0x80, 0x3D)
C_GREEN_L = RGBColor(0xDC, 0xFC, 0xE7)
C_YEL     = RGBColor(0xB4, 0x5A, 0x09)
C_YEL_L   = RGBColor(0xFE, 0xF3, 0xC7)
C_RED     = RGBColor(0xB9, 0x1C, 0x1C)
C_RED_L   = RGBColor(0xFE, 0xE2, 0xE2)
C_PURPLE  = RGBColor(0x6D, 0x28, 0xD9)
C_PURPLE_L= RGBColor(0xED, 0xE9, 0xFE)
C_TEAL    = RGBColor(0x0F, 0x76, 0x6E)
C_TEAL_L  = RGBColor(0xCC, 0xFB, 0xF1)
C_ORANGE  = RGBColor(0xC2, 0x41, 0x0C)
C_ORANGE_L= RGBColor(0xFF, 0xED, 0xD5)
C_WHITE   = RGBColor(0xFF, 0xFF, 0xFF)
C_LIGHT   = RGBColor(0xF8, 0xFA, 0xFC)
C_LGRAY   = RGBColor(0xE2, 0xE8, 0xF0)
C_GRAY    = RGBColor(0x94, 0xA3, 0xB8)
C_TEXT    = RGBColor(0x1E, 0x29, 0x3B)
C_MUTED   = RGBColor(0x64, 0x74, 0x8B)
C_GOLD    = RGBColor(0xD9, 0x70, 0x06)
C_GOLD_L  = RGBColor(0xFF, 0xF7, 0xED)

FONT = "Meiryo UI"
SW = Inches(13.33)
SH = Inches(7.5)

# ============================================================
# ヘルパー関数
# ============================================================

def new_slide(prs):
    return prs.slides.add_slide(prs.slide_layouts[6])


def bg(slide, color):
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def rect(slide, l, t, w, h, fill=None, line=None, lw=Pt(1), radius=False):
    stype = 5 if radius else 1
    s = slide.shapes.add_shape(stype, l, t, w, h)
    if fill:
        s.fill.solid()
        s.fill.fore_color.rgb = fill
    else:
        s.fill.background()
    if line:
        s.line.color.rgb = line
        s.line.width = lw
    else:
        s.line.fill.background()
    return s


def txt(slide, text, l, t, w, h, bold=False, size=14, color=C_TEXT,
        align=PP_ALIGN.LEFT, italic=False, wrap=True, font=FONT):
    box = slide.shapes.add_textbox(l, t, w, h)
    tf = box.text_frame
    tf.word_wrap = wrap
    para = tf.paragraphs[0]
    para.alignment = align
    run = para.add_run()
    run.text = text
    run.font.name = font
    run.font.bold = bold
    run.font.italic = italic
    run.font.size = Pt(size)
    run.font.color.rgb = color
    return box


def txt_block(slide, lines, l, t, w, h, default_size=11, default_color=C_TEXT,
              default_align=PP_ALIGN.LEFT, sp_after=2):
    """lines = list of (text,) or (text, bold) or (text, bold, size) or (text, bold, size, color)"""
    box = slide.shapes.add_textbox(l, t, w, h)
    tf = box.text_frame
    tf.word_wrap = True
    first = True
    for item in lines:
        if isinstance(item, str):
            text, bold, sz, clr = item, False, default_size, default_color
        else:
            text = item[0]
            bold = item[1] if len(item) > 1 else False
            sz   = item[2] if len(item) > 2 else default_size
            clr  = item[3] if len(item) > 3 else default_color
        para = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        para.alignment = default_align
        para.space_after = Pt(sp_after)
        run = para.add_run()
        run.text = text
        run.font.name = FONT
        run.font.bold = bold
        run.font.size = Pt(sz)
        run.font.color.rgb = clr
    return box


def header_bar(slide, title, label=None):
    rect(slide, 0, 0, SW, Inches(1.05), fill=C_NAVY)
    rect(slide, 0, Inches(1.05), SW, Pt(3), fill=C_BLUE)
    txt(slide, title, Inches(0.45), Inches(0.18), Inches(10.5), Inches(0.75),
        bold=True, size=22, color=C_WHITE)
    if label:
        txt(slide, label, Inches(10.5), Inches(0.28), Inches(2.5), Inches(0.5),
            size=10, color=C_GRAY, align=PP_ALIGN.RIGHT)


def card(slide, l, t, w, h, accent, light, title, body_lines, badge_text=None):
    """汎用カード"""
    rect(slide, l, t, w, h, fill=light, line=accent, lw=Pt(1.2), radius=True)
    rect(slide, l, t, w, Inches(0.38), fill=accent, radius=True)
    rect(slide, l, t + Inches(0.38) - Pt(2), w, Pt(4), fill=accent)
    txt(slide, title, l + Inches(0.12), t + Inches(0.06), w - Inches(0.24), Inches(0.3),
        bold=True, size=11, color=C_WHITE)
    if badge_text:
        txt(slide, badge_text, l + w - Inches(1.5), t + Inches(0.06),
            Inches(1.4), Inches(0.28), size=8.5, bold=True,
            color=C_GOLD_L, align=PP_ALIGN.RIGHT)
    txt_block(slide, body_lines, l + Inches(0.12), t + Inches(0.45),
              w - Inches(0.24), h - Inches(0.55), default_size=9.5, default_color=C_TEXT)


def score_dot(slide, l, t, score, max_score=5):
    """スコアドット表示"""
    for i in range(max_score):
        fill = C_BLUE if i < score else C_LGRAY
        rect(slide, l + Inches(0.22 * i), t, Inches(0.18), Inches(0.18),
             fill=fill, radius=True)


# ============================================================
# Slide 1: タイトル
# ============================================================
def slide_title(prs):
    s = new_slide(prs)
    bg(s, C_NAVY)

    # デコレーション
    rect(s, 0, SH - Inches(0.08), SW, Inches(0.08), fill=C_BLUE)
    rect(s, 0, 0, Inches(0.5), SH, fill=RGBColor(0x19, 0x3A, 0x6A))
    rect(s, Inches(0.5), 0, Inches(0.04), SH, fill=C_BLUE)

    txt(s, "Cut-in-Meter", Inches(1.2), Inches(1.5), Inches(10), Inches(1.4),
        bold=True, size=54, color=C_WHITE)
    txt(s, "プロダクト化戦略", Inches(1.2), Inches(3.0), Inches(10), Inches(0.9),
        bold=True, size=32, color=C_BLUE)
    txt(s, "マネタイズシナリオ分析  ×  開発ロードマップ",
        Inches(1.2), Inches(3.95), Inches(10), Inches(0.6),
        size=16, color=C_GRAY)
    txt(s, "2026年 4月", Inches(1.2), Inches(5.8), Inches(4), Inches(0.5),
        size=13, color=C_MUTED)


# ============================================================
# Slide 2: プロダクト概要
# ============================================================
def slide_overview(prs):
    s = new_slide(prs)
    bg(s, C_LIGHT)
    header_bar(s, "プロダクト概要")

    cw = Inches(3.9)
    ch = Inches(5.4)
    ct = Inches(1.4)
    gap = Inches(0.22)
    starts = [Inches(0.4), Inches(0.4) + cw + gap, Inches(0.4) + (cw + gap) * 2]

    card(s, starts[0], ct, cw, ch, C_BLUE, C_BLUE_L, "何をするアプリか", [
        ("「今、話しかけていい？」を AI が判定", True, 10),
        "",
        ("カメラ画像をリアルタイム解析し、", False, 9.5, C_MUTED),
        ("赤 / 黄 / 青の信号で割り込みOKかを表示", False, 9.5, C_MUTED),
        "",
        ("■ 主要機能", True, 9.5),
        ("・  カメラ / 画像ファイルからAI判定", False, 9.5),
        ("・  赤・黄・青の交通信号表示", False, 9.5),
        ("・  判定レベル調整（慎重〜ゆるめ）", False, 9.5),
        ("・  スコア履歴・スナップショット保存", False, 9.5),
        ("・  手動オーバーライド機能", False, 9.5),
    ])

    card(s, starts[1], ct, cw, ch, C_TEAL, C_TEAL_L, "現在の技術スタック", [
        ("バックエンド", True, 9.5),
        ("・  Python / FastAPI", False, 9.5),
        ("・  OpenAI Vision API（GPT-4 系）", False, 9.5),
        ("・  データ: CSV + ローカルJPEG", False, 9.5),
        "",
        ("フロントエンド", True, 9.5),
        ("・  Vanilla HTML / CSS / JS", False, 9.5),
        ("・  Chart.js（スコア推移グラフ）", False, 9.5),
        "",
        ("インフラ", True, 9.5),
        ("・  ローカル実行のみ（Docker未対応）", False, 9.5),
        ("・  認証・課金機能なし", False, 9.5),
    ])

    card(s, starts[2], ct, cw, ch, C_ORANGE, C_ORANGE_L, "プロダクト化に向けた課題", [
        ("技術的課題", True, 9.5),
        ("・  ローカル限定 → クラウド展開が必要", False, 9.5),
        ("・  CSV保存 → DB化が必要", False, 9.5),
        ("・  認証機能が未実装", False, 9.5),
        ("・  テストがほぼゼロ", False, 9.5),
        "",
        ("ビジネス的課題", True, 9.5),
        ("・  マネタイズ設計が未定", False, 9.5),
        ("・  「ジョークアプリ」の位置付けを脱する", False, 9.5),
        ("・  競合との差別化ポイント整理が必要", False, 9.5),
        "",
        ("→ 以降のスライドで解決策を提示", True, 9.5, C_ORANGE),
    ])


# ============================================================
# Slide 3: 市場機会
# ============================================================
def slide_market(prs):
    s = new_slide(prs)
    bg(s, C_LIGHT)
    header_bar(s, "市場機会  ー  なぜ今このプロダクトか")

    # 3つの大きな数字
    stats = [
        ("3.3億人", "世界のリモートワーカー数\n（2025年推計）", C_BLUE, C_BLUE_L),
        ("23分", "割り込み後に集中力を\n取り戻すまでの平均時間\n（UC Irvine研究）", C_RED, C_RED_L),
        ("$1.9兆", "生産性損失の年間コスト\n（非効率な割り込みによる\n米国企業全体の試算）", C_GREEN, C_GREEN_L),
    ]
    sw = Inches(3.9)
    sh = Inches(2.6)
    st = Inches(1.25)
    for i, (num, label, c, cl) in enumerate(stats):
        sl = Inches(0.4) + (sw + Inches(0.22)) * i
        rect(s, sl, st, sw, sh, fill=cl, line=c, lw=Pt(1.5), radius=True)
        txt(s, num, sl + Inches(0.15), st + Inches(0.2), sw - Inches(0.3), Inches(0.9),
            bold=True, size=36, color=c, align=PP_ALIGN.CENTER)
        txt(s, label, sl + Inches(0.15), st + Inches(1.1), sw - Inches(0.3), Inches(1.3),
            size=11, color=C_TEXT, align=PP_ALIGN.CENTER)

    # ボトムセクション
    rect(s, Inches(0.4), Inches(4.1), SW - Inches(0.8), Inches(2.85),
         fill=C_WHITE, line=C_LGRAY, lw=Pt(1))

    txt(s, "テクノロジートレンドとの整合性", Inches(0.6), Inches(4.25),
        Inches(12), Inches(0.4), bold=True, size=13, color=C_TEXT)

    trends = [
        ("🏠  リモート・ハイブリッドワークの定着", "Zoom / Slack / Teams での非同期コミュニケーションが常態化。"),
        ("🤖  マルチモーダルAIの実用化",         "GPT-4o 等の Vision API が低コスト・高精度で利用可能に。"),
        ("🔔  通知疲れ・集中管理ツールへの需要",  "Deep Focus / Focus Mode ツール市場が急拡大中。"),
        ("👥  チームウェア市場の成熟",            "Slack・Teamsとの統合でプラグインエコノミーが確立済み。"),
    ]
    for i, (title, desc) in enumerate(trends):
        row_t = Inches(4.7) + Inches(0.48) * i
        txt(s, title, Inches(0.6), row_t, Inches(4.2), Inches(0.4),
            bold=True, size=10, color=C_NAVY)
        txt(s, desc, Inches(4.9), row_t, Inches(8.0), Inches(0.4),
            size=10, color=C_MUTED)


# ============================================================
# Slide 4: シナリオ比較マトリクス
# ============================================================
def slide_matrix(prs):
    s = new_slide(prs)
    bg(s, C_LIGHT)
    header_bar(s, "5つのマネタイズシナリオ  ー  比較マトリクス")

    headers = ["シナリオ", "対象顧客", "収益モデル", "市場規模", "開発コスト", "収益ポテンシャル", "実現速度", "推奨度"]
    rows = [
        ["① B2C フリーミアム",     "個人・リモートワーカー",  "月額 ¥500〜",     "中",  "低",  "中",  "速",    "★★★☆☆"],
        ["② B2B チームSaaS",       "企業・チーム",            "¥500〜/人/月",    "大",  "中",  "高",  "中",    "★★★★★"],
        ["③ API as a Service",     "開発者・スタートアップ",  "従量課金",        "中",  "中",  "中",  "中",    "★★★★☆"],
        ["④ プラットフォームプラグイン", "Slack/Zoom ユーザー",    "$2〜5/人/月",     "大",  "中",  "高",  "中",    "★★★★☆"],
        ["⑤ OEM・ライセンス",      "デバイスメーカー",        "年間ライセンス料", "小",  "低",  "高",  "遅",    "★★★☆☆"],
    ]
    highlight_row = 1  # B2B SaaS

    col_ws = [Inches(2.3), Inches(2.1), Inches(1.7), Inches(0.85),
              Inches(1.1), Inches(1.5), Inches(0.95), Inches(1.05)]
    table_l = Inches(0.4)
    table_t = Inches(1.25)
    table_w = sum(col_ws)
    row_h = Inches(0.6)
    header_h = Inches(0.48)

    # ヘッダー行
    cx = table_l
    for i, (hdr, cw) in enumerate(zip(headers, col_ws)):
        rect(s, cx, table_t, cw, header_h, fill=C_NAVY)
        txt(s, hdr, cx + Inches(0.06), table_t + Inches(0.08), cw - Inches(0.1), header_h - Inches(0.1),
            bold=True, size=9, color=C_WHITE, align=PP_ALIGN.CENTER)
        cx += cw

    # データ行
    for ri, row in enumerate(rows):
        is_top = (ri == highlight_row)
        fill_c = C_BLUE_L if is_top else (C_WHITE if ri % 2 == 0 else C_LIGHT)
        row_t = table_t + header_h + row_h * ri
        cx = table_l
        for ci, (cell, cw) in enumerate(zip(row, col_ws)):
            lw = Pt(2) if is_top else Pt(0.5)
            line_c = C_BLUE if is_top else C_LGRAY
            rect(s, cx, row_t, cw, row_h, fill=fill_c, line=line_c, lw=lw)
            cell_bold = is_top and ci == 0
            cell_color = C_NAVY if is_top and ci == 0 else (C_BLUE if is_top else C_TEXT)
            align = PP_ALIGN.CENTER if ci > 1 else PP_ALIGN.LEFT
            txt(s, cell, cx + Inches(0.06), row_t + Inches(0.15),
                cw - Inches(0.1), row_h - Inches(0.15),
                bold=cell_bold, size=9, color=cell_color, align=align)
            cx += cw
        if is_top:
            txt(s, "← 最有力", table_l + table_w + Inches(0.1),
                row_t + Inches(0.17), Inches(1.0), Inches(0.3),
                bold=True, size=10, color=C_BLUE)

    txt(s, "※ 推奨度は市場規模・開発コスト・収益ポテンシャル・実現速度を総合評価",
        table_l, table_t + header_h + row_h * 5 + Inches(0.1),
        table_w, Inches(0.3), size=8.5, color=C_MUTED)


# ============================================================
# Slide 5〜9: 各シナリオ詳細
# ============================================================
SCENARIOS = [
    {
        "num": "①", "title": "B2C フリーミアム",
        "accent": C_TEAL, "light": C_TEAL_L,
        "target": "個人のリモートワーカー・テレワーク実施者",
        "price": "無料プラン + Pro ¥500/月（年払い ¥4,800）",
        "model": [
            ("フリーミアムモデル", True, 10),
            ("・ 無料: 1日20回まで判定 / データ7日保持", False, 9.5),
            ("・ Pro: 無制限 + 履歴無期限 + CSV出力", False, 9.5),
            ("・ 将来: 家族プラン ¥800/月", False, 9.5),
        ],
        "pros": ["参入コストが低い", "SNS口コミで拡散しやすい", "ユーザーフィードバックを素早く得られる"],
        "cons": ["ARPU（顧客単価）が低い", "課金転換率は一般的に2〜5%", "競合個人ツールとの価格競争に巻き込まれやすい"],
        "arpu": "¥500/月",
        "tam": "中（国内数百万人）",
        "timeline": "3ヶ月でMVP可能",
        "risk": "収益化に時間がかかる",
    },
    {
        "num": "②", "title": "B2B チームSaaS",
        "accent": C_BLUE, "light": C_BLUE_L,
        "target": "リモートファースト企業・ハイブリッドワーク導入チーム",
        "price": "¥500〜1,000/ユーザー/月（年間契約でディスカウント）",
        "model": [
            ("チームプランモデル", True, 10),
            ("・ Starter: 〜10人 ¥4,000/月（¥400/人）", False, 9.5),
            ("・ Team: 〜50人 ¥20,000/月（¥400/人）", False, 9.5),
            ("・ Business: 〜200人 ¥70,000/月（¥350/人）", False, 9.5),
            ("・ Enterprise: 要問合せ（SSO/監査ログ付き）", False, 9.5),
        ],
        "pros": ["B2B高ARPU・低チャーン", "年間契約でキャッシュフロー安定", "法人名義 → 経費計上で解約されにくい"],
        "cons": ["営業・導入支援コストがかかる", "稟議プロセスで商談が長くなりやすい", "競合製品（Slack/Teams内蔵機能）との比較"],
        "arpu": "¥3,500/月（チーム単位）〜",
        "tam": "大（国内リモートワーク企業 数十万社）",
        "timeline": "4〜5ヶ月でβ版",
        "risk": "営業コストの回収期間",
        "is_top": True,
    },
    {
        "num": "③", "title": "API as a Service",
        "accent": C_PURPLE, "light": C_PURPLE_L,
        "target": "アプリ開発者・スタートアップ・SIer",
        "price": "従量課金 $0.005/リクエスト + 月額プラン（$29〜）",
        "model": [
            ("開発者向けAPIモデル", True, 10),
            ("・ Free: 500 req/月（開発用）", False, 9.5),
            ("・ Starter: $29/月 10,000 req", False, 9.5),
            ("・ Growth: $99/月 100,000 req", False, 9.5),
            ("・ Enterprise: カスタム SLA付き", False, 9.5),
        ],
        "pros": ["スケーラブルな収益構造", "開発者コミュニティで認知が広がる", "将来的にM&Aターゲットになりやすい"],
        "cons": ["OpenAI直接利用との競合リスク", "APIドキュメント・SDKの整備コスト", "スパム・悪用防止の設計が必要"],
        "arpu": "$29〜/月（開発者1社）",
        "tam": "中（グローバル開発者市場）",
        "timeline": "4ヶ月でβ版",
        "risk": "ユーザー獲得の難しさ",
    },
    {
        "num": "④", "title": "プラットフォームプラグイン",
        "accent": C_GREEN, "light": C_GREEN_L,
        "target": "Slack / Microsoft Teams / Zoom 利用企業",
        "price": "$2〜5/ユーザー/月（マーケットプレイス経由）",
        "model": [
            ("プラグイン販売モデル", True, 10),
            ("・ Slack App Directoryに掲載", False, 9.5),
            ("・ Microsoft AppSourceに掲載", False, 9.5),
            ("・ Zoom Marketplace に掲載", False, 9.5),
            ("・ 各プラットフォームが課金代行（手数料20〜30%）", False, 9.5),
        ],
        "pros": ["既存ユーザーベースを活用できる", "プラットフォームの信頼感で採用されやすい", "課金インフラが整備済み"],
        "cons": ["手数料20〜30%が収益を圧迫", "プラットフォームポリシー変更リスク", "API連携・審査の開発コスト"],
        "arpu": "$3/ユーザー/月（手数料控除後 $2.1）",
        "tam": "大（Slack 3,200万人 / Teams 3億2,000万人）",
        "timeline": "5〜6ヶ月",
        "risk": "プラットフォーム依存リスク",
    },
    {
        "num": "⑤", "title": "OEM・ライセンス",
        "accent": C_ORANGE, "light": C_ORANGE_L,
        "target": "ウェブカムメーカー / スマートホームデバイスメーカー / ビデオ会議ベンダー",
        "price": "年間ライセンス料 ¥5,000,000〜 / 出荷台数×ロイヤリティ",
        "model": [
            ("技術ライセンスモデル", True, 10),
            ("・ AIスコアリングエンジンをSDK化して提供", False, 9.5),
            ("・ デバイスへの組み込みライセンス", False, 9.5),
            ("・ ロゴ・ブランドOEM契約", False, 9.5),
            ("・ 保守サポート費用（年間契約）", False, 9.5),
        ],
        "pros": ["1契約で大きな売上が見込める", "自社マーケティングコスト不要", "製品の信頼性がパートナーのブランド力で向上"],
        "cons": ["商談サイクルが6ヶ月〜1年以上", "法務・契約交渉コストが大きい", "依存関係が強く戦略の自由度が低下"],
        "arpu": "¥5,000,000+/社/年（1件の影響大）",
        "tam": "小〜中（国内デバイスメーカー限定的）",
        "timeline": "交渉含め1年以上",
        "risk": "商談成立まで収益ゼロ期間",
    },
]


def slide_scenario(prs, sc):
    s = new_slide(prs)
    bg(s, C_LIGHT)
    title = f"シナリオ {sc['num']}：{sc['title']}"
    if sc.get("is_top"):
        title += "  ★ 最有力"
    header_bar(s, title)

    accent = sc["accent"]
    light = sc["light"]

    # 左カラム: 概要
    lw = Inches(6.0)
    rect(s, Inches(0.4), Inches(1.2), lw, Inches(5.8), fill=light, line=accent, lw=Pt(1.5), radius=True)

    txt(s, "基本情報", Inches(0.6), Inches(1.35), lw - Inches(0.3), Inches(0.35),
        bold=True, size=11, color=accent)

    info_items = [
        ("対象顧客", sc["target"]),
        ("価格帯",   sc["price"]),
        ("ARPU",    sc["arpu"]),
        ("市場規模", sc["tam"]),
        ("実装期間", sc["timeline"]),
        ("主リスク", sc["risk"]),
    ]
    for i, (label, val) in enumerate(info_items):
        row_t = Inches(1.75) + Inches(0.55) * i
        txt(s, label, Inches(0.6), row_t, Inches(1.4), Inches(0.4),
            bold=True, size=9.5, color=accent)
        txt(s, val, Inches(2.1), row_t, Inches(4.1), Inches(0.4),
            size=9.5, color=C_TEXT)

    txt(s, "収益モデル詳細", Inches(0.6), Inches(5.2), lw - Inches(0.3), Inches(0.35),
        bold=True, size=11, color=accent)
    txt_block(s, sc["model"], Inches(0.6), Inches(5.58), lw - Inches(0.3), Inches(1.2),
              default_size=9.5, default_color=C_TEXT)

    # 右カラム: 強み・弱み
    rw = Inches(6.55)
    rl = Inches(6.7)

    rect(s, rl, Inches(1.2), rw, Inches(2.8), fill=C_GREEN_L, line=C_GREEN, lw=Pt(1), radius=True)
    txt(s, "◎  強み（Pros）", rl + Inches(0.15), Inches(1.35), rw - Inches(0.3), Inches(0.38),
        bold=True, size=11, color=C_GREEN)
    for i, pro in enumerate(sc["pros"]):
        txt(s, f"・  {pro}", rl + Inches(0.2), Inches(1.8) + Inches(0.6) * i,
            rw - Inches(0.4), Inches(0.5), size=10, color=C_TEXT)

    rect(s, rl, Inches(4.15), rw, Inches(2.8), fill=C_RED_L, line=C_RED, lw=Pt(1), radius=True)
    txt(s, "△  弱み・リスク（Cons）", rl + Inches(0.15), Inches(4.3), rw - Inches(0.3), Inches(0.38),
        bold=True, size=11, color=C_RED)
    for i, con in enumerate(sc["cons"]):
        txt(s, f"・  {con}", rl + Inches(0.2), Inches(4.75) + Inches(0.6) * i,
            rw - Inches(0.4), Inches(0.5), size=10, color=C_TEXT)


# ============================================================
# Slide 10: 最有力シナリオ選定理由
# ============================================================
def slide_decision(prs):
    s = new_slide(prs)
    bg(s, C_LIGHT)
    header_bar(s, "最有力シナリオ選定  ー  なぜ B2B チームSaaS か")

    # タイトルバナー
    rect(s, Inches(0.4), Inches(1.2), SW - Inches(0.8), Inches(0.65), fill=C_BLUE, radius=True)
    txt(s, "シナリオ② B2B チームSaaS を最有力と判断する  5つの理由",
        Inches(0.6), Inches(1.3), SW - Inches(1.2), Inches(0.5),
        bold=True, size=14, color=C_WHITE, align=PP_ALIGN.CENTER)

    reasons = [
        (C_BLUE,   C_BLUE_L,  "1. 高い ARPU と低チャーン",
         "法人契約はARPU ¥3,500〜/月と個人の7倍以上。経費計上できるため解約率が低く安定した収益基盤を構築できる。"),
        (C_GREEN,  C_GREEN_L, "2. 実需と課題が明確",
         "「今話しかけていい？」はリモートチームに実在する課題。ジョークアプリを脱し、真の生産性ツールとして訴求できる。"),
        (C_PURPLE, C_PURPLE_L,"3. 現在の技術が直接活用できる",
         "カメラ判定・スコアリング・履歴管理は既に実装済み。追加すべきは認証・チーム管理・課金のみ。"),
        (C_TEAL,   C_TEAL_L,  "4. ④プラットフォームプラグインへの発展が容易",
         "B2B SaaS として実績を積んだ後、Slack/Teams プラグイン化で既存顧客をそのまま移行できる。"),
        (C_ORANGE, C_ORANGE_L,"5. 日本市場で先行者優位を取れる",
         "「割り込みタイミング判定」特化ツールは国内にほぼ競合なし。先行して日本市場のシェアを確保し得る。"),
    ]

    rw = (SW - Inches(0.8)) / 5 - Inches(0.1)
    for i, (c, cl, title, body) in enumerate(reasons):
        rl = Inches(0.4) + (rw + Inches(0.1)) * i
        rect(s, rl, Inches(2.05), rw, Inches(4.8), fill=cl, line=c, lw=Pt(1.2), radius=True)
        rect(s, rl, Inches(2.05), rw, Inches(0.38), fill=c, radius=True)
        rect(s, rl, Inches(2.05) + Inches(0.38) - Pt(2), rw, Pt(4), fill=c)
        txt(s, title, rl + Inches(0.08), Inches(2.1), rw - Inches(0.15), Inches(0.32),
            bold=True, size=9, color=C_WHITE)
        txt(s, body, rl + Inches(0.1), Inches(2.6), rw - Inches(0.2), Inches(4.0),
            size=9, color=C_TEXT, wrap=True)


# ============================================================
# Slide 11: 開発ロードマップ
# ============================================================
def slide_roadmap(prs):
    s = new_slide(prs)
    bg(s, C_LIGHT)
    header_bar(s, "開発ロードマップ  ー  B2B チームSaaS（12ヶ月計画）")

    phases = [
        {
            "label": "Phase 1", "months": "Month 1〜2", "title": "基盤整備",
            "color": C_TEAL, "light": C_TEAL_L,
            "tasks": ["Docker化 + Fly.io / Cloud Run デプロイ",
                      "Google OAuth 認証実装",
                      "PostgreSQL 移行（CSV廃止）",
                      "HTTPS・カスタムドメイン取得",
                      "CI/CD パイプライン（GitHub Actions）"],
            "kpi": "本番URLで動作",
            "month_start": 0, "month_span": 2,
        },
        {
            "label": "Phase 2", "months": "Month 3〜4", "title": "チーム機能",
            "color": C_BLUE, "light": C_BLUE_L,
            "tasks": ["ワークスペース / チーム管理機能",
                      "メンバー招待・権限管理",
                      "チームダッシュボード（全員の状態一覧）",
                      "Slack 通知連携",
                      "管理者向けアナリティクス"],
            "kpi": "β版リリース・5社のパイロット導入",
            "month_start": 2, "month_span": 2,
        },
        {
            "label": "Phase 3", "months": "Month 5〜6", "title": "マネタイズ",
            "color": C_GREEN, "light": C_GREEN_L,
            "tasks": ["Stripe 決済統合",
                      "Free / Starter / Team プラン実装",
                      "使用量計測・プランごとの制限",
                      "ランディングページ作成",
                      "カスタマーサポート体制整備"],
            "kpi": "有料顧客 20社・MRR ¥200,000",
            "month_start": 4, "month_span": 2,
        },
        {
            "label": "Phase 4", "months": "Month 7〜12", "title": "スケール",
            "color": C_PURPLE, "light": C_PURPLE_L,
            "tasks": ["Slack App / Microsoft Teams アプリ",
                      "SSO（SAML / OIDC）対応",
                      "監査ログ・セキュリティ強化",
                      "API公開（開発者向け）",
                      "エンタープライズ向け個別契約対応"],
            "kpi": "有料顧客 150社・MRR ¥1,500,000",
            "month_start": 6, "month_span": 6,
        },
    ]

    # ガントバー
    timeline_l = Inches(3.0)
    timeline_w = SW - Inches(3.5)
    month_w = timeline_w / 12
    phase_h = Inches(1.1)
    phase_gap = Inches(0.12)
    start_t = Inches(1.25)

    # 月ヘッダー
    for m in range(12):
        ml = timeline_l + month_w * m
        rect(s, ml, start_t - Inches(0.38), month_w, Inches(0.35), fill=C_NAVY)
        txt(s, f"M{m+1}", ml + Inches(0.02), start_t - Inches(0.35),
            month_w - Inches(0.04), Inches(0.3),
            bold=False, size=8, color=C_GRAY, align=PP_ALIGN.CENTER)

    for i, ph in enumerate(phases):
        pt = start_t + (phase_h + phase_gap) * i
        # ラベル列
        rect(s, Inches(0.4), pt, Inches(2.5), phase_h, fill=ph["light"], line=ph["color"], lw=Pt(1))
        txt(s, ph["label"], Inches(0.5), pt + Inches(0.05), Inches(2.3), Inches(0.3),
            bold=True, size=11, color=ph["color"])
        txt(s, ph["months"], Inches(0.5), pt + Inches(0.35), Inches(2.3), Inches(0.25),
            size=8.5, color=C_MUTED)
        txt(s, ph["title"], Inches(0.5), pt + Inches(0.6), Inches(2.3), Inches(0.4),
            bold=True, size=10, color=C_TEXT)

        # ガントバー
        bar_l = timeline_l + month_w * ph["month_start"]
        bar_w = month_w * ph["month_span"] - Inches(0.04)
        rect(s, bar_l, pt + Inches(0.18), bar_w, Inches(0.65),
             fill=ph["color"], radius=True)
        # タスクリスト（バー内テキスト）
        task_str = "  ·  ".join(ph["tasks"][:3])
        txt(s, task_str, bar_l + Inches(0.1), pt + Inches(0.22),
            bar_w - Inches(0.15), Inches(0.6),
            size=7.5, color=C_WHITE, bold=False)

    # KPI サマリー（右下）
    kpi_t = start_t + (phase_h + phase_gap) * 4 + Inches(0.1)
    rect(s, Inches(0.4), kpi_t, SW - Inches(0.8), Inches(0.75), fill=C_NAVY, radius=True)
    kpi_items = ["Phase1完了: 本番稼働", "Phase2完了: β版・5社導入",
                 "Phase3完了: MRR ¥200K", "Phase4完了: MRR ¥1.5M"]
    kpi_w = (SW - Inches(1.2)) / 4
    for i, kpi in enumerate(kpi_items):
        txt(s, kpi, Inches(0.6) + kpi_w * i, kpi_t + Inches(0.18),
            kpi_w, Inches(0.4), size=9.5, bold=True, color=C_WHITE, align=PP_ALIGN.CENTER)


# ============================================================
# Slide 12: 収益シミュレーション
# ============================================================
def slide_revenue(prs):
    s = new_slide(prs)
    bg(s, C_LIGHT)
    header_bar(s, "収益シミュレーション  ー  B2B チームSaaS（保守的シナリオ）")

    # 数字カード
    milestones = [
        ("Phase 3 完了\nMonth 6",   "¥200,000",  "/月",  "20社 × 平均10人 × ¥1,000", C_TEAL,   C_TEAL_L),
        ("Phase 4 中盤\nMonth 9",   "¥750,000",  "/月",  "75社 × 平均10人 × ¥1,000", C_BLUE,   C_BLUE_L),
        ("Phase 4 完了\nMonth 12",  "¥1,500,000","/月",  "150社 × 平均10人 × ¥1,000",C_PURPLE, C_PURPLE_L),
        ("スケール\nMonth 18",      "¥5,000,000","/月",  "350社 × 平均14人 × ¥1,020", C_GREEN,  C_GREEN_L),
    ]
    mw = (SW - Inches(1.0)) / 4 - Inches(0.1)
    for i, (period, mrr, unit, basis, c, cl) in enumerate(milestones):
        ml = Inches(0.4) + (mw + Inches(0.1)) * i
        rect(s, ml, Inches(1.25), mw, Inches(3.0), fill=cl, line=c, lw=Pt(1.5), radius=True)
        txt(s, period, ml + Inches(0.12), Inches(1.35), mw - Inches(0.24), Inches(0.65),
            size=9.5, color=c, bold=True, align=PP_ALIGN.CENTER)
        txt(s, mrr, ml + Inches(0.06), Inches(2.05), mw - Inches(0.12), Inches(0.75),
            bold=True, size=22, color=c, align=PP_ALIGN.CENTER)
        txt(s, unit, ml + Inches(0.06), Inches(2.85), mw - Inches(0.12), Inches(0.3),
            size=10, color=C_MUTED, align=PP_ALIGN.CENTER)
        txt(s, basis, ml + Inches(0.08), Inches(3.25), mw - Inches(0.16), Inches(0.8),
            size=8.5, color=C_MUTED, align=PP_ALIGN.CENTER)

    # 視覚的バーグラフ
    bar_data = [
        ("M6",  200_000),
        ("M9",  750_000),
        ("M12", 1_500_000),
        ("M18", 5_000_000),
    ]
    max_val = 5_000_000
    graph_l = Inches(0.6)
    graph_b = Inches(6.9)
    graph_h = Inches(2.1)
    graph_w = SW - Inches(1.2)
    bar_w = Inches(1.5)
    bar_gap = (graph_w - bar_w * len(bar_data)) / (len(bar_data) + 1)

    rect(s, graph_l, graph_b - graph_h - Inches(0.1), graph_w, Inches(0.02), fill=C_LGRAY)

    colors = [C_TEAL, C_BLUE, C_PURPLE, C_GREEN]
    for i, (label, val) in enumerate(bar_data):
        bh = graph_h * (val / max_val)
        bl = graph_l + bar_gap + (bar_w + bar_gap) * i
        bt = graph_b - bh - Inches(0.1)
        rect(s, bl, bt, bar_w, bh, fill=colors[i], radius=True)
        txt(s, f"¥{val:,}", bl, bt - Inches(0.35), bar_w, Inches(0.3),
            bold=True, size=9, color=colors[i], align=PP_ALIGN.CENTER)
        txt(s, label, bl, graph_b - Inches(0.05), bar_w, Inches(0.25),
            size=9, color=C_MUTED, align=PP_ALIGN.CENTER)

    txt(s, "※ 保守的シナリオ。チャーン率5%/月、新規獲得20社/月（Phase4）を前提",
        Inches(0.4), Inches(7.2), SW - Inches(0.8), Inches(0.25),
        size=8, color=C_MUTED)


# ============================================================
# Slide 13: 次のアクション
# ============================================================
def slide_action(prs):
    s = new_slide(prs)
    bg(s, C_LIGHT)
    header_bar(s, "次のアクション  ー  まず30日でやること")

    actions = [
        {
            "week": "Week 1〜2", "theme": "インフラ基盤", "color": C_TEAL,
            "items": [
                "✅  Dockerfile / docker-compose.yml 作成（完了）",
                "□  Fly.io または Cloud Run にデプロイ",
                "□  カスタムドメイン + HTTPS 設定",
                "□  Google OAuth 認証の実装",
            ]
        },
        {
            "week": "Week 3", "theme": "データ基盤", "color": C_BLUE,
            "items": [
                "□  PostgreSQL への移行（CSV廃止）",
                "□  ユーザーテーブル・チームテーブル設計",
                "□  既存データの移行スクリプト作成",
                "□  GitHub Actions で CI を設定",
            ]
        },
        {
            "week": "Week 4", "theme": "プロダクト検証", "color": C_PURPLE,
            "items": [
                "□  知人のリモートワーカーに無料βテスト依頼（5〜10人）",
                "□  フィードバックシート作成・ヒアリング実施",
                "□  「1チームに価値があるか」を検証",
                "□  ランディングページのワイヤーフレーム作成",
            ]
        },
        {
            "week": "Month 2", "theme": "マネタイズ設計", "color": C_GREEN,
            "items": [
                "□  Stripe アカウント開設・料金プラン設計",
                "□  チーム招待機能のプロトタイプ実装",
                "□  最初の有料顧客 1社を獲得する",
                "□  Month 3 の開発計画をレビュー",
            ]
        },
    ]

    cw = (SW - Inches(0.8)) / 4 - Inches(0.1)
    for i, a in enumerate(actions):
        cl = Inches(0.4) + (cw + Inches(0.1)) * i
        ct = Inches(1.25)
        rect(s, cl, ct, cw, Inches(5.7), fill=C_WHITE, line=a["color"], lw=Pt(1.5), radius=True)
        rect(s, cl, ct, cw, Inches(0.42), fill=a["color"], radius=True)
        rect(s, cl, ct + Inches(0.42) - Pt(2), cw, Pt(4), fill=a["color"])
        txt(s, a["week"], cl + Inches(0.1), ct + Inches(0.06), cw - Inches(0.2), Inches(0.18),
            size=8, color=C_WHITE, bold=False)
        txt(s, a["theme"], cl + Inches(0.1), ct + Inches(0.22), cw - Inches(0.2), Inches(0.22),
            size=11, color=C_WHITE, bold=True)
        for j, item in enumerate(a["items"]):
            item_t = ct + Inches(0.55) + Inches(1.2) * j
            bg_c = C_GREEN_L if item.startswith("✅") else C_LIGHT
            rect(s, cl + Inches(0.1), item_t, cw - Inches(0.2), Inches(1.05),
                 fill=bg_c, line=C_LGRAY, lw=Pt(0.5), radius=True)
            txt(s, item, cl + Inches(0.18), item_t + Inches(0.1),
                cw - Inches(0.36), Inches(0.88),
                size=9, color=C_TEXT, wrap=True)

    # ボトムメッセージ
    rect(s, Inches(0.4), Inches(7.05), SW - Inches(0.8), Inches(0.35), fill=C_NAVY, radius=True)
    txt(s, "最初の一手：Fly.io へのデプロイ。URLが生まれた瞬間にプロダクトは始まる。",
        Inches(0.6), Inches(7.1), SW - Inches(1.2), Inches(0.28),
        bold=True, size=11, color=C_WHITE, align=PP_ALIGN.CENTER)


# ============================================================
# メイン
# ============================================================
def main():
    prs = Presentation()
    prs.slide_width = SW
    prs.slide_height = SH

    slide_title(prs)
    slide_overview(prs)
    slide_market(prs)
    slide_matrix(prs)
    for sc in SCENARIOS:
        slide_scenario(prs, sc)
    slide_decision(prs)
    slide_roadmap(prs)
    slide_revenue(prs)
    slide_action(prs)

    output = "cut-in-meter-monetization.pptx"
    prs.save(output)
    print(f"[OK] saved: {output}  ({len(prs.slides)} slides)")


if __name__ == "__main__":
    main()
