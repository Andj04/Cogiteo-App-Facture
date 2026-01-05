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
    
    /* Bouton primaire - par défaut bleu pour login */
    button[kind="primary"]:not(.login-btn-blue) {
        background: var(--primary-green) !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
    }
    
    button[kind="primary"]:not(.login-btn-blue):hover {
        background: #218838 !important;
    }
    
    /* Bouton connexion bleu */
    button[kind="primary"][data-testid*="login_btn"],
    button[kind="primary"][data-testid*="signup_btn"] {
        background: #1f77b4 !important;
        color: white !important;
        border: none !important;
        font-weight: 500 !important;
    }
    
    button[kind="primary"][data-testid*="login_btn"]:hover,
    button[kind="primary"][data-testid*="signup_btn"]:hover {
        background: #1565c0 !important;
    }
    
    /* Style du bouton Google Drive */
    button[data-testid*="google_drive_btn"] {
        background: white !important;
        color: #3c4043 !important;
        border: 1px solid #dadce0 !important;
        font-weight: 500 !important;
        box-shadow: none !important;
    }
    
    button[data-testid*="google_drive_btn"]:hover {
        box-shadow: 0 1px 3px rgba(0,0,0,0.12) !important;
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
        max-width: 420px;
        margin: 0 auto;
        padding: 0;
    }
    
    .login-card {
        background: white;
        border-radius: 8px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1), 0 4px 16px rgba(0, 0, 0, 0.08);
        padding: 40px 35px;
        margin: 20px 0;
    }
    
    .login-header {
        text-align: center;
        margin-bottom: 35px;
    }
    
    .login-title {
        font-size: 1.75rem;
        font-weight: 700;
        color: var(--text-dark);
        margin: 15px 0 8px;
        line-height: 1.3;
    }
    
    .login-subtitle {
        color: var(--text-gray);
        font-size: 0.95rem;
        margin: 0;
    }
    
    .google-drive-btn {
        width: 100%;
        padding: 12px 20px;
        background: white;
        border: 1px solid #dadce0;
        border-radius: 4px;
        font-size: 0.95rem;
        font-weight: 500;
        color: #3c4043;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
        margin-bottom: 15px;
        transition: box-shadow 0.2s;
    }
    
    .google-drive-btn:hover {
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
    }
    
    .google-icon {
        width: 20px;
        height: 20px;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path fill="%234285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="%2334A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="%23FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="%23EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>') no-repeat center;
        background-size: contain;
    }
    
    .google-confirm {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        margin: 15px 0 25px;
        color: #28a745;
        font-size: 0.9rem;
    }
    
    .google-confirm-check {
        color: #28a745;
        font-size: 1.1rem;
        font-weight: bold;
    }
    
    .divider-or {
        display: flex;
        align-items: center;
        text-align: center;
        margin: 25px 0;
        color: #5f6368;
        font-size: 0.875rem;
    }
    
    .divider-or::before,
    .divider-or::after {
        content: '';
        flex: 1;
        border-bottom: 1px solid #dadce0;
    }
    
    .divider-or span {
        padding: 0 15px;
        font-weight: 500;
    }
    
    .input-container {
        position: relative;
        margin-bottom: 20px;
    }
    
    .input-icon {
        position: absolute;
        left: 12px;
        top: 50%;
        transform: translateY(-50%);
        color: #5f6368;
        font-size: 1.1rem;
        z-index: 1;
    }
    
    .input-field {
        padding-left: 40px !important;
    }
    
    .password-container {
        position: relative;
    }
    
    .password-toggle {
        position: absolute;
        right: 12px;
        top: 50%;
        transform: translateY(-50%);
        background: none;
        border: none;
        color: #5f6368;
        cursor: pointer;
        font-size: 1.1rem;
        z-index: 2;
        padding: 5px;
    }
    
    .forgot-password-link {
        text-align: right;
        margin-top: -12px;
        margin-bottom: 8px;
        font-size: 0.875rem;
    }
    
    .forgot-password-link a {
        color: #1f77b4;
        text-decoration: none;
    }
    
    .forgot-password-link a:hover {
        text-decoration: underline;
    }
    
    .login-btn-blue {
        background: #1f77b4 !important;
        color: white !important;
        border: none !important;
        font-weight: 500 !important;
    }
    
    .login-btn-blue:hover {
        background: #1565c0 !important;
    }
    
    .signup-link {
        text-align: center;
        margin-top: 25px;
        color: #5f6368;
        font-size: 0.9rem;
    }
    
    .signup-link a {
        color: #1f77b4;
        text-decoration: none;
        font-weight: 500;
    }
    
    .signup-link a:hover {
        text-decoration: underline;
    }
    
    .footer-login {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 50px;
        padding-top: 20px;
        border-top: 1px solid #e0e0e0;
        color: #5f6368;
        font-size: 0.875rem;
    }
    
    .footer-login-item {
        display: flex;
        align-items: center;
        gap: 6px;
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
    """Page de connexion selon le design exact"""
    # Gradient header
    st.markdown('<div class="gradient-header"></div>', unsafe_allow_html=True)
    
    # Logo
    col_logo, col_empty = st.columns([1, 3])
    with col_logo:
        logo = load_logo()
        if logo:
            st.image(logo, width=140)
    
    st.markdown('<div class="login-page">', unsafe_allow_html=True)
    
    # Header text
    st.markdown("""
    <div class="login-header">
        <h1 class="login-title">Simplifiez vos achats au marché</h1>
        <p class="login-subtitle">Connectez-vous pour gérer vos commandes et factures</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Bouton Google Drive avec logo Google
    st.markdown("""
    <style>
    .google-btn-wrapper {
        width: 100%;
        margin-bottom: 15px;
    }
    .google-btn-wrapper button {
        width: 100%;
        padding: 12px 20px;
        background: white;
        border: 1px solid #dadce0;
        border-radius: 4px;
        font-size: 0.95rem;
        font-weight: 500;
        color: #3c4043;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
        transition: box-shadow 0.2s;
    }
    .google-btn-wrapper button:hover {
        box-shadow: 0 1px 3px rgba(0,0,0,0.12);
    }
    </style>
    <div class="google-btn-wrapper">
    """, unsafe_allow_html=True)
    
    google_clicked = st.button("🔵 Se connecter avec Google Drive", use_container_width=True, key="google_drive_btn")
    st.markdown("</div>", unsafe_allow_html=True)
    
    if google_clicked:
        service = get_drive_service()
        if service:
            st.success("✅ Connexion Google Drive réussie !")
            st.session_state['google_connected'] = True
        else:
            st.info("💡 Vous serez redirigé vers Google pour l'autorisation")
    
    st.markdown("""
    <div class="google-confirm">
        <span class="google-confirm-check">✓</span>
        <span>Vos factures sont stockées directement sur votre Drive personnel</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Séparateur
    st.markdown('<div class="divider-or"><span>OU AVEC EMAIL</span></div>', unsafe_allow_html=True)
    
    # Champ Email avec icône
    st.markdown("""
    <style>
    div[data-testid="stTextInput"]:has(input[placeholder*="exemple@restaurant.com"]) label {
        display: none;
    }
    </style>
    """, unsafe_allow_html=True)
    
    col_email_icon, col_email_input = st.columns([0.1, 0.9])
    with col_email_icon:
        st.markdown('<div style="padding-top: 38px; text-align: center; color: #5f6368; font-size: 1.1rem;">✉</div>', unsafe_allow_html=True)
    with col_email_input:
        username = st.text_input(
            "Email",
            placeholder="exemple@restaurant.com",
            label_visibility="visible",
            key="login_email"
        )
    
    # Champ Mot de passe avec icône et toggle
    if 'show_password' not in st.session_state:
        st.session_state['show_password'] = False
    
    col_pass_icon, col_pass_input, col_pass_toggle = st.columns([0.1, 0.75, 0.15])
    with col_pass_icon:
        st.markdown('<div style="padding-top: 38px; text-align: center; color: #5f6368; font-size: 1.1rem;">🔒</div>', unsafe_allow_html=True)
    with col_pass_input:
        password = st.text_input(
            "Mot de passe",
            type='password' if not st.session_state['show_password'] else 'text',
            placeholder="••••••••",
            label_visibility="visible",
            key="login_password"
        )
    with col_pass_toggle:
        st.markdown('<div style="padding-top: 38px;"></div>', unsafe_allow_html=True)
        if st.button("👁", key="toggle_password", help="Afficher/Masquer le mot de passe"):
            st.session_state['show_password'] = not st.session_state['show_password']
            st.rerun()
    
    # Lien mot de passe oublié
    st.markdown("""
    <div class="forgot-password-link">
        <a href="#">Mot de passe oublié ?</a>
    </div>
    """, unsafe_allow_html=True)
    
    # Bouton connexion (bleu)
    if st.session_state.get('signup_mode', False):
        if st.button("S'inscrire", use_container_width=True, type="primary", key="signup_btn"):
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
        if st.button("Se connecter", use_container_width=True, key="login_btn", type="primary"):
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
    st.markdown("""
    <div class="signup-link">
        Vous n'avez pas de compte ? <a href="#" onclick="document.querySelector('[data-testid=baseButton-secondary]').click(); return false;">S'inscrire</a>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("Toggle Signup", key="signup_toggle", use_container_width=False, type="secondary"):
        st.session_state['signup_mode'] = not st.session_state.get('signup_mode', False)
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)  # Fermeture login-card
    st.markdown('</div>', unsafe_allow_html=True)  # Fermeture login-page
    
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
    
    # Calculer le total en temps réel et compter les articles
    clean_df = edited_df[edited_df["Produit"].str.len() > 0].copy()
    if not clean_df.empty:
        clean_df["Total Article"] = clean_df["Quantité"] * clean_df["Prix Unitaire"]
        total_global = clean_df["Total Article"].sum()
        article_count = len(clean_df)
        st.session_state['calculated_df'] = clean_df
        st.session_state['total_global'] = total_global
    else:
        st.session_state['calculated_df'] = None
        st.session_state['total_global'] = 0
        total_global = 0
        article_count = 0
    
    # Afficher le compteur d'articles
    st.caption(f"{article_count} articles ajoutés")
    
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
    elif current_page == "numeriser":
        render_numeriser()
    elif current_page == "fournisseurs":
        render_fournisseurs()
    elif current_page == "parametres":
        render_parametres()
    else:
        render_tableau_de_bord()
