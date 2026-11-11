from io import BytesIO
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


def export_report_pdf_reportlab(tcp: bool, report_data: dict) -> bytes:
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
    story.append(Spacer(1, 18))

    story.append(Paragraph("Uvažujeme poissonovský LQ model prežívania klonogénov s akcelerovanou repopuláciou <br/>(Fowler 1989): "
        "BED = Nd[1+d/(α/β)]-K(t-t_delay).", styles["BodyText"]))
    story.append(Spacer(1, 18))

    summary_data = [
        [
            "Pacient",
        ],
        [
            "Meno, priezvisko",
            ""
        ],
        [
            "Rodné číslo",
            ""
        ],
        [
            "Diagnóza",
            ""
        ],
        [
            "Poznámky",
            ""
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

    ab_tumor = report_data.get('ab_tumor', 0)
    if report_data.get('a_tumor', 0) is not None:
        params = [
            ["Modelové parametre", "Hodnota"],
            ["α/β pre tumor", f"{report_data.get('ab_tumor', 0):.1f}"],
            ["α/β pre OARs", f"{report_data.get('ab_org', 0):.1f}"],
            ["α pre tumor", f"{report_data.get('a_tumor', 0):.1f}"],
            [f"k pre tumor [Gy_{ab_tumor}/d]", f"{report_data.get('k', 0):.2f}"],
            ["t_delay pre tumor [d]", f"{report_data.get('t_delay', 0)}"],
            ["TCP východzia", f"{report_data.get('ref_tcp', 0):.1f}"],
            ["Požadované % predpisovej BED", f"{report_data.get('tumor_control_pct', 0):.1f}%"],
        ]
    else:
        params = [
                ["Modelové parametre", "Hodnota"],
                ["α/β pre tumor", f"{report_data.get('ab_tumor', 0):.1f}"],
                ["α/β pre OARs", f"{report_data.get('ab_org', 0):.1f}"],
                [f"k pre tumor [Gy_{ab_tumor}/d]", f"{report_data.get('k', 0):.2f}"],
                ["t_delay [d]", f"{report_data.get('t_delay', 0)}"],
                ["Požadované % predpisovej BED", f"{report_data.get('tumor_control_pct', 0):.1f}%"]
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
                ("BACKGROUND", (0, len(params)-1), (-1, len(params)-1), colors.yellow),  # Highlight row 5
            ]
        )
    )
    story.append(params_table)
    story.append(Spacer(1, 18))

    params = [
                ["Parametre predpísaného vs. reálneho kurzu", "Hodnota"],
                ["Dávka na frakciu - predpis [Gy]", f"{report_data.get('frakcia_pk', 0):.2f}"],
                ["Počet frakcií - predpis", str(report_data.get("pocet_f_pk", 0))],
                ["Idealny počet dní predpisového kurzu", str(report_data.get("pocet_dni_pk", 0))],
                ["Počet už odžiarených frakcií", str(report_data.get("pocet_f_pred_pauzou", 0))],
                ["Počet navýšených frakcií", str(report_data.get("pocet_f_po_pauze", 0))],
                ["Počet pridaných extra frakcií", str(report_data.get("pocet_pridanych_f", 0))],
                ["Celkový počet dní reálneho kurzu [d]", str(report_data.get("pocet_dni_rk", 0))]
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

    if tcp:
        results = [
            ["Výsledok", "Hodnota"],
            ["Navýšenie a pridanie frakcií", report_data.get("combo_summary", "")],
            [
                "TCP reálna",
                f"{report_data.get('tcp_rk', 0):.2f}",       
            ],
            [
                "TCP %-pokles",
                f"{report_data.get('tcp_rk_perc', 0):.1f}%", 
            ],
            [
                "OARs EQD2 po doplnení dávky",
                f"{report_data.get('eqd2_org_add', 0):.2f}",
            ],
            [
                "OARs EQD2 %-navýšenie", 
                f"{report_data.get('eqd2_org_add_perc', 0):.1f}%"]
        ]
    else:
        results = [
            ["Výsledok", "Hodnota"],
            ["Navýšenie a pridanie frakcií", report_data.get("combo_summary", "")],
            [
                "OARs EQD2 po doplnení dávky [Gy]",
                f"{report_data.get('eqd2_org_add', 0):.2f}",
            ],
            [
                "OARs EQD2 %-navýšenie", 
                f"{report_data.get('eqd2_org_add_perc', 0):.1f}%"]
        ]

    results_table = Table(results, colWidths=[220, 220])
    results_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
                ("GRID", (0, 0), (-1, -1), 0.8, colors.HexColor("#e2e8f0")),
                ("FONTNAME", (0, 0), (-1, -1), font_name),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BACKGROUND", (0, 1), (-1, 1), colors.yellow),  # Highlight row 1
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
            "(c) ÚVN SNP Ružomberok FN",
            styles["BodyText"],
        )
    )

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()