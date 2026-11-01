from io import BytesIO
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


def export_report_pdf_reportlab(report_data: dict) -> bytes:
    font_candidates = (
        Path(__file__).resolve().parent / "fonts" / "DejaVuSans.ttf",
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/dejavu/DejaVuSans.ttf"),
        Path("/usr/local/share/fonts/DejaVuSans.ttf"),
    )
    font_path = next((path for path in font_candidates if path.is_file()), None)
    if font_path is None:
        raise FileNotFoundError(
            "DejaVuSans.ttf not found. Bundle it in a 'fonts' folder next to reporting.py."
        )

    font_name = "ReportDejaVuSans"
    bold_font_name = "ReportDejaVuSans-Bold"
    bold_font_path = font_path.with_name("DejaVuSans-Bold.ttf")

    if font_name not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(font_name, str(font_path)))

    if (
        bold_font_path.is_file()
        and bold_font_name not in pdfmetrics.getRegisteredFontNames()
    ):
        pdfmetrics.registerFont(TTFont(bold_font_name, str(bold_font_path)))

    title_font = bold_font_name if bold_font_path.is_file() else font_name
    registerFontFamily(
        font_name,
        normal=font_name,
        bold=title_font,
        italic=font_name,
        boldItalic=title_font,
    )

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    styles = getSampleStyleSheet()
    styles["Title"].fontName = title_font
    styles["BodyText"].fontName = font_name
    styles["Italic"].fontName = font_name
    story = []

    story.append(
        Paragraph(
            report_data.get("title", "Doplnok dávky rádioterapie"),
            styles["Title"],
        )
    )
    story.append(Spacer(1, 12))
    story.append(
        Paragraph(
            report_data.get("subtitle", "Report z aplikácie"),
            styles["BodyText"],
        )
    )
    story.append(Spacer(1, 18))

    summary_data = [
        [
            "Predpísaná tumor BED",
            f"{report_data.get('bed_tumor_pk', 0):.2f} Gy_{report_data.get('ab_tumor', 0):.1f}",
        ],
        [
            "Predpísaná OARs BED",
            f"{report_data.get('bed_org_pk', 0):.2f} Gy_{report_data.get('ab_org', 0):.1f}",
        ],
        [
            "Tumor BED s manažmentom",
            f"{report_data.get('bed_tumor_rk', 0):.2f} Gy_{report_data.get('ab_tumor', 0):.1f}",
        ],
        [
            "OARs BED s manažmentom",
            f"{report_data.get('bed_org_add', 0):.2f} Gy_{report_data.get('ab_org', 0):.1f}",
        ],
    ]

    summary_table = Table(summary_data, colWidths=[220, 220])
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
                ("GRID", (0, 0), (-1, -1), 0.8, colors.HexColor("#dfe7ee")),
                ("FONTNAME", (0, 0), (-1, -1), font_name),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(summary_table)
    story.append(Spacer(1, 18))

    params = [
        ["Parameter", "Hodnota"],
        ["α/β pre tumor", f"{report_data.get('ab_tumor', 0):.1f}"],
        ["α/β pre OAR", f"{report_data.get('ab_org', 0):.1f}"],
        ["k pre tumor", f"{report_data.get('k', 0):.2f}"],
        ["t_delay", f"{report_data.get('t_delay', 0)} dní"],
        ["Dávka na frakciu", f"{report_data.get('frakcia_pk', 0):.2f} Gy"],
        ["Počet frakcií", str(report_data.get("pocet_f_pk", 0))],
        ["Počet dní kurzu", str(report_data.get("pocet_dni_pk", 0))],
        ["Počet odžiarených frakcií", str(report_data.get("pocet_f_pred_pauzou", 0))],
        ["Počet frakcií po pauze", str(report_data.get("pocet_f_po_pauze", 0))],
        ["Počet pridaných extra frakcií", str(report_data.get("pocet_pridanych_f", 0))],
        ["Celkový počet dní kurzu", str(report_data.get("pocet_dni_rk", 0))],
        ["Požadovaná BED", f"{report_data.get('tumor_control_pct', 0):.1f}%"],
    ]

    params_table = Table(params, colWidths=[220, 220])
    params_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
                ("GRID", (0, 0), (-1, -1), 0.8, colors.HexColor("#e2e8f0")),
                ("FONTNAME", (0, 0), (-1, -1), font_name),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    story.append(params_table)
    story.append(Spacer(1, 18))

    results = [
        ["Výsledok", "Hodnota"],
        ["Navýšenie frakcií a doplnok po pauze", report_data.get("combo_summary", "")],
        [
            "BED tumor s manažmentom",
            f"{report_data.get('bed_tumor_rk', 0):.2f} Gy_{report_data.get('ab_tumor', 0):.1f}",
        ],
        [
            "BED tumor bez manažmentu",
            f"{report_data.get('bed_tumor_rk_bezm', 0):.2f} Gy_{report_data.get('ab_tumor', 0):.1f}",
        ],
        [
            "OARs BED s manažmentom",
            f"{report_data.get('bed_org_add', 0):.2f} Gy_{report_data.get('ab_org', 0):.1f}",
        ],
        ["OARs navýšenie", f"{report_data.get('bed_org_navyse_perc', 0):.1f}%"],
        [
            "Zmena tumor BED vs. predpis",
            f"{report_data.get('bed_tumor_ponize_perc', 0):.1f}%",
        ],
    ]

    if report_data.get("tcp_rows"):
        results.append(["TCP reálneho kurzu", report_data["tcp_rows"]])

    results_table = Table(results, colWidths=[220, 220])
    results_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
                ("GRID", (0, 0), (-1, -1), 0.8, colors.HexColor("#e2e8f0")),
                ("FONTNAME", (0, 0), (-1, -1), font_name),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    story.append(results_table)

    warnings = report_data.get("warnings_html", "")
    if warnings:
        story.append(Spacer(1, 12))
        story.append(Paragraph(warnings, styles["Italic"]))

    story.append(Spacer(1, 16))
    story.append(
        Paragraph(
            "(c) Radoslav Paučo, ÚVN SNP Ružomberok FN, paucor@uvn.sk",
            styles["BodyText"],
        )
    )

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()