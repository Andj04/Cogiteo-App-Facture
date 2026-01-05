import streamlit as st
import pandas as pd
import os
from database import init_db, create_user, check_login, add_to_history, get_user_history
from drive_service import upload_file, get_drive_service
from pdf_generator import create_pdf
from PIL import Image
from datetime import datetime, date

# Initialisation DB
init_db()

# Configuration Page
st.set_page_config(
    page_title="Cogiteo Market",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialisation session state
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ""
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = "tableau_de_bord"
if 'calculated_df' not in st.session_state:
    st.session_state['calculated_df'] = None
if 'total_global' not in st.session_state:
    st.session_state['total_global'] = 0
if 'invoice_date' not in st.session_state:
    st.session_state['invoice_date'] = date.today()
if 'delivery_date' not in st.session_state:
    st.session_state['delivery_date'] = date.today()
if 'editor_key' not in st.session_state:
    st.session_state['editor_key'] = 0
if 'signup_mode' not in st.session_state:
    st.session_state['signup_mode'] = False

# CSS personnalisé
st.markdown("""
    <style>
    /* Masquer les éléments Streamlit par défaut */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Variables */
    :root {
        --primary-blue: #1f77b4;
        --primary-green: #28a745;
        --dark-blue: #1565c0;
        --light-blue: #e3f2fd;
        --bg-gray: #f8f9fa;
        --text-dark: #212529;
        --text-gray: #6c757d;
        --border-color: #dee2e6;
        --success-green: #28a745;
    }
    
    /* Header gradient */
    .gradient-header {
        height: 60px;
        background: linear-gradient(90deg, #1f77b4 0%, #28a745 100%);
        width: 100%;
        margin: -1rem -1rem 2rem -1rem;
        padding: 0;
    }
    
    /* Logo container */
    .logo-header {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 15px 0;
    }
    
    /* Navigation bar */
    .nav-bar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 15px 30px;
        background: white;
        border-bottom: 1px solid var(--border-color);
        margin: -1rem -1rem 2rem -1rem;
    }
    
    .nav-links {
        display: flex;
        gap: 30px;
        align-items: center;
    }
    
    .nav-link {
        color: var(--text-gray);
        text-decoration: none;
        font-weight: 500;
        padding: 8px 0;
        border-bottom: 2px solid transparent;
        transition: all 0.3s;
    }
    
    .nav-link:hover {
        color: var(--primary-blue);
        border-bottom-color: var(--primary-blue);
    }
    
    .nav-link.active {
        color: var(--primary-blue);
        border-bottom-color: var(--primary-blue);
    }
    
    /* Cards */
    .info-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin: 20px 0;
        border: 2px solid #28a745;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    .info-card-title {
        display: flex;
        align-items: center;
        gap: 10px;
        color: #28a745;
        font-weight: 600;
        font-size: 1.1rem;
        margin-bottom: 15px;
    }
    
    /* Footer facture */
    .invoice-footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: white;
        padding: 20px 30px;
        border-top: 1px solid var(--border-color);
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
        display: flex;
        justify-content: space-between;
        align-items: center;
        z-index: 1000;
    }
    
    /* Bouton primaire vert */
    button[kind="primary"] {
        background: var(--primary-green) !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
    }
    
    button[kind="primary"]:hover {
        background: #218838 !important;
    }
    
    /* Input styling */
    .stTextInput>div>div>input {
        border-radius: 8px;
    }
    
    .stSelectbox>div>div>select {
        border-radius: 8px;
    }
    
    /* Table styling */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Status badges */
    .badge {
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
    }
    
    .badge-validated {
        background: #d4edda;
        color: #155724;
    }
    
    .badge-pending {
        background: #fff3cd;
        color: #856404;
    }
    
    .badge-cancelled {
        background: #f8d7da;
        color: #721c24;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: #f8f9fa;
    }
    
    /* Scroll area for main content when footer is fixed */
    .main-content {
        padding-bottom: 120px;
    }
    
    /* Google Drive button */
    .google-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
        background: white;
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 12px 20px;
        width: 100%;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s;
    }
    
    .google-btn:hover {
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-color: var(--primary-blue);
    }
    
    /* Login page styling */
    .login-page {
        max-width: 450px;
        margin: 0 auto;
        padding: 40px 20px;
    }
    
    .login-header {
        text-align: center;
        margin-bottom: 40px;
    }
    
    .login-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--text-dark);
        margin: 20px 0 10px;
    }
    
    .login-subtitle {
        color: var(--text-gray);
        font-size: 1rem;
    }
    
    .divider-or {
        display: flex;
        align-items: center;
        text-align: center;
        margin: 30px 0;
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
        font-size: 0.9rem;
    }
    
    .footer-login {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 50px;
        padding-top: 20px;
        border-top: 1px solid var(--border-color);
        color: var(--text-gray);
        font-size: 0.9rem;
    }
    
    .footer-login-item {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* Webcam area */
    .webcam-container {
        background: #1f77b4;
        border-radius: 12px;
        padding: 40px;
        text-align: center;
        min-height: 400px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        position: relative;
    }
    
    .webcam-frame {
        border: 2px dashed rgba(255,255,255,0.5);
        border-radius: 8px;
        padding: 60px 40px;
        margin: 20px 0;
    }
    
    .live-indicator {
        position: absolute;
        top: 20px;
        left: 20px;
        background: rgba(220, 53, 69, 0.9);
        color: white;
        padding: 5px 12px;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    
    .capture-controls {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin-top: 30px;
    }
    
    .capture-btn {
        width: 70px;
        height: 70px;
        border-radius: 50%;
        background: white;
        border: 4px solid rgba(255,255,255,0.3);
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
    }
    
    </style>
""", unsafe_allow_html=True)

def load_logo():
    """Charge le logo de l'application"""
    logo_path = "Logocogiteowf.png"
    if os.path.exists(logo_path):
        return logo_path
    return None

def render_login_page():
    """Page de connexion selon le design"""
    # Gradient header
    st.markdown('<div class="gradient-header"></div>', unsafe_allow_html=True)
    
    col_logo, col_empty = st.columns([1, 3])
    with col_logo:
        logo = load_logo()
        if logo:
            st.image(logo, width=120)
    
    st.markdown('<div class="login-page">', unsafe_allow_html=True)
    
    # Header text
    st.markdown("""
    <div class="login-header">
        <h1 class="login-title">Simplifiez vos achats au marché</h1>
        <p class="login-subtitle">Connectez-vous pour gérer vos commandes et factures</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Bouton Google Drive
    if st.button("🔵 Se connecter avec Google Drive", use_container_width=True, type="primary"):
        # Tentative de connexion Google Drive
        service = get_drive_service()
        if service:
            st.success("✅ Connexion Google Drive réussie !")
            st.session_state['google_connected'] = True
        else:
            st.info("💡 Vous serez redirigé vers Google pour l'autorisation")")
    
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 8px; margin: 15px 0; justify-content: center; color: var(--primary-green);">
        <span style="font-size: 1.2rem;">✓</span>
        <span style="font-size: 0.9rem; font-weight: 500;">Vos factures sont stockées directement sur votre Drive personnel</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Séparateur
    st.markdown('<div class="divider-or"><span>OU AVEC EMAIL</span></div>', unsafe_allow_html=True)
    
    # Formulaire email
    col_email1, col_email2 = st.columns([1, 20])
    with col_email2:
        st.markdown('<span style="font-size: 1.5rem;">✉️</span>', unsafe_allow_html=True)
    
    username = st.text_input(
        "Email",
        placeholder="exemple@restaurant.com",
        label_visibility="visible",
        key="login_email"
    )
    
    col_pass1, col_pass2, col_pass3 = st.columns([1, 15, 4])
    with col_pass2:
        st.markdown('<span style="font-size: 1.5rem;">🔒</span>', unsafe_allow_html=True)
    
    password = st.text_input(
        "Mot de passe",
        type='password',
        placeholder="••••••••",
        label_visibility="visible",
        key="login_password"
    )
    
    col_link1, col_link2 = st.columns([3, 1])
    with col_link2:
        st.markdown('<div style="text-align: right; margin-top: -10px;"><a href="#" style="color: var(--primary-blue); text-decoration: none; font-size: 0.9rem;">Mot de passe oublié ?</a></div>', unsafe_allow_html=True)
    
    # Bouton connexion
    if st.session_state.get('signup_mode', False):
        if st.button("S'inscrire", use_container_width=True, type="primary"):
            if username and password:
                if create_user(username, password):
                    st.success("✅ Compte créé avec succès !")
                    st.session_state['signup_mode'] = False
                    st.rerun()
                else:
                    st.error("❌ Ce nom d'utilisateur existe déjà.")
            else:
                st.warning("⚠️ Veuillez remplir tous les champs")
    else:
        if st.button("Se connecter", use_container_width=True, type="primary"):
            if username and password:
                if check_login(username, password):
                    st.session_state['logged_in'] = True
                    st.session_state['username'] = username
                    st.session_state['current_page'] = "tableau_de_bord"
                    st.rerun()
                else:
                    st.error("❌ Identifiants incorrects")
            else:
                st.warning("⚠️ Veuillez remplir tous les champs")
    
    # Lien s'inscrire
    st.markdown('<div style="text-align: center; margin-top: 20px; color: var(--text-gray);">Vous n\'avez pas de compte ? <span style="color: var(--primary-blue); font-weight: 600;">S\'inscrire</span></div>', unsafe_allow_html=True)
    
    col_sign1, col_sign2 = st.columns([1, 1])
    with col_sign2:
        if st.button("S'inscrire", key="signup_toggle", use_container_width=True, type="secondary"):
            st.session_state['signup_mode'] = not st.session_state.get('signup_mode', False)
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("""
    <div class="footer-login">
        <div class="footer-login-item">
            <span>🔒</span>
            <span>Connexion sécurisée</span>
        </div>
        <div class="footer-login-item">
            <span>❓</span>
            <span>Support</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_navigation():
    """Navigation principale"""
    pages = {
        "tableau_de_bord": "📊 Tableau de bord",
        "factures": "📄 Factures",
        "fournisseurs": "🏪 Fournisseurs",
        "parametres": "⚙️ Paramètres"
    }
    
    selected = st.selectbox(
        "Navigation",
        options=list(pages.keys()),
        format_func=lambda x: pages[x],
        key="nav_select",
        label_visibility="collapsed"
    )
    
    st.session_state['current_page'] = selected
    return selected

def render_sidebar():
    """Sidebar avec logo et navigation"""
    logo = load_logo()
    if logo:
        st.image(logo, width=120)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Menu navigation
    menu_items = {
        "tableau_de_bord": ("📊", "Tableau de bord"),
        "factures": ("📄", "Factures"),
        "fournisseurs": ("🏪", "Fournisseurs"),
        "parametres": ("⚙️", "Paramètres")
    }
    
    for page_key, (icon, label) in menu_items.items():
        if st.button(f"{icon} {label}", key=f"nav_{page_key}", use_container_width=True):
            st.session_state['current_page'] = page_key
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()
    
    # Profil utilisateur
    st.markdown(f"""
    <div style="text-align: center; padding: 20px 0;">
        <div style="background: var(--primary-blue); color: white; width: 50px; height: 50px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-size: 1.5rem; font-weight: bold; margin-bottom: 10px;">
            {st.session_state['username'][0].upper() if st.session_state['username'] else 'U'}
        </div>
        <div style="font-weight: 600; color: var(--text-dark);">{st.session_state['username']}</div>
        <div style="color: var(--text-gray); font-size: 0.9rem;">Utilisateur</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚪 Déconnexion", use_container_width=True):
        st.session_state['logged_in'] = False
        st.session_state['calculated_df'] = None
        st.session_state['total_global'] = 0
        st.session_state['current_page'] = "tableau_de_bord"
        st.rerun()

def render_tableau_de_bord():
    """Page tableau de bord"""
    st.title("📊 Tableau de bord")
    st.markdown("Bienvenue sur votre tableau de bord")
    
    # Statistiques rapides
    history = get_user_history(st.session_state['username'])
    if not history.empty:
        total_factures = len(history)
        total_amount = history['total_amount'].sum()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Factures", total_factures)
        with col2:
            st.metric("Montant Total", f"{total_amount:,.0f} FCFA")
        with col3:
            st.metric("Dernière Facture", history.iloc[0]['date'] if len(history) > 0 else "Aucune")
    else:
        st.info("Aucune facture enregistrée pour le moment")

def render_nouvelle_facture():
    """Page nouvelle facture manuelle"""
    # Header avec retour
    col_back, col_title, col_date, col_user = st.columns([1, 3, 2, 1])
    with col_back:
        if st.button("←", key="back_btn"):
            st.session_state['current_page'] = "factures"
            st.rerun()
    with col_title:
        st.markdown("### Nouvelle Facture Manuelle")
        st.caption("Cogiteo Market • Gestion des achats")
    with col_date:
        st.markdown(f"<div style='text-align: right; padding-top: 10px;'><span style='font-size: 1.2rem;'>📅</span> Aujourd'hui, {date.today().strftime('%d %b')}</div>", unsafe_allow_html=True)
    with col_user:
        st.markdown(f"<div style='text-align: right; padding-top: 10px;'><div style='background: var(--primary-green); color: white; width: 40px; height: 40px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-weight: bold;'>{st.session_state['username'][0].upper() if st.session_state['username'] else 'U'}</div></div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Section Informations Générales
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown('<div class="info-card-title"><span style="font-size: 1.3rem;">🏪</span> Informations Générales</div>', unsafe_allow_html=True)
    
    market_name = st.text_input(
        "Nom du Marché / Grossiste",
        placeholder="ex: Marché Central",
        key="market_name_input"
    )
    
    col_date1, col_date2 = st.columns(2)
    with col_date1:
        invoice_date = st.date_input(
            "Date de création de la facture",
            value=st.session_state['invoice_date'],
            key="invoice_date_input"
        )
        st.session_state['invoice_date'] = invoice_date
    with col_date2:
        delivery_date = st.date_input(
            "Date de livraison prévue",
            value=st.session_state['delivery_date'],
            key="delivery_date_input"
        )
        st.session_state['delivery_date'] = delivery_date
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Section Articles Achetés
    st.markdown("### 🛒 Articles Achetés")
    
    # Compteur d'articles sera mis à jour après l'édition
    article_count = 0
    
    # Configuration du Data Editor
    default_data = pd.DataFrame([{"Produit": "", "Unité": "kg", "Quantité": 0.0, "Prix Unitaire": 0, "Total Article": 0.0}])
    
    column_cfg = {
        "Unité": st.column_config.SelectboxColumn("Unité", options=["kg", "pièce", "sac", "carton", "litre", "g", "botte"], required=True),
        "Quantité": st.column_config.NumberColumn("Qté", min_value=0, format="%.2f"),
        "Prix Unitaire": st.column_config.NumberColumn("P.U. (FCFA)", min_value=0, format="%d"),
        "Total Article": st.column_config.NumberColumn("TOTAL (FCFA)", disabled=True, format="%d")
    }
    
    edited_df = st.data_editor(
        default_data,
        num_rows="dynamic",
        column_config=column_cfg,
        use_container_width=True,
        key="editor"
    )
    
    # Stocker le dataframe dans session_state
    st.session_state['editor_df'] = edited_df
    
    # Calculer le total en temps réel
    clean_df = edited_df[edited_df["Produit"].str.len() > 0].copy()
    if not clean_df.empty:
        clean_df["Total Article"] = clean_df["Quantité"] * clean_df["Prix Unitaire"]
        total_global = clean_df["Total Article"].sum()
        st.session_state['calculated_df'] = clean_df
        st.session_state['total_global'] = total_global
    else:
        st.session_state['calculated_df'] = None
        st.session_state['total_global'] = 0
        total_global = 0
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Footer avec total et bouton
    st.markdown("---")
    col_foot1, col_foot2 = st.columns([2, 1])
    with col_foot1:
        st.markdown(f"""
        <div style="padding: 15px 0;">
            <div style="margin-bottom: 10px;"><strong>TOTAL HORS TAXE</strong></div>
            <div style="font-size: 1.5rem; font-weight: 700; color: var(--text-dark);">{total_global:,.0f} FCFA</div>
            <div style="margin-top: 10px;"><strong>ARTICLES</strong></div>
            <div style="font-size: 1.2rem; font-weight: 700; color: var(--text-dark);">{article_count}</div>
        </div>
        """, unsafe_allow_html=True)
    with col_foot2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("✅ VALIDER ET ENVOYER AU DRIVE →", use_container_width=True, type="primary"):
            if not market_name:
                st.error("❌ Veuillez renseigner le nom du marché/grossiste")
            elif st.session_state['calculated_df'] is None or st.session_state['calculated_df'].empty:
                st.error("❌ Veuillez ajouter au moins un article")
            else:
                with st.spinner("Génération et envoi en cours..."):
                    invoice_date = st.session_state.get('invoice_date', date.today())
                    fname = create_pdf(
                        market_name,
                        st.session_state['calculated_df'],
                        st.session_state['total_global'],
                        st.session_state['username'],
                        invoice_date
                    )
                    
                    st.session_state['current_pdf'] = fname
                    add_to_history(st.session_state['username'], market_name, st.session_state['total_global'], fname)
                    
                    if upload_file(fname, fname):
                        st.success("✅ Facture générée et envoyée sur Google Drive avec succès !")
                        st.balloons()
                        # Réinitialiser le formulaire
                        st.session_state['editor_key'] += 1
                        st.session_state['calculated_df'] = None
                        st.session_state['total_global'] = 0
                        st.rerun()
                    else:
                        st.warning("⚠️ Facture générée mais erreur lors de l'envoi sur Drive")

def render_historique():
    """Page historique des factures"""
    st.title("📄 Historique des Factures")
    st.markdown("Consultez et gérez l'historique de vos factures et paiements.")
    
    # Barre de recherche et filtres
    col_search1, col_search2, col_search3 = st.columns([3, 1, 1])
    with col_search1:
        search_query = st.text_input("", placeholder="Rechercher par numéro de facture ou fournisseur...", label_visibility="collapsed", key="history_search")
    with col_search2:
        st.button("📅 Filtrer par date", use_container_width=True)
    with col_search3:
        st.button("📥 Exporter", use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Tableau des factures
    history = get_user_history(st.session_state['username'])
    
    if not history.empty:
        # Filtrer par recherche si nécessaire
        if search_query:
            history = history[history['market_name'].str.contains(search_query, case=False, na=False)]
        
        # Formater pour l'affichage
        display_df = history.copy()
        display_df['Date'] = pd.to_datetime(display_df['date']).dt.strftime('%d %b %Y')
        display_df = display_df.rename(columns={
            'market_name': 'NOM DU MARCHÉ / GROSSISTE',
            'Date': 'DATE DE CRÉATION',
            'total_amount': 'TOTAL FACTURE'
        })
        
        # Ajouter colonnes Status et Actions (simulées)
        display_df['STATUT'] = 'Validée'
        display_df['ACTIONS'] = '👁️'
        
        # Afficher le tableau
        st.dataframe(
            display_df[['NOM DU MARCHÉ / GROSSISTE', 'DATE DE CRÉATION', 'TOTAL FACTURE', 'STATUT', 'ACTIONS']],
            use_container_width=True,
            hide_index=True
        )
        
        # Pagination (simulée)
        st.markdown(f"<div style='text-align: center; margin-top: 20px; color: var(--text-gray);'>Affichage de 1 à {len(display_df)} sur {len(history)} résultats</div>", unsafe_allow_html=True)
    else:
        st.info("Aucune facture enregistrée")

def render_numeriser():
    """Page numériser un justificatif"""
    st.title("📷 Numériser un justificatif")
    
    col_new, col_recent = st.columns([2, 1])
    
    with col_new:
        st.markdown("### Nouvelle capture")
        st.markdown("Utilisez votre webcam pour scanner un ticket ou importez une image depuis votre ordinateur.")
        
        # Zone webcam stylisée
        st.markdown("""
        <div class="webcam-container">
            <div class="live-indicator">● EN DIRECT</div>
            <div class="webcam-frame">
                <div style="font-size: 4rem; color: white; margin-bottom: 20px;">📷</div>
                <div style="color: white; font-size: 1.2rem; font-weight: 600;">Cadrez le ticket ou le bon</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Contrôles
        col_gal, col_cap, col_crop = st.columns([1, 2, 1])
        with col_gal:
            st.button("🖼️ Galerie", use_container_width=True)
        with col_cap:
            pic = st.file_uploader("📷", type=['jpg', 'jpeg', 'png'], label_visibility="collapsed", key="scan_upload")
            if pic:
                img = Image.open(pic)
                st.image(img, width=300)
        with col_crop:
            st.button("✂️ Recadrer", use_container_width=True)
        
        if pic:
            if st.button("📄 Convertir et Envoyer sur Drive", use_container_width=True, type="primary"):
                with st.spinner("Conversion et envoi en cours..."):
                    try:
                        t_stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        p_name = f"SCAN_{t_stamp}.pdf"
                        img.convert('RGB').save("temp_scan.pdf")
                        if upload_file("temp_scan.pdf", p_name):
                            st.success("✅ Document converti et envoyé sur Google Drive avec succès !")
                            st.balloons()
                        else:
                            st.error("❌ Erreur lors de l'envoi sur Google Drive.")
                        if os.path.exists("temp_scan.pdf"):
                            os.remove("temp_scan.pdf")
                    except Exception as e:
                        st.error(f"Erreur: {e}")
    
    with col_recent:
        st.markdown("### Captures récentes")
        st.markdown('<div style="text-align: right;"><a href="#" style="color: var(--primary-blue); text-decoration: none;">Tout voir →</a></div>', unsafe_allow_html=True)
        
        # Thumbnails (simulés pour le moment)
        st.info("Aucune capture récente")

def render_fournisseurs():
    """Page fournisseurs"""
    st.title("🏪 Fournisseurs")
    st.info("Page Fournisseurs - À implémenter")

def render_parametres():
    """Page paramètres"""
    st.title("⚙️ Paramètres")
    st.info("Page Paramètres - À implémenter")

# --- APPLICATION PRINCIPALE ---
if not st.session_state['logged_in']:
    render_login_page()
else:
    # Sidebar
    with st.sidebar:
        render_sidebar()
    
    # Bouton Nouvelle Commande en haut
    if st.session_state['current_page'] in ["tableau_de_bord", "factures"]:
        col_nav1, col_nav2 = st.columns([4, 1])
        with col_nav2:
            if st.button("➕ Nouvelle Commande", use_container_width=True, type="primary"):
                st.session_state['current_page'] = "nouvelle_facture"
                st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
    
    # Contenu principal selon la page
    current_page = st.session_state['current_page']
    
    if current_page == "tableau_de_bord":
        render_tableau_de_bord()
    elif current_page == "factures":
        st.title("📄 Factures")
        # Liste des factures avec possibilité de créer une nouvelle
        if st.button("➕ Nouvelle Facture Manuelle", use_container_width=True, type="primary"):
            st.session_state['current_page'] = "nouvelle_facture"
            st.rerun()
        render_historique()
    elif current_page == "nouvelle_facture":
        render_nouvelle_facture()
    elif current_page == "fournisseurs":
        render_fournisseurs()
    elif current_page == "parametres":
        render_parametres()
    else:
        render_tableau_de_bord()
