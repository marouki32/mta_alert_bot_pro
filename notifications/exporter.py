# notifications/exporter.py

import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

def export_to_excel(csv_path: str, xlsx_path: str):
    """
    Lit data/alerts.csv et exporte en Excel .xlsx
    """
    df = pd.read_csv(csv_path, header=None,
                     names=["timestamp","symbol","score","confidence"])
    df.to_excel(xlsx_path, index=False)
    return xlsx_path

def export_to_pdf(csv_path: str, pdf_path: str, stats: dict):
    """
    Génère un PDF listant les alertes et les statistiques.
    """
    # Lire le CSV
    df = pd.read_csv(csv_path, header=None,
                     names=["timestamp","symbol","score","confidence"])

    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    styles = getSampleStyleSheet()
    flow = []

    # Titre
    flow.append(Paragraph("Rapport d'Alertes", styles['Title']))
    flow.append(Spacer(1,12))

    # Stats
    for k, v in stats.items():
        flow.append(Paragraph(f"<b>{k.replace('_',' ').capitalize()}:</b> {v}", styles['Normal']))
    flow.append(Spacer(1,12))

    # Tableau d’alertes
    data = [df.columns.tolist()] + df.values.tolist()
    table = Table(data)
    flow.append(table)

    doc.build(flow)
    return pdf_path
