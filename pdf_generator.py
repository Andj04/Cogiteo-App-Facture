from fpdf import FPDF
from datetime import datetime

def create_pdf(market_name, items_df, total_global, username):
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 10, f"FACTURE - {market_name.upper()}", ln=True, align='C')
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 5, f"Acheteur : {username}", ln=True, align='C')
    pdf.ln(10)
    
    # Infos
    invoice_num = f"FAC-{datetime.now().strftime('%Y%m%d%H%M')}"
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 7, f"Date : {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
    pdf.cell(0, 7, f"Ref : {invoice_num}", ln=True)
    pdf.ln(10)
    
    # Tableau En-têtes
    pdf.set_fill_color(220, 220, 220)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(60, 10, "Produit", 1, 0, 'L', 1)
    pdf.cell(20, 10, "Unite", 1, 0, 'C', 1)
    pdf.cell(20, 10, "Qte", 1, 0, 'C', 1)
    pdf.cell(40, 10, "P.U (FCFA)", 1, 0, 'R', 1)
    pdf.cell(50, 10, "Total (FCFA)", 1, 1, 'R', 1)
    
    # Tableau Données
    pdf.set_font("Arial", "", 10)
    for _, row in items_df.iterrows():
        # On s'assure que les valeurs sont bien formatées
        p = str(row['Produit'])
        u = str(row['Unité'])
        q = row['Quantité']
        pu = row['Prix Unitaire']
        tot = row['Total Article']
        
        pdf.cell(60, 10, p, 1)
        pdf.cell(20, 10, u, 1, 0, 'C')
        pdf.cell(20, 10, str(q), 1, 0, 'C')
        pdf.cell(40, 10, f"{pu:,.0f}", 1, 0, 'R')
        pdf.cell(50, 10, f"{tot:,.0f}", 1, 1, 'R')
            
    # Total Global
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(140, 10, "TOTAL A PAYER", 0, 0, 'R')
    pdf.set_fill_color(50, 200, 50) # Vert
    pdf.cell(50, 10, f"{total_global:,.0f} FCFA", 1, 1, 'R', 1)
    
    filename = f"Facture_{invoice_num}.pdf"
    pdf.output(filename)
    return filename

