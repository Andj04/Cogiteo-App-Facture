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
st.set_page_config(page_title="Resto-Marché Pro", page_icon="🛒")

# --- GESTION SESSION ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'username' not in st.session_state:
    st.session_state['username'] = ""
if 'calculated_df' not in st.session_state:
    st.session_state['calculated_df'] = None
if 'total_global' not in st.session_state:
    st.session_state['total_global'] = 0

# --- ECRAN DE LOGIN / SIGNUP ---
if not st.session_state['logged_in']:
    st.title("🔐 Connexion Resto-Marché")
    choice = st.selectbox("Menu", ["Se connecter", "Créer un compte"])
    
    username = st.text_input("Nom d'utilisateur")
    password = st.text_input("Mot de passe", type='password')
    
    if choice == "Se connecter":
        if st.button("Entrer"):
            if check_login(username, password):
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.rerun()
            else:
                st.error("Identifiants incorrects")
    else:
        if st.button("Créer le compte"):
            if create_user(username, password):
                st.success("Compte créé ! Veuillez vous connecter.")
            else:
                st.error("Ce nom d'utilisateur existe déjà.")

# --- APPLICATION PRINCIPALE ---
else:
    # Sidebar
    with st.sidebar:
        st.write(f"👤 Connecté en tant que : **{st.session_state['username']}**")
        if st.button("Déconnexion"):
            st.session_state['logged_in'] = False
            st.rerun()
        st.divider()
        st.write("📂 **Historique récent**")
        history = get_user_history(st.session_state['username'])
        if not history.empty:
            st.dataframe(history[['date', 'market_name', 'total_amount']], hide_index=True)
        else:
            st.write("Aucune facture.")

    st.title("🛒 Gestion des Achats")
    
    tab1, tab2 = st.tabs(["📝 Créer Facture", "📷 Scan Photo"])

    # --- ONGLET 1 : SAISIE ---
    with tab1:
        market_name = st.text_input("📍 Nom du Marché / Fournisseur")
        
        st.write("### Liste des courses")
        st.caption("Ajoutez vos articles un par un. Le total se calcule au clic sur 'Valider'.")

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
        if st.button("🔄 Valider et Calculer Total"):
            # Nettoyage et Calculs
            clean_df = edited_df[edited_df["Produit"].str.len() > 0].copy()
            clean_df["Total Article"] = clean_df["Quantité"] * clean_df["Prix Unitaire"]
            
            # Mise en mémoire
            st.session_state['calculated_df'] = clean_df
            st.session_state['total_global'] = clean_df["Total Article"].sum()
            
            st.success("Calculs effectués ! Vérifiez ci-dessous.")

        # AFFICHAGE DU RÉSULTAT ET GÉNÉRATION
        if st.session_state['calculated_df'] is not None and not st.session_state['calculated_df'].empty:
            st.divider()
            st.markdown(f"### 💰 Total Global : :green[{st.session_state['total_global']:,.0f} FCFA]")
            
            # Affichage du tableau calculé (lecture seule)
            st.dataframe(st.session_state['calculated_df'], use_container_width=True)
            
            # Bouton GÉNÉRATION PDF
            col_gen1, col_gen2 = st.columns(2)
            with col_gen1:
                if st.button("📄 Générer la Facture PDF"):
                    if not market_name:
                        st.error("Il manque le nom du marché !")
                    else:
                        fname = create_pdf(market_name, st.session_state['calculated_df'], st.session_state['total_global'], st.session_state['username'])
                        
                        # On stocke le nom du fichier généré dans la session pour afficher les boutons d'action
                        st.session_state['current_pdf'] = fname
                        
                        # Ajout à l'historique DB
                        add_to_history(st.session_state['username'], market_name, st.session_state['total_global'], fname)

            # ACTIONS SUR LE PDF GÉNÉRÉ
            if 'current_pdf' in st.session_state and os.path.exists(st.session_state['current_pdf']):
                st.write("---")
                st.success("Facture prête !")
                
                c1, c2 = st.columns(2)
                with c1:
                    with open(st.session_state['current_pdf'], "rb") as pdf_file:
                        st.download_button(label="📥 Télécharger PDF", data=pdf_file, file_name=st.session_state['current_pdf'], mime="application/pdf")
                with c2:
                    if st.button("☁️ Envoyer sur Google Drive"):
                        with st.spinner("Envoi en cours..."):
                            if upload_file(st.session_state['current_pdf'], st.session_state['current_pdf']):
                                st.success("Envoyé sur Drive !")
                            else:
                                st.error("Erreur d'envoi.")

    # --- ONGLET 2 : PHOTO ---
    with tab2:
        st.header("Scan rapide")
        pic = st.file_uploader("Prendre une photo", type=['jpg', 'png'])
        if pic:
            img = Image.open(pic)
            st.image(img, width=300)
            if st.button("Convertir et Drive"):
                # Logique simplifiée pour l'image
                t_stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                p_name = f"SCAN_{t_stamp}.pdf"
                img.convert('RGB').save("temp_scan.pdf")
                if upload_file("temp_scan.pdf", p_name):
                    st.success("Scan envoyé !")
                    os.remove("temp_scan.pdf")

