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

# CSS personnalisé pour un design moderne inspiré de l'UI mobile
st.markdown("""
    <style>
    /* Variables de couleurs */
    :root {
        --primary-blue: #1f77b4;
        --light-blue: #e3f2fd;
        --dark-blue: #1565c0;
        --success-green: #28a745;
        --warning-yellow: #ffc107;
        --text-dark: #212529;
        --text-gray: #6c757d;
        --bg-light: #f8f9fa;
        --border-color: #dee2e6;
    }
    
    /* Style global */
    .main {
        padding-top: 1rem;
        background-color: #ffffff;
    }
    
    /* Header moderne */
    .app-header {
        text-align: center;
        padding: 30px 0;
        margin-bottom: 40px;
    }
    
    .logo-container {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: var(--light-blue);
        border-radius: 16px;
        padding: 12px;
        margin-bottom: 15px;
    }
    
    .app-title {
        font-size: 2rem;
        font-weight: 700;
        color: var(--primary-blue);
        margin: 10px 0;
        letter-spacing: -0.5px;
    }
    
    .app-subtitle {
        font-size: 1.2rem;
        color: var(--text-gray);
        margin-top: -5px;
        font-weight: 400;
    }
    
    /* Cards modernes */
    .modern-card {
        background: white;
        border-radius: 16px;
        padding: 24px;
        margin: 20px 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid var(--border-color);
        transition: all 0.3s ease;
    }
    
    .modern-card:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.12);
        transform: translateY(-2px);
    }
    
    .card-primary {
        background: linear-gradient(135deg, var(--primary-blue) 0%, var(--dark-blue) 100%);
        color: white;
    }
    
    .card-success {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
    }
    
    /* Formulaire de connexion moderne */
    .login-container {
        max-width: 420px;
        margin: 0 auto;
        padding: 40px 30px;
    }
    
    .input-icon {
        position: relative;
    }
    
    /* Boutons modernes */
    .stButton>button {
        border-radius: 12px;
        font-weight: 600;
        padding: 12px 24px;
        transition: all 0.3s ease;
        border: none;
        font-size: 1rem;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(31, 119, 180, 0.3);
    }
    
    /* Bouton primaire */
    button[kind="primary"] {
        background: var(--primary-blue);
        color: white;
    }
    
    /* Total estimé bar */
    .total-bar {
        background: var(--light-blue);
        padding: 16px 24px;
        border-radius: 12px;
        margin: 20px 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-left: 4px solid var(--primary-blue);
    }
    
    .total-amount {
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--primary-blue);
    }
    
    /* Tableau moderne */
    .dataframe {
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* Badge de statut */
    .status-badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    .badge-success {
        background: #d4edda;
        color: #155724;
    }
    
    .badge-warning {
        background: #fff3cd;
        color: #856404;
    }
    
    /* Sidebar moderne */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, var(--bg-light) 100%);
    }
    
    /* Titres */
    h1, h2, h3 {
        color: var(--text-dark);
        font-weight: 700;
    }
    
    /* Séparateur OU */
    .divider-or {
        display: flex;
        align-items: center;
        text-align: center;
        margin: 20px 0;
        color: var(--text-gray);
    }
    
    .divider-or::before,
    .divider-or::after {
        content: '';
        flex: 1;
        border-bottom: 1px solid var(--border-color);
    }
    
    .divider-or span {
        padding: 0 15px;
        font-weight: 500;
    }
    
    /* Section bienvenue */
    .welcome-section {
        padding: 20px 0;
        margin-bottom: 30px;
    }
    
    .welcome-greeting {
        color: var(--text-gray);
        font-size: 1rem;
        margin-bottom: 5px;
    }
    
    .welcome-title {
        font-size: 2rem;
        font-weight: 700;
        color: var(--text-dark);
        margin: 0;
    }
    
    /* Cards d'action */
    .action-card {
        background: white;
        border-radius: 16px;
        padding: 24px;
        margin: 15px 0;
        border: 2px solid var(--border-color);
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .action-card:hover {
        border-color: var(--primary-blue);
        box-shadow: 0 4px 16px rgba(31, 119, 180, 0.15);
    }
    
    .action-card.primary {
        background: linear-gradient(135deg, var(--primary-blue) 0%, var(--dark-blue) 100%);
        color: white;
        border: none;
    }
    
    /* Historique amélioré */
    .history-item {
        background: white;
        border-radius: 12px;
        padding: 16px;
        margin: 10px 0;
        border-left: 4px solid var(--primary-blue);
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Footer */
    .app-footer {
        text-align: center;
        padding: 30px 0;
        margin-top: 50px;
        border-top: 1px solid var(--border-color);
        color: var(--text-gray);
        font-size: 0.9rem;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
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
    st.markdown('<div class="app-header">', unsafe_allow_html=True)
    if logo:
        st.markdown('<div class="logo-container">', unsafe_allow_html=True)
        st.image(logo, width=60)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-title">COGITEO MARKET</div>', unsafe_allow_html=True)
    st.markdown('<div class="app-subtitle">Simplifiez vos achats au marché</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

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
    
    # Formulaire de connexion moderne centré
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        # Onglets Se connecter / Créer un compte
        choice = st.radio(
            " ",
            ["Se connecter", "Créer un compte"],
            horizontal=True,
            label_visibility="hidden"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Champs du formulaire
        username = st.text_input(
            "Email professionnel",
            placeholder="nom@restaurant.com",
            label_visibility="visible"
        )
        
        col_pass1, col_pass2 = st.columns([3, 1])
        with col_pass1:
            password = st.text_input(
                "Mot de passe",
                type='password',
                placeholder="••••••••",
                label_visibility="visible"
            )
        with col_pass2:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div style="text-align: right; color: #1f77b4; font-size: 0.9rem; padding-top: 0.5rem;">Oublié ?</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Bouton de connexion/création
        if choice == "Se connecter":
            if st.button("Se connecter", use_container_width=True, type="primary"):
                if username and password:
                    if check_login(username, password):
                        st.session_state['logged_in'] = True
                        st.session_state['username'] = username
                        st.rerun()
                    else:
                        st.error("Identifiants incorrects")
                else:
                    st.warning("Veuillez remplir tous les champs")
        else:
            if st.button("Créer le compte", use_container_width=True, type="primary"):
                if username and password:
                    if create_user(username, password):
                        st.success("✅ Compte créé avec succès ! Veuillez vous connecter.")
                        st.balloons()
                    else:
                        st.error("Ce nom d'utilisateur existe déjà.")
                else:
                    st.warning("Veuillez remplir tous les champs")
        
        # Séparateur OU
        st.markdown('<div class="divider-or"><span>OU</span></div>', unsafe_allow_html=True)
        
        # Bouton Google Drive
        if st.button("🔵 Continuer avec Google Drive", use_container_width=True):
            st.info("💡 Vos factures sont stockées directement sur votre Drive personnel")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown('<div class="app-footer">', unsafe_allow_html=True)
    col_f1, col_f2, col_f3 = st.columns([1, 2, 1])
    with col_f2:
        st.markdown('[Politique de confidentialité](/) • [Mentions légales](/)', unsafe_allow_html=True)
        st.markdown('<div style="margin-top: 10px; color: #6c757d;">COGITEO MARKET © 2024</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- APPLICATION PRINCIPALE ---
else:
    # Sidebar moderne
    with st.sidebar:
        logo = load_logo()
        if logo:
            st.image(logo, width=80)
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Profil utilisateur
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1f77b4 0%, #1565c0 100%); color: white; padding: 20px; border-radius: 12px; margin-bottom: 25px; text-align: center;">
            <div style="background: rgba(255,255,255,0.2); width: 60px; height: 60px; border-radius: 50%; margin: 0 auto 10px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem;">👤</div>
            <h4 style="color: white; margin: 0; font-size: 1.1rem;">{st.session_state['username']}</h4>
            <div style="background: #28a745; width: 12px; height: 12px; border-radius: 50%; margin: 8px auto 0; border: 2px solid white;"></div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚪 Déconnexion", use_container_width=True):
            st.session_state['logged_in'] = False
            st.session_state['calculated_df'] = None
            st.session_state['total_global'] = 0
            st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Historique stylisé
        st.markdown("### 📂 Activités Récentes")
        st.markdown('<div style="text-align: right; margin-bottom: 10px;"><a href="#" style="color: #1f77b4; text-decoration: none; font-size: 0.9rem;">Voir tout →</a></div>', unsafe_allow_html=True)
        
        history = get_user_history(st.session_state['username'])
        if not history.empty:
            # Limiter à 5 dernières factures
            history_display = history.head(5)
            
            for idx, row in history_display.iterrows():
                # Déterminer le badge de statut
                status = "Validé"
                badge_class = "badge-success"
                
                # Formater la date
                date_str = str(row.get('date', 'N/A'))
                if ' ' in date_str:
                    date_str = date_str.split()[0]
                
                market = str(row.get('market_name', 'N/A'))
                filename = str(row.get('filename', 'N/A')).replace('Facture_', '')
                total = float(row.get('total_amount', 0))
                
                st.markdown(f"""
                <div class="history-item">
                    <div style="display: flex; align-items: start; gap: 12px;">
                        <div style="background: #dc3545; color: white; width: 40px; height: 40px; border-radius: 8px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 0.8rem;">PDF</div>
                        <div style="flex: 1;">
                            <div style="font-weight: 700; color: #212529; margin-bottom: 4px;">{market}</div>
                            <div style="color: #6c757d; font-size: 0.85rem; margin-bottom: 8px;">{date_str} • #{filename}</div>
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <span class="status-badge {badge_class}">{status}</span>
                                <span style="font-weight: 700; color: #212529;">{total:,.0f} FCFA</span>
                            </div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align: center; padding: 40px 20px; color: #6c757d;">
                <div style="font-size: 3rem; margin-bottom: 10px;">📄</div>
                <div>Aucune facture enregistrée</div>
            </div>
            """, unsafe_allow_html=True)

    # Page d'accueil avec cartes d'action
    st.markdown('<div class="welcome-section">', unsafe_allow_html=True)
    st.markdown(f'<div class="welcome-greeting">Bonjour, {st.session_state["username"]} 👋</div>', unsafe_allow_html=True)
    st.markdown('<div class="welcome-title">Gérez vos factures</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Cartes d'action principales
    col_action1, col_action2 = st.columns(2)
    with col_action1:
        st.markdown("""
        <div class="modern-card">
            <h3 style="margin-top: 0; color: #212529;">📝 Saisie Rapide</h3>
            <p style="color: #6c757d; margin-bottom: 15px;">Créer une nouvelle facture</p>
            <div style="background: #e3f2fd; padding: 8px; border-radius: 8px; text-align: center; color: #1f77b4; font-weight: 600;">Manuel</div>
        </div>
        """, unsafe_allow_html=True)
    with col_action2:
        st.markdown("""
        <div class="modern-card card-primary" style="color: white;">
            <h3 style="margin-top: 0; color: white;">📷 Scanner une photo</h3>
            <p style="margin-bottom: 15px; opacity: 0.9;">Ticket ou bon papier</p>
            <span style="background: rgba(255,255,255,0.2); padding: 6px 12px; border-radius: 20px; font-size: 0.85rem; font-weight: 600;">Recommandé</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["📝 Créer Facture", "📷 Scan Photo"])

    # --- ONGLET 1 : SAISIE ---
    with tab1:
        st.markdown('<div class="modern-card">', unsafe_allow_html=True)
        st.markdown("### 📋 Nouvelle Facture")
        
        # Nom du marché
        market_name = st.text_input(
            "Nom du Marché / Grossiste",
            placeholder="ex: Marché Central",
            help="Entrez le nom du fournisseur ou du marché"
        )
        
        # Dates
        col_date1, col_date2 = st.columns(2)
        with col_date1:
            invoice_date = st.date_input(
                "Date de création",
                value=st.session_state['invoice_date'],
                help="Date de création de la facture"
            )
            st.session_state['invoice_date'] = invoice_date
        with col_date2:
            delivery_date = st.date_input(
                "Date de livraison (optionnel)",
                value=st.session_state['invoice_date'],
                help="Date de livraison prévue"
            )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Section articles
        col_art1, col_art2 = st.columns([3, 1])
        with col_art1:
            st.markdown("### 🛒 Articles Achetés")
        with col_art2:
            if st.button("🔄 Historique", use_container_width=True):
                pass  # Action à implémenter
        
        st.markdown('<div style="margin-bottom: 15px; color: #6c757d;">Ajoutez vos articles ci-dessous</div>', unsafe_allow_html=True)

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

        # Total estimé en haut (calcul en temps réel)
        if not edited_df.empty:
            current_total = (edited_df['Quantité'] * edited_df['Prix Unitaire']).sum()
            if current_total > 0:
                st.markdown(f"""
                <div class="total-bar">
                    <span style="font-weight: 600; color: #212529;">Total estimé</span>
                    <span class="total-amount">{current_total:,.0f} FCFA</span>
                </div>
                """, unsafe_allow_html=True)
        
        # Bouton ajouter une ligne (visuellement intégré)
        if st.button("➕ Ajouter une ligne", use_container_width=False):
            st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Bouton VALIDER LES CALCULS
        if st.button("🔄 Valider et Calculer Total", use_container_width=True, type="secondary"):
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
            <div class="total-bar">
                <span style="font-weight: 700; color: #212529; font-size: 1.2rem;">TOTAL A PAYER</span>
                <span class="total-amount" style="font-size: 1.8rem;">{st.session_state['total_global']:,.0f} FCFA</span>
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
            
            # Bouton GÉNÉRATION PDF - Style moderne
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("✅ VALIDER ET ENVOYER AU DRIVE", use_container_width=True, type="primary"):
                if not market_name:
                    st.error("❌ Veuillez renseigner le nom du fournisseur !")
                else:
                    with st.spinner("Génération et envoi en cours..."):
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
                        
                        # Upload automatique sur Drive
                        if upload_file(fname, fname):
                            st.success("✅ Facture générée et envoyée sur Google Drive avec succès !")
                            st.balloons()
                        else:
                            st.warning("⚠️ Facture générée mais erreur lors de l'envoi sur Drive. Vous pouvez la télécharger ci-dessous.")

            # ACTIONS SUR LE PDF GÉNÉRÉ
            if 'current_pdf' in st.session_state and os.path.exists(st.session_state['current_pdf']):
                st.markdown("---")
                with open(st.session_state['current_pdf'], "rb") as pdf_file:
                    st.download_button(
                        label="📥 Télécharger la facture PDF",
                        data=pdf_file,
                        file_name=st.session_state['current_pdf'],
                        mime="application/pdf",
                        use_container_width=True,
                        type="secondary"
                    )

    # --- ONGLET 2 : PHOTO ---
    with tab2:
        st.markdown("### 📷 Numériser un justificatif")
        
        # Zone de scan stylisée
        st.markdown("""
        <div style="background: #f8f9fa; border-radius: 16px; padding: 60px 20px; text-align: center; margin: 30px 0; border: 2px dashed #dee2e6; position: relative;">
            <div style="position: absolute; top: 20px; right: 20px; background: white; border-radius: 50%; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                ⚡
            </div>
            <div style="background: white; border-radius: 50%; width: 80px; height: 80px; margin: 0 auto 20px; display: flex; align-items: center; justify-content: center; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                📄
            </div>
            <h3 style="color: #1f77b4; margin: 10px 0;">Cadrez le ticket ou le bon</h3>
            <p style="color: #6c757d; margin: 5px 0;">Assurez-vous que le document est bien éclairé et lisible.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col_scan1, col_scan2, col_scan3 = st.columns([1, 2, 1])
        with col_scan2:
            pic = st.file_uploader(
                "Choisir une image",
                type=['jpg', 'jpeg', 'png'],
                help="Formats acceptés : JPG, JPEG, PNG",
                label_visibility="collapsed"
            )
            
            if pic:
                img = Image.open(pic)
                st.image(img, width=400, caption="Aperçu de l'image")
                
                col_gal1, col_gal2, col_gal3 = st.columns([1, 2, 1])
                with col_gal2:
                    if st.button("📄 Convertir et Envoyer sur Drive", use_container_width=True, type="primary"):
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

