# 🔐 Exemple de Configuration des Secrets Streamlit Cloud

## 📋 Configuration minimale requise

Dans les **Secrets** de Streamlit Cloud, ajoutez ces 4 valeurs :

```toml
[GOOGLE_DRIVE]
CLIENT_ID = "123456789-abc123def456.apps.googleusercontent.com"
CLIENT_SECRET = "GOCSPX-ExempleSecret123ABC"
STREAMLIT_APP_URL = "https://votre-app.streamlit.app"
FOLDER_ID = "1pxs0MOmITeDtgFw9uA05NZdJJm381y41"
```

## ✅ Explication des champs

### CLIENT_ID (OBLIGATOIRE)
C'est l'ID client OAuth de Google. 
- Dans votre `client_secret.json` : c'est la valeur de `web.client_id`
- **Exemple de format** : `123456789-abc123def456.apps.googleusercontent.com`
- **Où le trouver** : Dans votre fichier `client_secret.json` → `web.client_id`

### CLIENT_SECRET (OBLIGATOIRE)
C'est le secret client OAuth de Google.
- Dans votre `client_secret.json` : c'est la valeur de `web.client_secret`
- **Exemple de format** : `GOCSPX-ExempleSecret123ABC`
- **Où le trouver** : Dans votre fichier `client_secret.json` → `web.client_secret`

### FOLDER_ID (OPTIONNEL)
C'est l'ID du dossier Google Drive où seront stockées les factures.
- Si vous ne le spécifiez pas, la valeur par défaut `1pxs0MOmITeDtgFw9uA05NZdJJm381y41` sera utilisée
- Pour trouver l'ID d'un dossier Google Drive : ouvrez le dossier dans votre navigateur et regardez l'URL
  - Exemple : `https://drive.google.com/drive/folders/1pxs0MOmITeDtgFw9uA05NZdJJm381y41`
  - L'ID est la partie après `/folders/`

### STREAMLIT_APP_URL (OBLIGATOIRE pour Streamlit Cloud)
C'est l'URL complète de votre application Streamlit.
- **Après déploiement**, vous obtiendrez une URL comme : `https://cogiteo-app-facture.streamlit.app`
- Remplacez `votre-app` par le nom réel de votre application
- ⚠️ **Important** : Pas de `/` à la fin de l'URL
- Cette URL sera utilisée comme URI de redirection OAuth (100% en ligne, pas de localhost)

## 📝 Configuration complète minimale

Voici exactement ce que vous devez copier-coller dans les Secrets Streamlit (remplacez par vos vraies valeurs) :

```toml
[GOOGLE_DRIVE]
CLIENT_ID = "votre-client-id.apps.googleusercontent.com"
CLIENT_SECRET = "votre-client-secret"
STREAMLIT_APP_URL = "https://votre-app.streamlit.app"
FOLDER_ID = "1pxs0MOmITeDtgFw9uA05NZdJJm381y41"
```

**Note :** Remplacez `https://votre-app.streamlit.app` par l'URL réelle de votre application Streamlit après le premier déploiement.

## ⚠️ Important : Configuration Google Cloud Console

**AVANT** de déployer, assurez-vous d'avoir configuré dans [Google Cloud Console](https://console.cloud.google.com/apis/credentials) :

1. Allez dans votre projet OAuth 2.0
2. Cliquez sur votre client OAuth
3. Dans **"URIs de redirection autorisés"**, ajoutez :
   - `urn:ietf:wg:oauth:2.0:oob` (pour la méthode console)
   - L'URL de votre application Streamlit (après déploiement) : `https://votre-app.streamlit.app`

## 🔍 Comment obtenir les valeurs depuis client_secret.json

Si vous avez votre fichier `client_secret.json` :

```json
{
  "web": {
    "client_id": "797952505390-...",
    "client_secret": "GOCSPX-..."
  }
}
```

- `CLIENT_ID` = `web.client_id`
- `CLIENT_SECRET` = `web.client_secret`

