import streamlit as st
import pandas as pd
import os
from database import init_db, create_user, check_login, add_to_history, get_user_history
from drive_service import upload_file
from pdf_generator import create_pdf
from PIL import Image
from datetime import datetime

# Initialisation DB
init_db()

# Configuration Page
st.set_page_config(
    page_title="Cogiteo Factures",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour un design professionnel
st.markdown("""
    <style>
    /* Style global */
    .main {
        padding-top: 2rem;
    }
    
    /* Header avec logo */
    .header-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 20px;
        padding: 20px 0;
        margin-bottom: 30px;
        border-bottom: 3px solid #1f77b4;
    }
    
    .logo-img {
        max-height: 80px;
        width: auto;
    }
    
    .app-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin: 0;
        text-align: center;
    }
    
    /* Style pour les sections */
    .section-box {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 20px 0;
    }
    
    /* Style pour les boutons */
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Sidebar améliorée */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
    }
    
    /* Titres */
    h1, h2, h3 {
        color: #1f77b4;
    }
    
    /* Cards pour les informations importantes */
    .info-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        margin: 15px 0;
    }
    
    /* Style pour le total */
    .total-display {
        font-size: 1.8rem;
        font-weight: bold;
        color: #28a745;
        text-align: center;
        padding: 15px;
        background-color: #d4edda;
        border-radius: 8px;
        border: 2px solid #28a745;
    }
    </style>
""", unsafe_allow_html=True)

def load_logo():
    """Charge le logo de l'application"""
    try:
        if os.path.exists("Logocogiteowf.png"):
            return Image.open("Logocogiteowf.png")
        return None
    except:
        return None

def display_header():
    """Affiche le header avec logo et titre"""
    logo = load_logo()
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if logo:
            st.image(logo, width=150)
        st.markdown('<h1 class="app-title">Cogiteo Factures</h1>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; color: #666; font-size: 1.1rem; margin-top: -10px;">Gestion professionnelle de factures</p>', unsafe_allow_html=True)

# --- GESTION SESSION ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ""
if 'calculated_df' not in st.session_state:
    st.session_state['calculated_df'] = None
if 'total_global' not in st.session_state:
    st.session_state['total_global'] = 0
if 'invoice_date' not in st.session_state:
    st.session_state['invoice_date'] = datetime.now().date()

# --- ECRAN DE LOGIN / SIGNUP ---
if not st.session_state['logged_in']:
    display_header()
    
    # Centrer le formulaire de connexion
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("---")
        st.markdown("### 🔐 Connexion")
        
        choice = st.radio(
            "Sélectionnez une option :",
            ["Se connecter", "Créer un compte"],
            horizontal=True,
            label_visibility="visible"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.container():
            username = st.text_input("👤 Nom d'utilisateur", placeholder="Entrez votre nom d'utilisateur")
            password = st.text_input("🔒 Mot de passe", type='password', placeholder="Entrez votre mot de passe")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if choice == "Se connecter":
            if st.button("🚀 Se connecter", use_container_width=True, type="primary"):
                if username and password:
                    if check_login(username, password):
                        st.session_state['logged_in'] = True
                        st.session_state['username'] = username
                        st.rerun()
                    else:
                        st.error("❌ Identifiants incorrects")
                else:
                    st.warning("⚠️ Veuillez remplir tous les champs")
        else:
            if st.button("✨ Créer le compte", use_container_width=True, type="primary"):
                if username and password:
                    if create_user(username, password):
                        st.success("✅ Compte créé avec succès ! Veuillez vous connecter.")
                        st.balloons()
                    else:
                        st.error("❌ Ce nom d'utilisateur existe déjà.")
                else:
                    st.warning("⚠️ Veuillez remplir tous les champs")

# --- APPLICATION PRINCIPALE ---
else:
    # Sidebar
    with st.sidebar:
        logo = load_logo()
        if logo:
            st.image(logo, width=120)
        st.markdown("---")
        
        st.markdown(f"""
        <div style="background-color: #1f77b4; color: white; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
            <h4 style="color: white; margin: 0;">👤 {st.session_state['username']}</h4>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚪 Déconnexion", use_container_width=True):
            st.session_state['logged_in'] = False
            st.session_state['calculated_df'] = None
            st.session_state['total_global'] = 0
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 📂 Historique récent")
        history = get_user_history(st.session_state['username'])
        if not history.empty:
            # Formater l'historique pour un meilleur affichage
            history_display = history[['date', 'market_name', 'total_amount']].copy()
            history_display['total_amount'] = history_display['total_amount'].apply(lambda x: f"{x:,.0f} FCFA")
            history_display.columns = ['Date', 'Fournisseur', 'Montant']
            st.dataframe(history_display, hide_index=True, use_container_width=True)
        else:
            st.info("Aucune facture enregistrée.")

    # Header principal
    display_header()
    
    tab1, tab2 = st.tabs(["📝 Créer Facture", "📷 Scan Photo"])

    # --- ONGLET 1 : SAISIE ---
    with tab1:
        st.markdown("### 📋 Informations de la facture")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            market_name = st.text_input(
                "📍 Nom du Fournisseur / Marché",
                placeholder="Ex: Marché de Treichville, Grossiste ABC...",
                help="Entrez le nom du fournisseur ou du marché"
            )
        with col2:
            invoice_date = st.date_input(
                "📅 Date de la facture",
                value=st.session_state['invoice_date'],
                help="Sélectionnez la date de la facture (par défaut : aujourd'hui)"
            )
            st.session_state['invoice_date'] = invoice_date
        
        st.markdown("---")
        st.markdown("### 🛒 Articles à facturer")
        st.info("💡 Ajoutez vos articles un par un. Cliquez sur 'Valider et Calculer' pour calculer le total.")

        # Configuration du Data Editor
        # On initialise avec 1 ligne vide si c'est la première fois
        default_data = pd.DataFrame([{"Produit": "", "Unité": "kg", "Quantité": 0.0, "Prix Unitaire": 0, "Total Article": 0.0}])
        
        column_cfg = {
            "Unité": st.column_config.SelectboxColumn("Unité", options=["kg", "pièce", "sac", "carton", "litre", "g", "botte"], required=True),
            "Quantité": st.column_config.NumberColumn("Qté", min_value=0, format="%.2f"),
            "Prix Unitaire": st.column_config.NumberColumn("P.U (FCFA)", min_value=0, format="%d"),
            "Total Article": st.column_config.NumberColumn("Total Ligne", disabled=True, format="%d FCFA") # Désactivé car calculé auto
        }

        # L'éditeur de données
        edited_df = st.data_editor(
            default_data, 
            num_rows="dynamic", # Permet d'ajouter des lignes dynamiquement
            column_config=column_cfg, 
            use_container_width=True,
            key="editor"
        )

        # Bouton VALIDER LES CALCULS
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button("🔄 Valider et Calculer Total", use_container_width=True, type="primary"):
                # Nettoyage et Calculs
                clean_df = edited_df[edited_df["Produit"].str.len() > 0].copy()
                if not clean_df.empty:
                    clean_df["Total Article"] = clean_df["Quantité"] * clean_df["Prix Unitaire"]
                    
                    # Mise en mémoire
                    st.session_state['calculated_df'] = clean_df
                    st.session_state['total_global'] = clean_df["Total Article"].sum()
                    
                    st.success("✅ Calculs effectués avec succès !")
                else:
                    st.warning("⚠️ Veuillez ajouter au moins un article")

        # AFFICHAGE DU RÉSULTAT ET GÉNÉRATION
        if st.session_state['calculated_df'] is not None and not st.session_state['calculated_df'].empty:
            st.markdown("---")
            
            # Affichage du total de manière proéminente
            st.markdown(f"""
            <div class="total-display">
                💰 TOTAL GLOBAL : {st.session_state['total_global']:,.0f} FCFA
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Affichage du tableau calculé
            st.markdown("### 📊 Détail des articles")
            st.dataframe(
                st.session_state['calculated_df'],
                use_container_width=True,
                hide_index=True
            )
            
            # Bouton GÉNÉRATION PDF
            st.markdown("---")
            st.markdown("### 📄 Génération de la facture")
            
            col_gen1, col_gen2 = st.columns(2)
            with col_gen1:
                if st.button("📄 Générer la Facture PDF", use_container_width=True, type="primary"):
                    if not market_name:
                        st.error("❌ Veuillez renseigner le nom du fournisseur !")
                    else:
                        with st.spinner("Génération du PDF en cours..."):
                            # Récupérer la date depuis session_state
                            invoice_date = st.session_state.get('invoice_date', datetime.now().date())
                            fname = create_pdf(
                                market_name, 
                                st.session_state['calculated_df'], 
                                st.session_state['total_global'], 
                                st.session_state['username'],
                                invoice_date
                            )
                            
                            # On stocke le nom du fichier généré dans la session pour afficher les boutons d'action
                            st.session_state['current_pdf'] = fname
                            
                            # Ajout à l'historique DB
                            add_to_history(st.session_state['username'], market_name, st.session_state['total_global'], fname)
                            st.success("✅ Facture PDF générée avec succès !")

            # ACTIONS SUR LE PDF GÉNÉRÉ
            if 'current_pdf' in st.session_state and os.path.exists(st.session_state['current_pdf']):
                st.markdown("---")
                st.markdown("### ✨ Actions disponibles")
                
                c1, c2 = st.columns(2)
                with c1:
                    with open(st.session_state['current_pdf'], "rb") as pdf_file:
                        st.download_button(
                            label="📥 Télécharger PDF",
                            data=pdf_file,
                            file_name=st.session_state['current_pdf'],
                            mime="application/pdf",
                            use_container_width=True,
                            type="primary"
                        )
                with c2:
                    if st.button("☁️ Envoyer sur Google Drive", use_container_width=True):
                        with st.spinner("Envoi sur Google Drive en cours..."):
                            if upload_file(st.session_state['current_pdf'], st.session_state['current_pdf']):
                                st.success("✅ Facture envoyée sur Google Drive avec succès !")
                                st.balloons()
                            else:
                                st.error("❌ Erreur lors de l'envoi sur Google Drive.")

    # --- ONGLET 2 : PHOTO ---
    with tab2:
        st.markdown("### 📷 Numérisation de documents")
        st.info("💡 Téléchargez une photo de ticket ou de facture pour la convertir en PDF et l'envoyer sur Google Drive.")
        
        pic = st.file_uploader(
            "Choisir une image",
            type=['jpg', 'jpeg', 'png'],
            help="Formats acceptés : JPG, JPEG, PNG"
        )
        
        if pic:
            col_img1, col_img2, col_img3 = st.columns([1, 2, 1])
            with col_img2:
                img = Image.open(pic)
                st.image(img, width=400, caption="Aperçu de l'image")
                
                if st.button("📄 Convertir en PDF et Envoyer sur Drive", use_container_width=True, type="primary"):
                    with st.spinner("Conversion et envoi en cours..."):
                        try:
                            t_stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                            p_name = f"SCAN_{t_stamp}.pdf"
                            img.convert('RGB').save("temp_scan.pdf")
                            if upload_file("temp_scan.pdf", p_name):
                                st.success("✅ Document converti et envoyé sur Google Drive avec succès !")
                                st.balloons()
                                os.remove("temp_scan.pdf")
                            else:
                                st.error("❌ Erreur lors de l'envoi sur Google Drive.")
                                if os.path.exists("temp_scan.pdf"):
                                    os.remove("temp_scan.pdf")
                        except Exception as e:
                            st.error(f"❌ Erreur : {e}")
                            if os.path.exists("temp_scan.pdf"):
                                os.remove("temp_scan.pdf")

