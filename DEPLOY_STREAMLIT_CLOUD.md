# 🚀 Déploiement sur Streamlit Community Cloud

Ce guide vous explique comment déployer votre application sur Streamlit Community Cloud.

## 📋 Prérequis

1. Un compte GitHub avec votre dépôt `Cogiteo-App-Facture`
2. Un compte Streamlit (gratuit) : https://share.streamlit.io/
3. Un projet Google Cloud avec OAuth 2.0 configuré

## 🔧 Étapes de déploiement

### 1. Préparer votre dépôt GitHub

Assurez-vous que votre code est bien poussé sur GitHub :
```bash
git add .
git commit -m "Prepare for Streamlit Cloud deployment"
git push origin main
```

### 2. Créer un compte Streamlit Cloud

1. Allez sur https://share.streamlit.io/
2. Cliquez sur **"Sign up"** ou **"Sign in"**
3. Connectez-vous avec votre compte GitHub

### 3. Déployer votre application

1. Sur la page principale de Streamlit Cloud, cliquez sur **"New app"**
2. Configurez votre application :
   - **Repository** : Sélectionnez `Andj04/Cogiteo-App-Facture`
   - **Branch** : `main`
   - **Main file path** : `main.py`
   - **App URL** : Laissez par défaut ou choisissez un nom personnalisé
3. Cliquez sur **"Deploy"**

### 4. Configurer les secrets (IMPORTANT)

Après le déploiement, vous devez configurer les secrets pour Google Drive :

1. Dans la page de votre application, cliquez sur **"⚙️ Settings"** (en haut à droite)
2. Cliquez sur **"Secrets"** dans le menu de gauche
3. Ajoutez les secrets suivants au format TOML :

```toml
[GOOGLE_DRIVE]
CLIENT_ID = "votre-client-id.apps.googleusercontent.com"
CLIENT_SECRET = "votre-client-secret"
STREAMLIT_APP_URL = "https://votre-app.streamlit.app"
FOLDER_ID = "1pxs0MOmITeDtgFw9uA05NZdJJm381y41"
```

**Où trouver ces informations :**
- Ouvrez votre fichier `client_secret.json` local
- `CLIENT_ID` = La valeur de `web.client_id` (par exemple : `123456789-abc.apps.googleusercontent.com`)
- `CLIENT_SECRET` = La valeur de `web.client_secret`
- `STREAMLIT_APP_URL` = L'URL complète de votre application Streamlit (par exemple : `https://cogiteo-app-facture.streamlit.app`)
- `FOLDER_ID` = L'ID du dossier Google Drive où vous voulez stocker les factures (optionnel, valeur par défaut fournie)

**Important :** `STREAMLIT_APP_URL` doit être l'URL exacte de votre application Streamlit. Vous la trouverez après le déploiement initial de l'application.

4. Cliquez sur **"Save"**

### 5. Configurer Google Cloud Console pour Streamlit Cloud

**IMPORTANT :** Vous devez configurer le type d'application OAuth en "Application Web" (pas "Application de bureau") et ajouter l'URL de votre application Streamlit :

1. Allez sur [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Sélectionnez votre projet OAuth 2.0
3. **Si vous avez un client de type "Application de bureau" :**
   - Créez un **nouveau client OAuth 2.0** de type **"Application Web"**
   - OU modifiez votre client existant pour qu'il soit de type "Application Web"
4. Cliquez sur votre client OAuth (type "Application Web") pour l'éditer
5. Dans **"URIs de redirection autorisés"**, ajoutez :
   - **L'URL exacte de votre application Streamlit** (par exemple : `https://votre-app.streamlit.app`)
   - ⚠️ Pas de `/` à la fin de l'URL
6. Cliquez sur **"ENREGISTRER"**
7. **Téléchargez le nouveau `client_secret.json`** et mettez à jour vos secrets dans Streamlit Cloud avec les nouvelles valeurs (`web.client_id` et `web.client_secret`)

### 6. Redéployer l'application

Après avoir configuré les secrets :
1. Dans Streamlit Cloud, cliquez sur **"☰"** (menu) > **"Redeploy"**
2. Ou faites un nouveau commit et push sur GitHub (redéploiement automatique)

## ⚠️ Notes importantes

### Authentification OAuth sur Streamlit Cloud

Sur Streamlit Cloud, l'authentification OAuth fonctionne en **mode 100% en ligne** :
- **Redirection automatique** : Après autorisation Google, vous serez automatiquement redirigé vers l'application
- **Pas besoin de copier-coller** : Le code OAuth est géré automatiquement via l'URL
- **Session temporaire** : Les tokens sont stockés en session (perdus à chaque redémarrage de l'application)
- **Application Web OAuth** : Utilise le flow OAuth "Web" au lieu de "Installed App"

### Base de données

- La base de données SQLite (`app_database.db`) est créée dans l'environnement Cloud
- Les données sont **temporaires** et peuvent être perdues lors d'un redéploiement
- Pour une solution permanente, envisagez d'utiliser une base de données externe (PostgreSQL, MySQL, etc.)

### Stockage des fichiers

- Les fichiers PDF générés sont temporaires
- L'upload sur Google Drive fonctionne normalement
- Les fichiers locaux sont supprimés après la session

## 🔍 Vérification du déploiement

1. Ouvrez votre application sur Streamlit Cloud
2. Testez la création d'un compte
3. Testez la création d'une facture
4. Testez l'upload sur Google Drive

## 🐛 Dépannage

### Erreur : "Configuration OAuth introuvable"
- Vérifiez que les secrets sont correctement configurés dans Streamlit Cloud
- Vérifiez que les noms des secrets correspondent exactement (sensible à la casse)

### Erreur : "redirect_uri_mismatch"
- Vérifiez que l'URL de votre application Streamlit est bien ajoutée dans Google Cloud Console
- L'URL doit être exactement : `https://votre-app.streamlit.app` (sans `/` à la fin)

### Erreur : "Token expiré"
- Sur Streamlit Cloud, les tokens sont stockés en session
- Si la session expire, vous devrez vous ré-authentifier
- C'est normal et attendu

## 📚 Ressources

- [Documentation Streamlit Cloud](https://docs.streamlit.io/streamlit-community-cloud)
- [Gestion des secrets Streamlit](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)
- [Configuration OAuth Google](CONFIGURATION_OAUTH.md)

