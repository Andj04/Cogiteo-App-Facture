# 📥 Comment télécharger client_secret.json depuis Google Cloud Console

## 🔍 Étapes détaillées

### 1. Accéder à Google Cloud Console

1. Allez sur : https://console.cloud.google.com/
2. Connectez-vous avec votre compte Google

### 2. Sélectionner votre projet

1. En haut de la page, dans la barre de navigation, vous verrez le nom du projet actuel
2. Cliquez sur le **sélecteur de projet** (à côté du nom)
3. Sélectionnez le projet qui contient vos identifiants OAuth
   - Si vous ne voyez pas votre projet, utilisez la barre de recherche pour le trouver

### 3. Accéder aux identifiants OAuth

1. Dans le menu latéral gauche, cliquez sur **"API et services"** (ou cherchez-le dans le menu)
2. Puis cliquez sur **"Identifiants"** (Credentials)

   **OU** accédez directement à :
   https://console.cloud.google.com/apis/credentials

### 4. Trouver votre client OAuth 2.0

1. Dans la liste des identifiants, cherchez votre **"ID client OAuth 2.0"**
2. Il devrait avoir un nom comme :
   - "Client OAuth 2.0"
   - Ou le nom que vous avez donné lors de la création

### 5. Ouvrir le client OAuth

1. **Cliquez sur le nom** de votre client OAuth 2.0 pour l'ouvrir

### 6. Télécharger le fichier JSON

1. Dans la page de détails du client OAuth, vous verrez plusieurs onglets en haut
2. En haut à droite, vous verrez une icône de **téléchargement** (⬇️) ou un bouton **"Télécharger JSON"**
3. Cliquez sur **"Télécharger JSON"** ou **"Download"**

   **Alternative** :
   - En bas de la page, dans la section **"Secrets client"**, vous pouvez aussi voir un bouton **"Télécharger"**

### 7. Enregistrer le fichier

1. Une fenêtre de téléchargement s'ouvrira
2. Le fichier sera nommé quelque chose comme : `client_secret_XXXXXXXXXX-XXXXX.apps.googleusercontent.com.json`
3. **Renommez-le en** : `client_secret.json`
4. Placez-le dans le dossier de votre projet local

## ⚠️ Important : Vérifier le type de client

**Pour Streamlit Cloud (application web en ligne)**, votre client OAuth doit être de type **"Application Web"** (Web application) :

1. Dans la page de détails du client, vérifiez la section **"Type d'application"**
2. Si c'est **"Application de bureau"** (Desktop app) :
   - Vous devez créer un **nouveau client** de type **"Application Web"**
   - OU modifier le type si possible

### Structure du fichier client_secret.json

**Pour une Application Web** (nécessaire pour Streamlit Cloud) :
```json
{
  "web": {
    "client_id": "votre-client-id.apps.googleusercontent.com",
    "project_id": "votre-project-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "GOCSPX-votre-secret",
    "redirect_uris": []
  }
}
```

**Pour une Application de bureau** (utilisation locale uniquement) :
```json
{
  "installed": {
    "client_id": "votre-client-id.apps.googleusercontent.com",
    "project_id": "votre-project-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "GOCSPX-votre-secret",
    "redirect_uris": []
  }
}
```

## 📝 Raccourci direct

Vous pouvez aussi accéder directement à cette URL (remplacez `PROJECT_ID` par votre ID de projet) :
```
https://console.cloud.google.com/apis/credentials?project=PROJECT_ID
```

## 🔄 Re-télécharger après modification

Si vous avez modifié votre client OAuth (ajout d'URI de redirection, changement de type, etc.) :

1. Suivez les mêmes étapes ci-dessus
2. Le nouveau fichier téléchargé contiendra les modifications
3. Remplacez l'ancien `client_secret.json` par le nouveau

## 💡 Astuce

Après avoir téléchargé le fichier pour la première fois :
- Sauvegardez-le dans un endroit sûr
- Ne le commitez **JAMAIS** sur Git (il est dans `.gitignore`)
- Utilisez-le uniquement pour l'utilisation locale
- Pour Streamlit Cloud, utilisez les secrets dans l'interface Streamlit

## 🆘 Problème : Je ne vois pas le bouton de téléchargement

Si vous ne voyez pas le bouton de téléchargement :
1. Assurez-vous d'avoir ouvert le client OAuth (cliqué dessus)
2. Vérifiez que vous êtes bien sur la page de détails (pas sur la liste)
3. Le bouton peut être dans différentes positions selon la version de Google Cloud Console
4. Essayez de chercher "Download" ou "Télécharger" dans la page

## 🔐 Sécurité

⚠️ **Important** :
- Ne partagez **JAMAIS** votre `client_secret.json`
- Ne le commitez **JAMAIS** sur Git
- Si vous pensez qu'il a été compromis, régénérez un nouveau secret dans Google Cloud Console

