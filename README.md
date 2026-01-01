# 🛒 Cogiteo App Facture

Application web de gestion de factures pour les achats en restaurant/marché, avec intégration Google Drive.

## ✨ Fonctionnalités

- 🔐 **Authentification utilisateur** : Création de compte et connexion sécurisée
- 📝 **Saisie de factures** : Ajout progressif d'articles avec calcul automatique
- 📄 **Génération PDF** : Création automatique de factures au format PDF
- ☁️ **Stockage Google Drive** : Envoi automatique des factures sur Google Drive
- 📷 **Scan de photos** : Conversion d'images en PDF et envoi sur Drive
- 📂 **Historique** : Consultation de l'historique des factures par utilisateur

## 🚀 Installation

### Prérequis

- Python 3.8 ou supérieur
- Un compte Google avec accès à Google Drive API

### Étapes d'installation

1. **Cloner le dépôt**
   ```bash
   git clone https://github.com/Andj04/Cogiteo-App-Facture.git
   cd Cogiteo-App-Facture
   ```

2. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurer Google Drive OAuth**
   - Allez sur [Google Cloud Console](https://console.cloud.google.com/)
   - Créez un nouveau projet ou sélectionnez un projet existant
   - Activez l'API Google Drive
   - Créez des identifiants OAuth 2.0 (type "Application de bureau")
   - Téléchargez le fichier `client_secret.json`
   - Placez-le dans le dossier racine du projet
   - **Configurez les URI de redirection** (voir [CONFIGURATION_OAUTH.md](CONFIGURATION_OAUTH.md))

4. **Lancer l'application**
   ```bash
   streamlit run main.py
   ```

## 📋 Configuration Google Drive

Pour utiliser la fonctionnalité d'upload sur Google Drive, vous devez :

1. Configurer les URI de redirection dans Google Cloud Console :
   - `urn:ietf:wg:oauth:2.0:oob`
   - `http://localhost:8080/`
   - `http://localhost:8090/`

2. Consultez le fichier [CONFIGURATION_OAUTH.md](CONFIGURATION_OAUTH.md) pour plus de détails.

## ☁️ Déploiement sur Streamlit Community Cloud

L'application peut être déployée gratuitement sur Streamlit Community Cloud :

1. Poussez votre code sur GitHub
2. Allez sur https://share.streamlit.io/
3. Connectez-vous avec votre compte GitHub
4. Sélectionnez votre dépôt et configurez l'application
5. Configurez les secrets Google Drive dans les paramètres

📖 **Guide complet** : Consultez [DEPLOY_STREAMLIT_CLOUD.md](DEPLOY_STREAMLIT_CLOUD.md) pour les instructions détaillées.

## 🏗️ Structure du projet

```
Cogiteo-App-Facture/
├── main.py                      # Application principale Streamlit
├── database.py                  # Gestion de la base de données SQLite
├── drive_service.py             # Service Google Drive OAuth
├── pdf_generator.py             # Génération de factures PDF
├── requirements.txt             # Dépendances Python
├── CONFIGURATION_OAUTH.md       # Guide de configuration OAuth
├── DEPLOY_STREAMLIT_CLOUD.md    # Guide de déploiement Streamlit Cloud
├── .gitignore                   # Fichiers à ignorer par Git
└── README.md                    # Ce fichier
```

## 🔒 Fichiers sensibles

Les fichiers suivants ne doivent **PAS** être commités sur Git :
- `client_secret.json` (identifiants OAuth)
- `token.json` (token d'authentification)
- `app_database.db` (base de données locale)
- `*.pdf` (factures générées)

Ces fichiers sont automatiquement ignorés par `.gitignore`.

## 📖 Utilisation

1. **Créer un compte** : Utilisez l'option "Créer un compte" pour vous inscrire
2. **Se connecter** : Connectez-vous avec votre nom d'utilisateur et mot de passe
3. **Créer une facture** :
   - Entrez le nom du marché/fournisseur
   - Ajoutez vos articles (produit, unité, quantité, prix unitaire)
   - Cliquez sur "Valider et Calculer Total"
   - Cliquez sur "Générer la Facture PDF"
4. **Upload sur Drive** : Cliquez sur "Envoyer sur Google Drive" pour sauvegarder automatiquement

## 🛠️ Technologies utilisées

- **Streamlit** : Framework web Python
- **SQLite** : Base de données locale
- **FPDF** : Génération de PDF
- **Google Drive API** : Stockage cloud
- **Pandas** : Manipulation de données

## 📝 Licence

Ce projet est sous licence MIT.

## 👤 Auteur

**Andj04**

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

