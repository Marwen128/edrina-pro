#!/bin/bash

echo "🍽️ EdRina Resto - Démarrage du système..."
echo "============================================="

# Fonction pour vérifier si Python est installé
check_python() {
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 n'est pas installé. Veuillez l'installer d'abord."
        exit 1
    fi
    echo "✅ Python 3 détecté"
}

# Fonction pour vérifier si Node.js est installé
check_node() {
    if ! command -v node &> /dev/null; then
        echo "❌ Node.js n'est pas installé. Veuillez l'installer d'abord."
        exit 1
    fi
    echo "✅ Node.js détecté"
}

# Fonction pour vérifier si Yarn est installé
check_yarn() {
    if ! command -v yarn &> /dev/null; then
        echo "❌ Yarn n'est pas installé. Installation en cours..."
        npm install -g yarn
    fi
    echo "✅ Yarn détecté"
}

# Installation du backend
setup_backend() {
    echo ""
    echo "🔧 Configuration du backend..."
    cd backend
    
    if [ ! -d "venv" ]; then
        echo "📦 Création de l'environnement virtuel Python..."
        python3 -m venv venv
    fi
    
    echo "📦 Installation des dépendances Python..."
    source venv/bin/activate
    pip install -r requirements.txt
    
    cd ..
    echo "✅ Backend configuré"
}

# Installation du frontend
setup_frontend() {
    echo ""
    echo "🔧 Configuration du frontend..."
    cd frontend
    
    echo "📦 Installation des dépendances Node.js..."
    yarn install
    
    cd ..
    echo "✅ Frontend configuré"
}

# Démarrage des services
start_services() {
    echo ""
    echo "🚀 Démarrage des services..."
    
    # Démarrer le backend en arrière-plan
    echo "🔥 Démarrage du backend FastAPI..."
    cd backend
    source venv/bin/activate
    python server.py &
    BACKEND_PID=$!
    cd ..
    
    # Attendre un peu que le backend démarre
    sleep 3
    
    # Démarrer le frontend
    echo "🎨 Démarrage du frontend React..."
    cd frontend
    yarn start &
    FRONTEND_PID=$!
    cd ..
    
    echo ""
    echo "🎉 EdRina Resto est démarré !"
    echo "================================"
    echo "🔗 Frontend: http://localhost:3000"
    echo "🔗 Backend API: http://localhost:8000"
    echo "🔗 Documentation API: http://localhost:8000/docs"
    echo ""
    echo "👤 Compte admin par défaut:"
    echo "   Utilisateur: admin"
    echo "   Mot de passe: admin123"
    echo ""
    echo "❌ Pour arrêter, appuyez sur Ctrl+C"
    
    # Attendre que l'utilisateur arrête les services
    wait $BACKEND_PID $FRONTEND_PID
}

# Fonction principale
main() {
    check_python
    check_node
    check_yarn
    setup_backend
    setup_frontend
    start_services
}

# Gestion des signaux pour arrêter proprement
cleanup() {
    echo ""
    echo "🛑 Arrêt d'EdRina Resto..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Lancer le script principal
main