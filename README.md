# 🍽️ EdRina Resto - Système de Gestion de Restaurant

## 📋 Description

EdRina Resto est un logiciel de gestion complet pour restaurant développé spécialement pour **EdRina Resto**. Cette application web moderne permet de gérer efficacement les commandes, le menu, les utilisateurs et les paiements avec un système de rôles sécurisé.

## ✨ Fonctionnalités Principales

### 🔐 Authentification Sécurisée
- ✅ Système de login avec utilisateur + mot de passe
- ✅ 4 rôles d'utilisateur : **serveur**, **chef**, **caisse**, **admin**
- ✅ Accès refusé si login incorrect
- ✅ L'admin peut gérer tous les utilisateurs et mots de passe

### 🍽️ Gestion des Tables et Commandes
- ✅ **8 tables fixes** dans le restaurant
- ✅ Les serveurs peuvent sélectionner une table et enregistrer les commandes
- ✅ Ajout d'éléments du menu et validation des commandes
- ✅ Envoi automatique vers la cuisine et la caisse
- ✅ Modification des commandes avec restrictions par rôle
- ✅ Horodatage de toutes les opérations (création, modification, préparation, encaissement)

### 👨‍🍳 Interface Chef
- ✅ Visualisation des commandes avec numéro de table et nom du serveur
- ✅ Liste des plats à préparer
- ✅ Marquage des commandes comme "prêtes"
- ✅ Notification automatique au serveur quand une commande est prête

### 💰 Interface Caisse
- ✅ Affichage des commandes prêtes à encaisser
- ✅ Calcul automatique en **Dinars Tunisiens (TND)**
- ✅ Statut "Payée" ou "En attente"
- ✅ Historique complet des paiements avec dates et heures

### 📦 Gestion du Menu
- ✅ Interface pour ajouter, modifier ou supprimer des articles
- ✅ Nom, description optionnelle et prix en TND
- ✅ Modification réservée aux administrateurs

### 👥 Gestion des Utilisateurs
- ✅ Ajout/suppression d'utilisateurs par l'admin
- ✅ Attribution de rôles spécifiques
- ✅ Identifiants uniques pour chaque utilisateur

### 🎨 Interface Utilisateur (UI/UX)
- ✅ Design moderne et intuitif avec thème bleu
- ✅ Compatible ordinateur, tablette et mobile (Responsive)
- ✅ Navigation fluide et rapide

### 🔔 Notifications
- ✅ Notifications automatiques au serveur quand une commande est prête

### 📊 Données & Sauvegarde
- ✅ Stockage sécurisé des données
- ✅ Historique complet avec horodatage
- ✅ Export des données possible

## 🛠️ Technologies Utilisées

### Backend
- **FastAPI** - Framework Python moderne et rapide
- **JWT** - Authentification sécurisée
- **bcrypt** - Chiffrement des mots de passe
- **Pydantic** - Validation des données

### Frontend
- **React 19** - Framework JavaScript moderne
- **Tailwind CSS** - Styling moderne et responsive
- **Axios** - Communication avec l'API
- **React Router** - Navigation

## 🚀 Installation et Démarrage

### Prérequis
- Python 3.8+
- Node.js 16+
- Yarn ou npm

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python server.py
```

### Frontend
```bash
cd frontend
yarn install
yarn start
```

## 🔑 Accès par Défaut

### Administrateur
- **Utilisateur :** `admin`
- **Mot de passe :** `admin123`

L'administrateur peut ensuite créer des comptes pour :
- **Serveurs** (`serveur`)
- **Chefs** (`chef`) 
- **Caissiers** (`caisse`)

## 📱 URLs d'accès

- **Backend API :** http://localhost:8000
- **Frontend Web :** http://localhost:3000
- **Documentation API :** http://localhost:8000/docs

## 🏗️ Architecture

```
EdRina Resto/
├── backend/           # API FastAPI
│   ├── server.py      # Serveur principal
│   └── requirements.txt
├── frontend/          # Application React
│   ├── src/
│   │   ├── App.js     # Composant principal
│   │   └── App.css    # Styles
│   └── package.json
└── README.md
```

## 👥 Rôles et Permissions

### 🔐 Admin
- ✅ Gestion complète des utilisateurs
- ✅ Modification du menu
- ✅ Modification de toutes les commandes
- ✅ Accès aux statistiques
- ✅ Export des données

### 👨‍🍳 Chef
- ✅ Gestion du menu (ajout/modification d'articles)
- ✅ Visualisation des commandes en cuisine
- ✅ Marquage des commandes comme prêtes

### 💰 Caisse
- ✅ Visualisation des commandes prêtes
- ✅ Encaissement des commandes
- ✅ Historique des paiements
- ✅ Statistiques financières

### 🍽️ Serveur
- ✅ Création de nouvelles commandes
- ✅ Modification de ses propres commandes (tant qu'elles ne sont pas préparées)
- ✅ Visualisation de ses commandes
- ✅ Réception de notifications

## 📊 Menu d'Exemple

Le système est livré avec un menu tunisien traditionnel :
- **Couscous Royal** - 18.5 TND
- **Tajine Agneau** - 22.0 TND  
- **Brick à l'oeuf** - 8.0 TND
- **Salade Mechouia** - 12.0 TND
- **Makrouda** - 6.0 TND
- **Thé à la menthe** - 4.0 TND

## 🔄 Workflow des Commandes

1. **Serveur** crée une commande pour une table (1-8)
2. Commande envoyée automatiquement en **cuisine** et à la **caisse**
3. **Chef** prépare et marque comme "prête"
4. **Notification automatique** envoyée au serveur
5. **Caisse** encaisse la commande
6. Historique sauvegardé avec horodatage

## 🔮 Évolutions Prévues

- 📱 Application Android (APK)
- 🏷️ Commande via QR code
- 📈 Statistiques et rapports avancés
- 🏢 Support multi-restaurants
- 💬 Système de messagerie interne
- 📤 Export PDF/Excel

## 📧 Support

Pour toute question ou assistance, contactez l'équipe de développement.

---

**© 2024 Marwen Ben Jemaa - All rights reserved by EdRina Resto.**
