from fpdf import FPDF
from datetime import datetime, date
import os

def create_pdf(market_name, items_df, total_global, username, invoice_date=None):
    """
    Crée un PDF de facture
    
    Args:
        market_name: Nom du fournisseur/marché
        items_df: DataFrame avec les articles
        total_global: Montant total
        username: Nom de l'utilisateur
        invoice_date: Date de la facture (datetime.date ou None pour aujourd'hui)
    """
    pdf = FPDF()
    pdf.add_page()
    
    # Logo (si disponible)
    logo_path = "Logocogiteowf.png"
    if os.path.exists(logo_path):
        try:
            pdf.image(logo_path, x=10, y=10, w=40)
            pdf.ln(15)  # Espace après le logo
        except:
            pass
    
    # Titre de l'application
    pdf.set_font("Arial", "B", 16)
    pdf.set_text_color(31, 119, 180)  # Bleu Cogiteo
    pdf.cell(0, 8, "COGITEO FACTURES", ln=True, align='C')
    
    # Header Facture
    pdf.set_font("Arial", "B", 18)
    pdf.set_text_color(0, 0, 0)  # Noir
    pdf.cell(0, 10, f"FACTURE - {market_name.upper()}", ln=True, align='C')
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 5, f"Acheteur : {username}", ln=True, align='C')
    pdf.ln(10)
    
    # Infos
    # Utiliser la date fournie ou la date actuelle
    if invoice_date is None:
        invoice_date = datetime.now().date()
    elif isinstance(invoice_date, datetime):
        invoice_date = invoice_date.date()
    
    # Générer le numéro de facture avec la date sélectionnée
    invoice_num = f"FAC-{invoice_date.strftime('%Y%m%d')}{datetime.now().strftime('%H%M')}"
    
    # Formater la date pour l'affichage
    date_str = invoice_date.strftime('%d/%m/%Y')
    time_str = datetime.now().strftime('%H:%M')
    
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 7, f"Date : {date_str} à {time_str}", ln=True)
    pdf.cell(0, 7, f"Ref : {invoice_num}", ln=True)
    pdf.ln(5)
    
    # Section Fournisseur (mise en évidence)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, f"Fournisseur : {market_name}", ln=True)
    pdf.ln(5)
    
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

