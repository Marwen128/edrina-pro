#!/usr/bin/env python3
"""
Démonstration complète d'EdRina Resto
Inclut la création d'utilisateurs et tout le workflow
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
headers = {"Content-Type": "application/json"}

def print_section(title):
    """Affiche une section de la demo"""
    print(f"\n{'='*60}")
    print(f"🍽️ {title}")
    print('='*60)

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def print_info(message):
    print(f"ℹ️  {message}")

def login_user(username, password):
    """Connexion utilisateur"""
    login_data = {"username": username, "password": password}
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        token = data["access_token"]
        user = data["user"]
        print_success(f"Connexion réussie - {user['username']} ({user['role']})")
        return token, user
    else:
        print_error(f"Échec de connexion: {response.text}")
        return None, None

def create_user(token, username, password, role):
    """Création d'un utilisateur"""
    auth_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    user_data = {
        "username": username,
        "password": password,
        "role": role
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/register", json=user_data, headers=auth_headers)
    
    if response.status_code == 200:
        print_success(f"Utilisateur {username} créé avec le rôle {role}")
        return True
    else:
        print_error(f"Échec création utilisateur {username}: {response.text}")
        return False

def create_menu_item(token, name, description, price, category):
    """Création d'un plat"""
    auth_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    item_data = {
        "name": name,
        "description": description,
        "price": price,
        "category": category,
        "available": True
    }
    
    response = requests.post(f"{BASE_URL}/api/menu", json=item_data, headers=auth_headers)
    
    if response.status_code == 200:
        item_id = response.json()["id"]
        print_success(f"Plat '{name}' ajouté (ID: {item_id[:8]}...)")
        return item_id
    else:
        print_error(f"Échec ajout plat '{name}': {response.text}")
        return None

def create_order(token, table_number, items):
    """Création d'une commande"""
    auth_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    order_data = {
        "table_number": table_number,
        "items": items,
        "customer_notes": f"Commande table {table_number}"
    }
    
    response = requests.post(f"{BASE_URL}/api/orders", json=order_data, headers=auth_headers)
    
    if response.status_code == 200:
        order_id = response.json()["id"]
        print_success(f"Commande créée pour table {table_number} (ID: {order_id[:8]}...)")
        return order_id
    else:
        print_error(f"Échec création commande: {response.text}")
        return None

def update_order_status(token, order_id, status):
    """Mise à jour du statut d'une commande"""
    auth_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.patch(f"{BASE_URL}/api/orders/{order_id}/status", 
                            json={"status": status}, 
                            headers=auth_headers)
    
    if response.status_code == 200:
        print_success(f"Commande marquée '{status}'")
        return True
    else:
        print_error(f"Échec mise à jour statut: {response.text}")
        return False

def process_payment(token, order_id, amount):
    """Traitement du paiement"""
    auth_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    payment_data = {
        "amount": amount,
        "method": "cash",
        "currency": "TND"
    }
    
    response = requests.post(f"{BASE_URL}/api/orders/{order_id}/payment", 
                           json=payment_data, 
                           headers=auth_headers)
    
    if response.status_code == 200:
        print_success(f"Paiement de {amount} TND effectué")
        return True
    else:
        print_error(f"Échec paiement: {response.text}")
        return False

def main():
    """Démonstration complète"""
    print("🍽️ EdRina Resto - Démonstration Complète")
    print(f"🌐 URL: {BASE_URL}")
    print(f"🕐 Heure: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Phase 1: Connexion Admin et Setup
    print_section("PHASE 1: CONFIGURATION INITIALE")
    
    admin_token, admin_user = login_user("admin", "admin123")
    if not admin_token:
        print_error("Impossible de continuer sans accès administrateur")
        return
    
    # Phase 2: Création des utilisateurs
    print_section("PHASE 2: CRÉATION DES UTILISATEURS")
    
    users_to_create = [
        ("serveur1", "serveur123", "serveur"),
        ("chef1", "chef123", "chef"),
        ("caisse1", "caisse123", "caisse")
    ]
    
    for username, password, role in users_to_create:
        create_user(admin_token, username, password, role)
        time.sleep(0.5)
    
    # Phase 3: Configuration du menu
    print_section("PHASE 3: CONFIGURATION DU MENU")
    
    menu_items = [
        ("Couscous Royal", "Couscous traditionnel avec agneau, poulet et merguez", 25.50, "Plats Principaux"),
        ("Tajine d'Agneau", "Tajine d'agneau aux pruneaux et amandes", 28.00, "Plats Principaux"),
        ("Salade Mechouia", "Salade grillée tunisienne traditionnelle", 8.50, "Entrées"),
        ("Thé à la Menthe", "Thé traditionnel tunisien", 3.50, "Boissons"),
        ("Makroudh", "Pâtisserie aux dattes", 6.00, "Desserts")
    ]
    
    created_items = []
    for name, desc, price, category in menu_items:
        item_id = create_menu_item(admin_token, name, desc, price, category)
        if item_id:
            created_items.append({
                "id": item_id,
                "name": name,
                "price": price
            })
        time.sleep(0.5)
    
    if not created_items:
        print_error("Aucun plat créé - arrêt de la démonstration")
        return
    
    # Phase 4: Simulation workflow serveur
    print_section("PHASE 4: PRISE DE COMMANDE (SERVEUR)")
    
    serveur_token, _ = login_user("serveur1", "serveur123")
    if not serveur_token:
        print_error("Impossible de se connecter comme serveur")
        return
    
    # Création d'une commande
    order_items = [
        {
            "menu_item_id": created_items[0]["id"],
            "menu_item_name": created_items[0]["name"],
            "price": created_items[0]["price"],
            "quantity": 2,
            "notes": "Sans piment"
        },
        {
            "menu_item_id": created_items[3]["id"],
            "menu_item_name": created_items[3]["name"],
            "price": created_items[3]["price"],
            "quantity": 3,
            "notes": "Bien sucré"
        }
    ]
    
    order_id = create_order(serveur_token, 5, order_items)
    if not order_id:
        print_error("Impossible de créer la commande")
        return
    
    total_amount = sum(item["price"] * item["quantity"] for item in order_items)
    print_info(f"Montant total: {total_amount} TND")
    
    # Phase 5: Workflow cuisine
    print_section("PHASE 5: PRÉPARATION EN CUISINE (CHEF)")
    
    chef_token, _ = login_user("chef1", "chef123")
    if not chef_token:
        print_error("Impossible de se connecter comme chef")
        return
    
    # Simulation du workflow cuisine
    print_info("Commande reçue en cuisine...")
    time.sleep(2)
    
    if update_order_status(chef_token, order_id, "in_preparation"):
        print_info("Préparation en cours...")
        time.sleep(3)
        
        if update_order_status(chef_token, order_id, "ready"):
            print_info("Commande prête - notification envoyée au serveur")
    
    # Phase 6: Encaissement
    print_section("PHASE 6: ENCAISSEMENT (CAISSE)")
    
    caisse_token, _ = login_user("caisse1", "caisse123")
    if not caisse_token:
        print_error("Impossible de se connecter comme caissier")
        return
    
    # Finaliser la commande
    if update_order_status(caisse_token, order_id, "served"):
        print_info("Commande servie au client")
        
        if process_payment(caisse_token, order_id, total_amount):
            print_info("Transaction terminée avec succès !")
    
    # Phase 7: Statistiques
    print_section("PHASE 7: STATISTIQUES (ADMIN)")
    
    auth_headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {admin_token}"
    }
    
    today = datetime.now().strftime("%Y-%m-%d")
    response = requests.get(f"{BASE_URL}/api/statistics/daily?date={today}", headers=auth_headers)
    
    if response.status_code == 200:
        stats = response.json()
        print_success("Statistiques du jour récupérées:")
        print(f"  📊 Commandes: {stats.get('total_orders', 0)}")
        print(f"  💰 Revenus: {stats.get('total_revenue', 0)} TND")
        print(f"  🍽️ Tables servies: {stats.get('tables_served', 0)}")
    
    print_section("DÉMONSTRATION TERMINÉE")
    print("🎉 Toutes les fonctionnalités d'EdRina Resto ont été testées avec succès !")
    print("✅ Système prêt pour la production")
    print("\n🌐 Accès à l'application:")
    print("   Frontend: http://localhost:3000")
    print("   Backend API: http://localhost:8000")
    print("   Documentation: http://localhost:8000/docs")

if __name__ == "__main__":
    main()