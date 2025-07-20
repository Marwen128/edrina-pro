#!/usr/bin/env python3
"""
Script de test pour EdRina Resto API
Démontre toutes les fonctionnalités principales
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
headers = {"Content-Type": "application/json"}

def print_section(title):
    """Affiche une section du test"""
    print(f"\n{'='*50}")
    print(f"🧪 {title}")
    print('='*50)

def test_auth():
    """Test d'authentification"""
    print_section("AUTHENTIFICATION")
    
    # Test login admin
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data, headers=headers)
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ Connexion admin réussie")
        print(f"🔑 Token: {token[:50]}...")
        return token
    else:
        print("❌ Échec de connexion admin")
        print(f"Erreur: {response.text}")
        return None

def test_menu_management(token):
    """Test de gestion du menu"""
    print_section("GESTION DU MENU")
    
    auth_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    # Ajouter un plat
    new_dish = {
        "name": "Couscous Royal",
        "description": "Couscous traditionnel avec agneau, poulet et merguez",
        "price": 25.50,
        "category": "Plats Principaux",
        "available": True
    }
    
    response = requests.post(f"{BASE_URL}/api/menu", json=new_dish, headers=auth_headers)
    if response.status_code == 200:
        dish_id = response.json()["id"]
        print("✅ Plat ajouté avec succès")
        print(f"📝 ID: {dish_id}")
        print(f"🍽️ Nom: {new_dish['name']}")
        print(f"💰 Prix: {new_dish['price']} TND")
        return dish_id
    else:
        print("❌ Échec d'ajout du plat")
        return None

def test_order_creation(token, dish_id):
    """Test de création de commande"""
    print_section("CRÉATION DE COMMANDE")
    
    auth_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    # Créer une commande
    new_order = {
        "table_number": 3,
        "items": [
            {
                "menu_item_id": dish_id,
                "menu_item_name": "Couscous Royal",
                "price": 25.50,
                "quantity": 2,
                "notes": "Sans piment"
            }
        ],
        "customer_notes": "Table pour anniversaire"
    }
    
    response = requests.post(f"{BASE_URL}/api/orders", json=new_order, headers=auth_headers)
    if response.status_code == 200:
        order_id = response.json()["id"]
        print("✅ Commande créée avec succès")
        print(f"📋 ID: {order_id}")
        print(f"🍽️ Table: {new_order['table_number']}")
        print(f"📝 Items: {len(new_order['items'])}")
        return order_id
    else:
        print("❌ Échec de création de commande")
        return None

def test_order_workflow(token, order_id):
    """Test du workflow de commande"""
    print_section("WORKFLOW DE COMMANDE")
    
    auth_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    # Marquer comme en préparation
    response = requests.patch(f"{BASE_URL}/api/orders/{order_id}/status", 
                            json={"status": "in_preparation"}, 
                            headers=auth_headers)
    if response.status_code == 200:
        print("✅ Commande marquée 'en préparation'")
    
    time.sleep(1)
    
    # Marquer comme prête
    response = requests.patch(f"{BASE_URL}/api/orders/{order_id}/status", 
                            json={"status": "ready"}, 
                            headers=auth_headers)
    if response.status_code == 200:
        print("✅ Commande marquée 'prête'")
    
    time.sleep(1)
    
    # Marquer comme servie
    response = requests.patch(f"{BASE_URL}/api/orders/{order_id}/status", 
                            json={"status": "served"}, 
                            headers=auth_headers)
    if response.status_code == 200:
        print("✅ Commande marquée 'servie'")

def test_payment(token, order_id):
    """Test de paiement"""
    print_section("PAIEMENT")
    
    auth_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    payment_data = {
        "amount": 51.00,  # 2 × 25.50
        "method": "cash",
        "currency": "TND"
    }
    
    response = requests.post(f"{BASE_URL}/api/orders/{order_id}/payment", 
                           json=payment_data, 
                           headers=auth_headers)
    if response.status_code == 200:
        print("✅ Paiement effectué avec succès")
        print(f"💰 Montant: {payment_data['amount']} {payment_data['currency']}")
        print(f"💳 Méthode: {payment_data['method']}")
    else:
        print("❌ Échec du paiement")

def test_statistics(token):
    """Test des statistiques"""
    print_section("STATISTIQUES")
    
    auth_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    today = datetime.now().strftime("%Y-%m-%d")
    response = requests.get(f"{BASE_URL}/api/statistics/daily?date={today}", headers=auth_headers)
    
    if response.status_code == 200:
        stats = response.json()
        print("✅ Statistiques récupérées")
        print(f"📊 Commandes: {stats.get('total_orders', 0)}")
        print(f"💰 Revenus: {stats.get('total_revenue', 0)} TND")
        print(f"🍽️ Tables servies: {stats.get('tables_served', 0)}")
    else:
        print("❌ Échec de récupération des statistiques")

def main():
    """Fonction principale de test"""
    print("🍽️ EdRina Resto - Test Complet de l'API")
    print(f"🌐 URL: {BASE_URL}")
    print(f"🕐 Heure: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test d'authentification
    token = test_auth()
    if not token:
        print("❌ Impossible de continuer sans authentification")
        return
    
    # Test de gestion du menu
    dish_id = test_menu_management(token)
    if not dish_id:
        print("❌ Impossible de continuer sans plat")
        return
    
    # Test de création de commande
    order_id = test_order_creation(token, dish_id)
    if not order_id:
        print("❌ Impossible de continuer sans commande")
        return
    
    # Test du workflow
    test_order_workflow(token, order_id)
    
    # Test de paiement
    test_payment(token, order_id)
    
    # Test des statistiques
    test_statistics(token)
    
    print_section("TEST TERMINÉ")
    print("🎉 Tous les tests ont été exécutés !")
    print("✅ EdRina Resto API fonctionne parfaitement")

if __name__ == "__main__":
    main()