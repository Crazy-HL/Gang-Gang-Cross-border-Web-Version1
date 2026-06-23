from __future__ import annotations

from io import BytesIO
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.ttfonts import TTFError
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


RISK_LABELS = {
    'high': '高风险',
    'medium': '中风险',
    'low': '低风险',
    'pending': '待检测',
}

REVIEW_LABELS = {
    'none': '未申请',
    'pending': '待人工复核',
    'approved': '已通过复核',
    'rejected': '已驳回复核',
}


def _register_font() -> str:
    candidates = [
        Path('C:/Windows/Fonts/simhei.ttf'),
        Path('C:/Windows/Fonts/Deng.ttf'),
        Path('C:/Windows/Fonts/NotoSansSC-VF.ttf'),
        Path('C:/Windows/Fonts/msyh.ttc'),
        Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc'),
        Path('/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc'),
    ]
    for path in candidates:
        if path.exists():
            try:
                pdfmetrics.registerFont(TTFont('GangGangCN', str(path)))
                return 'GangGangCN'
            except TTFError:
                continue
    return 'Helvetica'


def _clean(value: Any) -> str:
    return str(value or '').replace('\n', '<br/>')


def _percent(value: Any) -> str:
    try:
        return f'{float(value) * 100:.0f}%'
    except (TypeError, ValueError):
        return '0%'


def build_report_pdf(report: dict[str, Any]) -> bytes:
    font_name = _register_font()
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Title'],
        fontName=font_name,
        fontSize=22,
        leading=30,
        textColor=colors.HexColor('#0f172a'),
        alignment=TA_CENTER,
        spaceAfter=10,
    )
    section_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontName=font_name,
        fontSize=13,
        leading=18,
        textColor=colors.HexColor('#1d4ed8'),
        spaceBefore=14,
        spaceAfter=8,
    )
    body_style = ParagraphStyle(
        'BodyCN',
        parent=styles['BodyText'],
        fontName=font_name,
        fontSize=10,
        leading=16,
        textColor=colors.HexColor('#334155'),
    )
    small_style = ParagraphStyle(
        'SmallCN',
        parent=body_style,
        fontSize=9,
        leading=14,
        textColor=colors.HexColor('#475569'),
    )

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title=report.get('title') or 'IP Risk Report',
    )

    story: list[Any] = [
        Paragraph(_clean(report.get('title') or '知识产权风险检测报告'), title_style),
        Paragraph(f'报告编号：{_clean(report.get("id"))}　生成时间：{_clean(report.get("generatedAt"))}', small_style),
        Spacer(1, 8),
    ]

    risk_label = RISK_LABELS.get(report.get('riskLevel'), report.get('riskLevel') or '-')
    risk_table = Table(
        [
            [
                Paragraph(f'风险等级<br/><b>{risk_label}</b>', body_style),
                Paragraph(f'风险分数<br/><b>{report.get("riskScore", 0)}</b>', body_style),
                Paragraph(f'人工复核<br/><b>{REVIEW_LABELS.get(report.get("reviewStatus"), "-")}</b>', body_style),
            ]
        ],
        colWidths=[52 * mm, 52 * mm, 52 * mm],
    )
    risk_table.setStyle(
        TableStyle(
            [
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#eff6ff')),
                ('BOX', (0, 0), (-1, -1), 0.8, colors.HexColor('#bfdbfe')),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#dbeafe')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ]
        )
    )
    story.extend([risk_table, Paragraph('检测结论', section_style), Paragraph(_clean(report.get('summary')), body_style)])

    evidence = report.get('evidence') or []
    if evidence:
        story.append(Paragraph('官方记录与线索', section_style))
        rows = [[Paragraph('名称', small_style), Paragraph('来源', small_style), Paragraph('相似度', small_style)]]
        for item in evidence[:8]:
            rows.append(
                [
                    Paragraph(_clean(item.get('matched')), small_style),
                    Paragraph(_clean(item.get('source')), small_style),
                    Paragraph(_percent(item.get('similarity')), small_style),
                ]
            )
        table = Table(rows, colWidths=[68 * mm, 58 * mm, 30 * mm], repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#fff7ed')),
                    ('BOX', (0, 0), (-1, -1), 0.6, colors.HexColor('#fed7aa')),
                    ('INNERGRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#ffedd5')),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('LEFTPADDING', (0, 0), (-1, -1), 7),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 7),
                    ('TOPPADDING', (0, 0), (-1, -1), 6),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(table)
        for item in evidence[:5]:
            if item.get('description'):
                story.append(Spacer(1, 6))
                story.append(Paragraph(f'<b>{_clean(item.get("matched"))}</b>：{_clean(item.get("description"))}', small_style))

    suggestions = report.get('suggestions') or []
    if suggestions:
        story.append(Paragraph('处理建议', section_style))
        for index, suggestion in enumerate(suggestions, start=1):
            story.append(Paragraph(f'{index}. {_clean(suggestion)}', body_style))
            story.append(Spacer(1, 4))

    if report.get('reviewNote'):
        story.append(Paragraph('人工复核备注', section_style))
        story.append(Paragraph(_clean(report.get('reviewNote')), body_style))

    story.append(Spacer(1, 12))
    story.append(Paragraph('本报告为上架前风险预检结果，不能替代律师法律意见；正式上架前建议结合授权文件、商品类目和平台规则复核。', small_style))

    doc.build(story)
    return buffer.getvalue()
