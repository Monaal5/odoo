import io
from datetime import datetime
from typing import List, Dict, Any
import pandas as pd

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from app.db.database import dict_cursor


class ReportService:
    """Service handling CSV and PDF stock report generation."""

    @staticmethod
    def get_stock_data(conn) -> List[Dict[str, Any]]:
        """
        Fetch current stock on-hand grouped by product and warehouse.
        Joins products and warehouses table to provide human-readable names.
        """
        with dict_cursor(conn) as cur:
            cur.execute(
                """
                SELECT
                    p.sku                   AS "SKU",
                    p.name                  AS "Product",
                    COALESCE(w.name, 'Default Main Warehouse') AS "Warehouse",
                    COALESCE(SUM(sle.qty_delta), 0) AS "Qty",
                    p.reorder_min           AS "ReorderMin"
                FROM products p
                LEFT JOIN stock_ledger_entries sle ON sle.product_id = p.id
                LEFT JOIN warehouses w ON w.id = sle.warehouse_id
                WHERE p.is_active = TRUE
                GROUP BY p.id, p.sku, p.name, w.id, w.name, p.reorder_min
                ORDER BY p.name, "Warehouse"
                """
            )
            rows = [dict(r) for r in cur.fetchall()]

            # Convert numeric types to float/int for safety
            for row in rows:
                row["Qty"] = float(row["Qty"])
                row["ReorderMin"] = float(row.get("ReorderMin") or 0)
                row["IsLowStock"] = (
                    row["Qty"] <= row["ReorderMin"] and row["ReorderMin"] > 0
                ) or row["Qty"] <= 0

            return rows

    @staticmethod
    def generate_stock_csv(conn) -> str:
        """
        Generate CSV export formatted with columns: SKU, Product, Warehouse, Qty.
        Uses pandas for dataframe formatting.
        """
        raw_data = ReportService.get_stock_data(conn)

        if not raw_data:
            df = pd.DataFrame(columns=["SKU", "Product", "Warehouse", "Qty"])
        else:
            df = pd.DataFrame(raw_data)
            df = df[["SKU", "Product", "Warehouse", "Qty"]]

        # Export to CSV string buffer
        output = io.StringIO()
        df.to_csv(output, index=False)
        return output.getvalue()

    @staticmethod
    def generate_stock_pdf(conn) -> bytes:
        """
        Generate a professional PDF stock report using ReportLab.
        Includes Company header, Date, Summary KPIs, Low Stock table, Full Stock table,
        and Signature footer.
        """
        raw_data = ReportService.get_stock_data(conn)

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()

        # Custom Paragraph Styles
        title_style = ParagraphStyle(
            "CompanyTitle",
            parent=styles["Heading1"],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#1e293b"),  # Dark slate
            fontName="Helvetica-Bold",
        )

        subtitle_style = ParagraphStyle(
            "ReportSubtitle",
            parent=styles["Normal"],
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#64748b"),
            fontName="Helvetica",
        )

        section_heading = ParagraphStyle(
            "SectionHeading",
            parent=styles["Heading2"],
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#0f172a"),
            fontName="Helvetica-Bold",
            spaceAfter=6,
        )

        body_style = ParagraphStyle(
            "BodyText",
            parent=styles["Normal"],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#334155"),
        )

        table_header_style = ParagraphStyle(
            "TableHeader",
            parent=styles["Normal"],
            fontSize=9,
            leading=11,
            textColor=colors.white,
            fontName="Helvetica-Bold",
        )

        table_cell_style = ParagraphStyle(
            "TableCell",
            parent=styles["Normal"],
            fontSize=9,
            leading=11,
            textColor=colors.HexColor("#1e293b"),
        )

        alert_cell_style = ParagraphStyle(
            "AlertCell",
            parent=styles["Normal"],
            fontSize=9,
            leading=11,
            textColor=colors.HexColor("#b91c1c"),  # Red text
            fontName="Helvetica-Bold",
        )

        story = []

        # 1. Company Name & Header
        story.append(Paragraph("StockSense IMS", title_style))
        story.append(Paragraph("Real-Time Stock Audit & Inventory Health Report", subtitle_style))
        story.append(Spacer(1, 8))

        report_date = datetime.now().strftime("%B %d, %Y - %H:%M:%S UTC")
        story.append(Paragraph(f"<b>Generated On:</b> {report_date}", body_style))
        story.append(Spacer(1, 10))

        story.append(
            HRFlowable(
                width="100%",
                thickness=1.5,
                color=colors.HexColor("#0284c7"),
                spaceAfter=15,
            )
        )

        # 2. Stock Summary KPIs
        total_skus = len(set(r["SKU"] for r in raw_data)) if raw_data else 0
        total_units = sum(r["Qty"] for r in raw_data) if raw_data else 0
        low_stock_items = [r for r in raw_data if r["IsLowStock"]]

        summary_data = [
            [
                Paragraph("<b>Total SKUs Monitored</b>", body_style),
                Paragraph("<b>Total Stock Units</b>", body_style),
                Paragraph("<b>Low Stock Alerts</b>", body_style),
            ],
            [
                Paragraph(f"<font size=14 color='#0f172a'><b>{total_skus}</b></font>", body_style),
                Paragraph(f"<font size=14 color='#0f172a'><b>{total_units:,.1f}</b></font>", body_style),
                Paragraph(
                    f"<font size=14 color='{'#dc2626' if low_stock_items else '#16a34a'}'><b>{len(low_stock_items)}</b></font>",
                    body_style,
                ),
            ],
        ]
        summary_table = Table(summary_data, colWidths=[2.2 * inch, 2.2 * inch, 2.2 * inch])
        summary_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
                    ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ]
            )
        )
        story.append(summary_table)
        story.append(Spacer(1, 15))

        # 3. Low Stock Alerts Table (if any)
        if low_stock_items:
            story.append(Paragraph("⚠️ Low Stock & Reorder Alerts", section_heading))
            ls_table_data = [
                [
                    Paragraph("SKU", table_header_style),
                    Paragraph("Product Name", table_header_style),
                    Paragraph("Warehouse", table_header_style),
                    Paragraph("Current Qty", table_header_style),
                    Paragraph("Reorder Min", table_header_style),
                ]
            ]
            for item in low_stock_items:
                ls_table_data.append(
                    [
                        Paragraph(str(item["SKU"]), alert_cell_style),
                        Paragraph(str(item["Product"]), alert_cell_style),
                        Paragraph(str(item["Warehouse"]), alert_cell_style),
                        Paragraph(f"{item['Qty']:,.1f}", alert_cell_style),
                        Paragraph(f"{item['ReorderMin']:,.1f}", alert_cell_style),
                    ]
                )

            ls_table = Table(ls_table_data, colWidths=[1.1 * inch, 2.3 * inch, 1.8 * inch, 1.1 * inch, 1.1 * inch])
            ls_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#991b1b")),  # Dark Red Header
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#fca5a5")),
                        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#fecaca")),
                        ("TOPPADDING", (0, 0), (-1, -1), 5),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                    ]
                )
            )
            story.append(ls_table)
            story.append(Spacer(1, 15))

        # 4. Main Inventory Stock Table
        story.append(Paragraph("📦 On-Hand Inventory Summary", section_heading))
        main_table_data = [
            [
                Paragraph("SKU", table_header_style),
                Paragraph("Product Name", table_header_style),
                Paragraph("Warehouse / Location", table_header_style),
                Paragraph("Qty On-Hand", table_header_style),
            ]
        ]

        if not raw_data:
            main_table_data.append(
                [
                    Paragraph("N/A", table_cell_style),
                    Paragraph("No inventory records found", table_cell_style),
                    Paragraph("-", table_cell_style),
                    Paragraph("0", table_cell_style),
                ]
            )
        else:
            for item in raw_data:
                cell_style = alert_cell_style if item["IsLowStock"] else table_cell_style
                main_table_data.append(
                    [
                        Paragraph(str(item["SKU"]), cell_style),
                        Paragraph(str(item["Product"]), cell_style),
                        Paragraph(str(item["Warehouse"]), cell_style),
                        Paragraph(f"{item['Qty']:,.1f}", cell_style),
                    ]
                )

        main_table = Table(main_table_data, colWidths=[1.3 * inch, 2.8 * inch, 2.0 * inch, 1.3 * inch])
        main_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),  # Dark Slate Header
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        story.append(main_table)
        story.append(Spacer(1, 30))

        # 5. Signature Footer
        story.append(
            HRFlowable(
                width="100%",
                thickness=1,
                color=colors.HexColor("#cbd5e1"),
                spaceAfter=15,
            )
        )

        footer_data = [
            [
                Paragraph("<b>Prepared By:</b> StockSense IMS System", body_style),
                Paragraph("<b>Authorized Signature:</b> _______________________", body_style),
            ]
        ]
        footer_table = Table(footer_data, colWidths=[3.7 * inch, 3.7 * inch])
        footer_table.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (0, 0), "LEFT"),
                    ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )
        story.append(footer_table)

        doc.build(story)
        return buffer.getvalue()
