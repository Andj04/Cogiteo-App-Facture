# 🔧 Configuration OAuth Google Drive

## Problèmes courants

### Erreur 400 : redirect_uri_mismatch
L'URI de redirection utilisé par l'application ne correspond pas à ceux configurés dans la Google Cloud Console.

### Erreur 400 : invalid_request - Missing required parameter: redirect_uri
Le redirect_uri n'est pas configuré correctement pour la méthode console (OOB flow).

### Erreur WinError 10048 : Port déjà utilisé
Le port est déjà utilisé par une autre application (comme Streamlit sur le port 8501).

## ✅ Solution : Configurer les URI de redirection

L'application utilise maintenant une méthode intelligente qui :
1. **Essaie d'abord** d'utiliser un serveur local sur un port libre (8080, 8090, etc.)
2. **Sinon**, passe en mode console (copier-coller du code)

### Étapes à suivre :

1. **Allez sur Google Cloud Console**
   - Ouvrez : https://console.cloud.google.com/apis/credentials
   - Connectez-vous avec votre compte Google

2. **Sélectionnez votre projet**
   - Dans le menu déroulant en haut, choisissez le projet qui contient vos identifiants OAuth

3. **Ouvrez les identifiants OAuth 2.0**
   - Dans la liste des identifiants, trouvez votre client OAuth 2.0
   - Cliquez dessus pour l'éditer

4. **Ajoutez les URI de redirection**
   - Trouvez la section **"URIs de redirection autorisés"**
   - Cliquez sur **"+ AJOUTER UN URI"**
   - Ajoutez ces URI (un par un) pour la méthode serveur local :
     ```
     http://localhost:8080/
     http://127.0.0.1:8080/
     http://localhost:8090/
     http://127.0.0.1:8090/
     ```
   - **IMPORTANT** : Ajoutez aussi cet URI pour la méthode console (fallback) - **OBLIGATOIRE** :
     ```
     urn:ietf:wg:oauth:2.0:oob
     ```
     ⚠️ Cet URI est **essentiel** pour éviter l'erreur "Missing required parameter: redirect_uri" !
   - Cliquez sur **"ENREGISTRER"**

5. **Vérifiez le type d'application**
   - Assurez-vous que le type d'application est défini sur **"Application de bureau"** ou **"Autre"**
   - Si ce n'est pas le cas, créez un nouveau client OAuth 2.0 avec le type "Application de bureau"

6. **Téléchargez à nouveau le fichier client_secret.json**
   - Après avoir modifié les URI, téléchargez à nouveau le fichier `client_secret.json`
   - Remplacez l'ancien fichier dans le dossier de l'application

7. **Supprimez le token.json existant** (si vous en avez un)
   - Cela forcera une nouvelle authentification avec les bons URI
   - Supprimez le fichier `token.json` dans le dossier de l'application

8. **Relancez l'application**
   - Redémarrez Streamlit : `streamlit run main.py`
   - Réessayez l'authentification

## 🔍 Vérification

### Méthode Serveur Local (automatique)

Si un port libre est trouvé (8080, 8090, etc.) :
- Une fenêtre de votre navigateur s'ouvrira automatiquement
- Vous serez redirigé vers Google pour autoriser l'application
- Après autorisation, vous serez redirigé vers le port local
- L'authentification se terminera automatiquement

### Méthode Console (si serveur local échoue)

Si tous les ports sont occupés :
- Un lien s'affichera dans Streamlit
- Cliquez sur le lien pour autoriser l'application
- Copiez le code d'autorisation depuis l'URL (la partie après `code=`)
- Collez-le dans le champ prévu dans Streamlit

## ⚠️ Notes importantes

- L'application teste automatiquement plusieurs ports (8080, 8090, 8091, 8092, 8093)
- Le premier port libre sera utilisé automatiquement
- Si aucun port n'est libre, la méthode console sera utilisée
- N'oubliez pas d'ajouter **tous les URI de redirection** dans Google Cloud Console

## 🆘 Si le problème persiste

1. Vérifiez que le fichier `client_secret.json` est dans le bon dossier
2. Vérifiez que **tous les URI de redirection** sont ajoutés (y compris `urn:ietf:wg:oauth:2.0:oob`)
3. Vérifiez que votre application OAuth est de type "Application de bureau"
4. Attendez quelques minutes après la modification (les changements peuvent prendre du temps à se propager)
5. Si vous utilisez la méthode console, assurez-vous de copier le code complet depuis l'URL

