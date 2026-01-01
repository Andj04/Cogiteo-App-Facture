import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from PIL import Image

# --- CONFIGURATION ---
DRIVE_FOLDER_ID = "1pxs0MOmITeDtgFw9uA05NZdJJm381y41"
CREDENTIALS_FILE = "credentials.json"

# --- FONCTION GOOGLE DRIVE ---
def upload_to_drive(filepath, filename):
    if not os.path.exists(CREDENTIALS_FILE):
        st.error(f"⚠️ Fichier '{CREDENTIALS_FILE}' introuvable.")
        return False
    try:
        SCOPES = ['https://www.googleapis.com/auth/drive']
        creds = service_account.Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=SCOPES)
        service = build('drive', 'v3', credentials=creds)
        file_metadata = {'name': filename, 'parents': [DRIVE_FOLDER_ID]}
        media = MediaFileUpload(filepath, resumable=True)
        service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return True
    except Exception as e:
        st.error(f"Erreur Drive : {e}")
        return False

# --- FONCTION GÉNÉRATION PDF ---
def generate_invoice_pdf(market_name, items_df, total_amount, invoice_num):
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 10, f"FACTURE FOURNISSEUR - {market_name.upper()}", ln=True, align='C')
    pdf.ln(5)
    
    # Infos
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 7, f"Date : {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True)
    pdf.cell(0, 7, f"N° Facture : {invoice_num}", ln=True)
    pdf.cell(0, 7, f"Devise : Franc CFA (XAF)", ln=True)
    pdf.ln(10)
    
    # Tableau - En-têtes
    pdf.set_fill_color(230, 230, 230)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(55, 10, "Produit", 1, 0, 'L', 1)
    pdf.cell(25, 10, "Unite", 1, 0, 'C', 1)
    pdf.cell(20, 10, "Qte", 1, 0, 'C', 1)
    pdf.cell(40, 10, "Prix Unit.", 1, 0, 'R', 1)
    pdf.cell(50, 10, "Total", 1, 1, 'R', 1)
    
    # Lignes
    pdf.set_font("Arial", "", 10)
    for _, row in items_df.iterrows():
        if row['Produit'] and str(row['Produit']).strip() != "":
            qte = float(row['Quantité'])
            pu = float(row['Prix Unitaire'])
            total_ligne = qte * pu
            
            pdf.cell(55, 10, str(row['Produit']), 1)
            pdf.cell(25, 10, str(row['Unité']), 1, 0, 'C')
            pdf.cell(20, 10, str(qte), 1, 0, 'C')
            pdf.cell(40, 10, f"{pu:,.0f} FCFA", 1, 0, 'R')
            pdf.cell(50, 10, f"{total_ligne:,.0f} FCFA", 1, 1, 'R')
            
    # Total Final
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(140, 10, "MONTANT TOTAL A PAYER", 0, 0, 'R')
    pdf.set_fill_color(255, 200, 0)
    pdf.cell(50, 10, f"{total_amount:,.0f} FCFA", 1, 1, 'R', 1)
    
    filename = f"Facture_{invoice_num}.pdf"
    pdf.output(filename)
    return filename

# --- INTERFACE ---
st.set_page_config(page_title="Resto-Marché", layout="wide")
st.title("👨‍🍳 Resto-Marché : Facturation Fournisseur")

tab1, tab2 = st.tabs(["📝 Nouvelle Facture", "📷 Numérisation Bon/Image"])

with tab1:
    col_a, col_b = st.columns(2)
    with col_a:
        market = st.text_input("Nom du Marché / Grossiste", placeholder="ex: Marché de Treichville")
    with col_b:
        inv_id = f"FAC-{datetime.now().strftime('%y%m%d-%H%M')}"
        st.write(f"**N° Facture généré :** `{inv_id}`")

    # Configuration du tableau de saisie
    st.subheader("Articles achetés")
    
    # On définit les options pour la colonne Unité
    unit_options = ["kg", "pièce", "sac", "carton", "litre", "g", "botte", "casier"]
    
    df_init = pd.DataFrame([
        {"Produit": "", "Unité": "kg", "Quantité": 0.0, "Prix Unitaire": 0.0, "Note": ""},
    ])
    
    edited_df = st.data_editor(
        df_init, 
        num_rows="dynamic", 
        use_container_width=True,
        column_config={
            "Unité": st.column_config.SelectboxColumn("Unité", options=unit_options, required=True),
            "Quantité": st.column_config.NumberColumn("Qté", min_value=0, format="%.2f"),
            "Prix Unitaire": st.column_config.NumberColumn("Prix (FCFA)", min_value=0, format="%d"),
            "Note": st.column_config.TextColumn("Note / Commentaire")
        }
    )

    # Calculs
    total_global = 0
    if not edited_df.empty:
        total_global = (edited_df['Quantité'] * edited_df['Prix Unitaire']).sum()

    st.markdown(f"### Total : `{total_global:,.0f} FCFA`")

    if st.button("🚀 Finaliser et envoyer au Drive"):
        if not market:
            st.error("Veuillez indiquer le nom du marché.")
        elif total_global <= 0:
            st.error("La facture est vide.")
        else:
            with st.spinner("Génération..."):
                fname = generate_invoice_pdf(market, edited_df, total_global, inv_id)
                if upload_to_drive(fname, fname):
                    st.success(f"Facture envoyée sur Drive ! (ID: {inv_id})")
                    os.remove(fname)

with tab2:
    st.header("Transformer une photo en PDF")
    pic = st.file_uploader("Prendre une photo du ticket", type=['jpg', 'jpeg', 'png'])
    if pic:
        img = Image.open(pic)
        st.image(img, width=400)
        if st.button("Convertir & Envoyer"):
            with st.spinner("Traitement..."):
                t_stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                p_name = f"SCAN_{t_stamp}.pdf"
                img.convert('RGB').save("temp.pdf")
                if upload_to_drive("temp.pdf", p_name):
                    st.success("Image envoyée avec succès !")
                    os.remove("temp.pdf")