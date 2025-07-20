# 🚀 EdRina Resto - Démarrage Rapide

## ⚡ Lancement Immédiat

### 1. Démarrage Automatique
```bash
# Exécutez simplement le script de démarrage
./start.sh
```

### 2. Démarrage Manuel

#### Backend (Terminal 1)
```bash
cd backend
source venv/bin/activate
python server.py
```

#### Frontend (Terminal 2)
```bash
cd frontend
yarn start
```

## 🌐 Accès à l'Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **Documentation API**: http://localhost:8000/docs

## 👤 Comptes de Test

### Administrateur
- **Login**: `admin`
- **Mot de passe**: `admin123`
- **Rôle**: Administrateur (accès complet)

### Serveur
- **Login**: `serveur1`
- **Mot de passe**: `serveur123`
- **Rôle**: Serveur

### Chef
- **Login**: `chef1`
- **Mot de passe**: `chef123`
- **Rôle**: Chef

### Caissier
- **Login**: `caisse1`
- **Mot de passe**: `caisse123`
- **Rôle**: Caisse

## 🍽️ Test Rapide du Système

1. **Connectez-vous en tant qu'admin** pour configurer le menu
2. **Ajoutez quelques plats** dans la gestion du menu
3. **Connectez-vous en tant que serveur** pour créer une commande
4. **Utilisez le compte chef** pour marquer les plats comme prêts
5. **Utilisez le compte caisse** pour encaisser les commandes

## 📱 Développement Android

Consultez le fichier `ANDROID_GUIDE.md` pour créer l'application mobile.

## 🔧 Dépannage

### Problème de Port
Si le port 3000 ou 8000 est occupé :
```bash
# Backend sur port 8001
uvicorn server:app --host 0.0.0.0 --port 8001

# Frontend sur port 3001
yarn start --port 3001
```

### Réinstallation des Dépendances
```bash
# Backend
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend
rm -rf node_modules yarn.lock
yarn install
```

## 📞 Support

Pour toute question ou personnalisation, consultez la documentation complète dans `DOCUMENTATION.md`.

---

**🎉 EdRina Resto est prêt à être utilisé ! Bon service ! 🍽️**