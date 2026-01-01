import os.path
import socket
import json
from urllib.parse import urlparse, parse_qs
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow, Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import streamlit as st

# Si tu modifies ces scopes, supprime le fichier token.json
SCOPES = ['https://www.googleapis.com/auth/drive.file']
CLIENT_SECRET_FILE = 'client_secret.json'
TOKEN_FILE = 'token.json'

# Récupérer FOLDER_ID depuis les secrets Streamlit ou utiliser la valeur par défaut
try:
    FOLDER_ID = st.secrets.get("GOOGLE_DRIVE", {}).get("FOLDER_ID", "1pxs0MOmITeDtgFw9uA05NZdJJm381y41")
except:
    FOLDER_ID = "1pxs0MOmITeDtgFw9uA05NZdJJm381y41"

def get_drive_service():
    creds = None
    # Chargement du token existant
    # D'abord vérifier dans session_state (pour Streamlit Cloud)
    if 'google_credentials' in st.session_state:
        try:
            creds = Credentials.from_authorized_user_info(json.loads(st.session_state['google_credentials']), SCOPES)
        except Exception as e:
            st.warning(f"Erreur lors du chargement du token de session : {e}")
            del st.session_state['google_credentials']
            creds = None
    
    # Sinon, essayer depuis le fichier (pour utilisation locale)
    if not creds and os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        except Exception as e:
            st.warning(f"Erreur lors du chargement du token : {e}")
            # Supprimer le token invalide
            if os.path.exists(TOKEN_FILE):
                os.remove(TOKEN_FILE)
            creds = None
    
    # Si pas de credentials valides, on lance le flow OAuth
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                st.warning(f"Erreur lors du rafraîchissement du token : {e}")
                creds = None
        
        if not creds:
            # Vérifier si on est sur Streamlit Cloud (secrets disponibles)
            is_streamlit_cloud = False
            client_config = None
            streamlit_url = None
            
            try:
                if hasattr(st, 'secrets') and 'GOOGLE_DRIVE' in st.secrets:
                    # Utiliser les secrets de Streamlit Cloud
                    is_streamlit_cloud = True
                    secrets = st.secrets['GOOGLE_DRIVE']
                    
                    # Obtenir l'URL de l'application Streamlit
                    try:
                        # Obtenir l'URL de l'application depuis les secrets
                    streamlit_url = secrets.get("STREAMLIT_APP_URL", "")
                    if not streamlit_url:
                        st.error("❌ STREAMLIT_APP_URL manquant dans les secrets !")
                        st.info("💡 Ajoutez STREAMLIT_APP_URL dans les secrets avec l'URL complète de votre application Streamlit (ex: https://votre-app.streamlit.app)")
                        return None
                    except:
                        pass
                    
                    # Utiliser le flow "web" pour Streamlit Cloud (pas "installed")
                    client_config = {
                        "web": {
                            "client_id": secrets.get("CLIENT_ID"),
                            "client_secret": secrets.get("CLIENT_SECRET"),
                            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                            "token_uri": "https://oauth2.googleapis.com/token",
                            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                            "redirect_uris": [streamlit_url] if streamlit_url else []
                        }
                    }
                    if not client_config["web"]["client_id"] or not client_config["web"]["client_secret"]:
                        client_config = None
            except Exception as e:
                st.warning(f"Impossible de charger les secrets Streamlit : {e}")
                client_config = None
            
            # Si pas de secrets, essayer le fichier local
            if not client_config:
                if not os.path.exists(CLIENT_SECRET_FILE):
                    st.error("❌ Configuration OAuth introuvable !")
                    st.info("""
                    💡 **Pour utilisation locale :**
                    Assurez-vous que le fichier `client_secret.json` est dans le même dossier que l'application.
                    
                    💡 **Pour Streamlit Cloud :**
                    Configurez les secrets dans les paramètres de l'application :
                    - CLIENT_ID
                    - CLIENT_SECRET
                    - STREAMLIT_APP_URL (URL complète de votre app, ex: https://votre-app.streamlit.app)
                    - FOLDER_ID (optionnel)
                    """)
                    return None
                # Charger depuis le fichier
                with open(CLIENT_SECRET_FILE, 'r') as f:
                    client_config = json.load(f)
            
            try:
                # Sur Streamlit Cloud, utiliser Flow (web) au lieu de InstalledAppFlow
                if is_streamlit_cloud:
                    # Vérifier si on est dans le callback OAuth
                    try:
                        # Streamlit 1.27+
                        query_params = st.query_params
                    except:
                        try:
                            # Anciennes versions de Streamlit
                            query_params = st.experimental_get_query_params()
                        except:
                            query_params = {}
                    
                    if 'code' in query_params:
                        # On est de retour de l'autorisation Google
                        flow = Flow.from_client_config(client_config, SCOPES)
                        flow.redirect_uri = streamlit_url
                        
                        # Récupérer le code d'autorisation
                        # Gérer les deux formats (dict ou liste)
                        auth_code = query_params['code']
                        if isinstance(auth_code, list):
                            auth_code = auth_code[0]
                        
                        # Échanger le code contre les credentials
                        flow.fetch_token(code=auth_code)
                        creds = flow.credentials
                        
                        # Sauvegarder dans session_state
                        st.session_state['google_credentials'] = creds.to_json()
                        
                        st.success("✅ Authentification réussie !")
                        st.rerun()
                        return build('drive', 'v3', credentials=creds)
                    
                    # Sinon, initier le flow d'autorisation
                    flow = Flow.from_client_config(client_config, SCOPES)
                    flow.redirect_uri = streamlit_url
                    
                    authorization_url, state = flow.authorization_url(
                        access_type='offline',
                        include_granted_scopes='true',
                        prompt='consent'
                    )
                    
                    st.info("🔐 **Authentification Google Drive requise**")
                    st.markdown("---")
                    st.markdown("**Cliquez sur le bouton ci-dessous pour vous connecter à Google Drive :**")
                    st.markdown(f"[🔗 Se connecter à Google Drive]({authorization_url})")
                    st.info("Après autorisation, vous serez automatiquement redirigé vers l'application.")
                    
                    # Stocker le state dans session pour vérification
                    st.session_state['oauth_state'] = state
                    return None
                else:
                    # Utilisation locale avec InstalledAppFlow
                    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
                
                # Essayer d'abord avec un serveur local sur un port libre
                # Tester plusieurs ports jusqu'à en trouver un libre
                ports_to_try = [8080, 8090, 8091, 8092, 8093]
                port_used = None
                
                def is_port_free(port):
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        try:
                            s.bind(('localhost', port))
                            return True
                        except OSError:
                            return False
                
                for port in ports_to_try:
                    if is_port_free(port):
                        port_used = port
                        break
                
                if port_used:
                    # Méthode avec serveur local (plus fluide)
                    try:
                        st.info(f"🔐 **Authentification Google Drive** - Port {port_used}")
                        st.info("Une fenêtre de votre navigateur va s'ouvrir pour l'autorisation...")
                        creds = flow.run_local_server(
                            port=port_used,
                            open_browser=True,
                            authorization_prompt_message='',
                            success_message='✅ Authentification réussie ! Vous pouvez fermer cette fenêtre.',
                            redirect_uri_trailing_slash=False
                        )
                    except OSError as e:
                        st.warning(f"⚠️ Le port {port_used} n'est plus disponible, passage en mode console...")
                        port_used = None
                
                if not port_used:
                    # Méthode console (fallback si serveur local ne fonctionne pas)
                    # On utilise le redirect_uri OOB (Out of Band) pour la méthode console
                    st.info("🔐 **Authentification Google Drive requise**")
                    st.markdown("---")
                    
                    # Créer un nouveau flow et modifier le redirect_uri pour OOB
                    flow_console = InstalledAppFlow.from_client_config(client_config, SCOPES)
                    # Définir le redirect_uri OOB (Out of Band) pour la méthode console
                    flow_console.redirect_uri = 'urn:ietf:wg:oauth:2.0:oob'
                    
                    authorization_url, _ = flow_console.authorization_url(prompt='consent')
                    
                    st.markdown("**📋 Étapes à suivre :**")
                    st.markdown("1. Cliquez sur le lien ci-dessous pour autoriser l'application")
                    st.markdown("2. Connectez-vous avec votre compte Google")
                    st.markdown("3. Autorisez l'application à accéder à Google Drive")
                    st.markdown("4. **Copiez le code d'autorisation** qui apparaît dans l'URL après 'code=' ou affiché sur la page")
                    st.markdown("5. Collez-le dans le champ ci-dessous")
                    
                    st.markdown(f"[🔗 Cliquez ici pour autoriser l'application]({authorization_url})")
                    
                    # Champ pour saisir le code d'autorisation
                    auth_code = st.text_input(
                        "📝 Collez le code d'autorisation ici :",
                        type="default",
                        help="Le code d'autorisation se trouve dans l'URL après 'code=' ou affiché sur la page de confirmation"
                    )
                    
                    if auth_code:
                        try:
                            # Échange du code contre les credentials avec le redirect_uri OOB
                            flow_console.fetch_token(code=auth_code.strip())
                            creds = flow_console.credentials
                        except Exception as e:
                            st.error(f"❌ Code invalide ou expiré : {e}")
                            st.info("💡 Assurez-vous d'avoir copié le code complet depuis l'URL de redirection ou la page de confirmation.")
                            return None
                    else:
                        return None
                
                # Sauvegarde du token (seulement si pas sur Streamlit Cloud)
                # Sur Streamlit Cloud, on utilise la session pour stocker temporairement
                try:
                    # Essayer de sauvegarder dans un fichier (local)
                    if not os.getenv('STREAMLIT_SERVER'):
                        with open(TOKEN_FILE, 'w') as token:
                            token.write(creds.to_json())
                        st.success("✅ Authentification réussie ! Token sauvegardé.")
                    else:
                        # Sur Streamlit Cloud, stocker dans session_state
                        st.session_state['google_credentials'] = creds.to_json()
                        st.success("✅ Authentification réussie !")
                except Exception as e:
                    # Si on ne peut pas sauvegarder, stocker en session
                    st.session_state['google_credentials'] = creds.to_json()
                    st.success("✅ Authentification réussie !")
                
                st.rerun()  # Recharger pour utiliser les nouveaux credentials
                    
            except Exception as e:
                st.error(f"❌ Erreur lors de l'authentification OAuth : {e}")
                st.info("""
                **Solution pour l'erreur "Missing required parameter: redirect_uri" :**
                
                1. Allez dans [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
                2. Sélectionnez votre projet OAuth 2.0
                3. Cliquez sur votre client OAuth pour l'éditer
                4. Dans **"URIs de redirection autorisés"**, ajoutez :
                   - `urn:ietf:wg:oauth:2.0:oob` (pour la méthode console)
                   - `http://localhost:8080/` (pour la méthode serveur local)
                   - `http://localhost:8090/` (port alternatif)
                5. Cliquez sur **"ENREGISTRER"**
                6. Téléchargez à nouveau `client_secret.json` et remplacez-le
                7. Supprimez `token.json` si il existe
                8. Relancez l'application
                
                ⚠️ **Important** : L'URI `urn:ietf:wg:oauth:2.0:oob` est essentiel pour la méthode console !
                """)
                return None

    return build('drive', 'v3', credentials=creds)

def upload_file(filepath, filename):
    service = get_drive_service()
    if not service:
        return False
    
    try:
        file_metadata = {'name': filename, 'parents': [FOLDER_ID]}
        media = MediaFileUpload(filepath, resumable=True)
        service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return True
    except Exception as e:
        st.error(f"Erreur Drive : {e}")
        return False

