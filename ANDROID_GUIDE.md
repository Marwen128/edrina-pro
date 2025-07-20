# 📱 EdRina Resto - Guide de Développement Android

## 🎯 Objectif

Ce guide explique comment créer une application Android native pour EdRina Resto basée sur l'API existante.

## 🛠️ Technologies Recommandées

### Option 1: React Native (Recommandé)
- **Avantages**: Réutilisation du code React existant
- **Framework**: React Native + Expo
- **Navigation**: React Navigation
- **State Management**: Context API + AsyncStorage

### Option 2: Flutter
- **Avantages**: Performance native, UI moderne
- **Langage**: Dart
- **HTTP**: dio package
- **State Management**: Provider ou Riverpod

### Option 3: Android Natif
- **Avantages**: Performance maximale
- **Langage**: Kotlin
- **Architecture**: MVVM avec LiveData
- **HTTP**: Retrofit + OkHttp

## 🚀 Approche React Native (Recommandée)

### 1. Installation
```bash
# Installation d'Expo CLI
npm install -g @expo/cli

# Création du projet
npx create-expo-app EdRinaRestoApp
cd EdRinaRestoApp

# Installation des dépendances essentielles
npm install @react-navigation/native @react-navigation/stack
npm install react-native-screens react-native-safe-area-context
npm install axios react-native-async-storage/async-storage
npm install @expo/vector-icons
```

### 2. Structure du Projet
```
EdRinaRestoApp/
├── src/
│   ├── components/     # Composants réutilisables
│   ├── screens/        # Écrans de l'app
│   │   ├── LoginScreen.js
│   │   ├── ServerScreen.js
│   │   ├── ChefScreen.js
│   │   └── CashierScreen.js
│   ├── services/       # API calls
│   │   └── api.js
│   ├── contexts/       # Context API
│   │   └── AuthContext.js
│   └── utils/          # Utilitaires
├── app.json
└── App.js
```

### 3. Configuration API
```javascript
// src/services/api.js
import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';

const API_BASE_URL = 'http://YOUR_SERVER_IP:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur pour ajouter le token
api.interceptors.request.use(async (config) => {
  const token = await AsyncStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
```

### 4. Contexte d'Authentification
```javascript
// src/contexts/AuthContext.js
import React, { createContext, useContext, useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import api from '../services/api';

const AuthContext = createContext();

export const useAuth = () => useContext(AuthContext);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const token = await AsyncStorage.getItem('token');
      if (token) {
        const response = await api.get('/auth/me');
        setUser(response.data);
      }
    } catch (error) {
      await AsyncStorage.removeItem('token');
    } finally {
      setLoading(false);
    }
  };

  const login = async (username, password) => {
    const response = await api.post('/auth/login', { username, password });
    const { access_token, user: userData } = response.data;
    
    await AsyncStorage.setItem('token', access_token);
    setUser(userData);
    return userData;
  };

  const logout = async () => {
    await AsyncStorage.removeItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};
```

### 5. Écran de Login
```javascript
// src/screens/LoginScreen.js
import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, Alert, StyleSheet } from 'react-native';
import { useAuth } from '../contexts/AuthContext';

export default function LoginScreen() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const handleLogin = async () => {
    if (!username || !password) {
      Alert.alert('Erreur', 'Veuillez remplir tous les champs');
      return;
    }

    setLoading(true);
    try {
      await login(username, password);
    } catch (error) {
      Alert.alert('Erreur', 'Identifiants incorrects');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>EdRina Resto</Text>
      <Text style={styles.subtitle}>Système de Gestion Restaurant</Text>
      
      <TextInput
        style={styles.input}
        placeholder="Nom d'utilisateur"
        value={username}
        onChangeText={setUsername}
        autoCapitalize="none"
      />
      
      <TextInput
        style={styles.input}
        placeholder="Mot de passe"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />
      
      <TouchableOpacity 
        style={styles.button} 
        onPress={handleLogin}
        disabled={loading}
      >
        <Text style={styles.buttonText}>
          {loading ? 'Connexion...' : 'Se connecter'}
        </Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    padding: 20,
    backgroundColor: '#f5f5f5',
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    textAlign: 'center',
    color: '#1e40af',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    textAlign: 'center',
    color: '#6b7280',
    marginBottom: 40,
  },
  input: {
    borderWidth: 1,
    borderColor: '#d1d5db',
    borderRadius: 8,
    padding: 15,
    marginBottom: 15,
    backgroundColor: 'white',
  },
  button: {
    backgroundColor: '#1e40af',
    borderRadius: 8,
    padding: 15,
    alignItems: 'center',
  },
  buttonText: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 16,
  },
});
```

### 6. Navigation Principal
```javascript
// App.js
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { AuthProvider, useAuth } from './src/contexts/AuthContext';
import LoginScreen from './src/screens/LoginScreen';
import ServerScreen from './src/screens/ServerScreen';
import ChefScreen from './src/screens/ChefScreen';
import CashierScreen from './src/screens/CashierScreen';
import AdminScreen from './src/screens/AdminScreen';

const Stack = createStackNavigator();

function AppNavigator() {
  const { user, loading } = useAuth();

  if (loading) {
    return null; // Afficher un spinner de chargement
  }

  return (
    <NavigationContainer>
      <Stack.Navigator>
        {!user ? (
          <Stack.Screen 
            name="Login" 
            component={LoginScreen} 
            options={{ headerShown: false }}
          />
        ) : (
          <>
            {user.role === 'serveur' && (
              <Stack.Screen name="Server" component={ServerScreen} />
            )}
            {user.role === 'chef' && (
              <Stack.Screen name="Chef" component={ChefScreen} />
            )}
            {user.role === 'caisse' && (
              <Stack.Screen name="Cashier" component={CashierScreen} />
            )}
            {user.role === 'admin' && (
              <Stack.Screen name="Admin" component={AdminScreen} />
            )}
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppNavigator />
    </AuthProvider>
  );
}
```

## 📦 Génération de l'APK

### Avec Expo (Recommandé)
```bash
# Build pour Android
expo build:android

# Ou avec EAS Build (nouvelle méthode)
npm install -g @expo/eas-cli
eas build --platform android
```

### Configuration app.json
```json
{
  "expo": {
    "name": "EdRina Resto",
    "slug": "edrina-resto",
    "version": "1.0.0",
    "orientation": "portrait",
    "icon": "./assets/icon.png",
    "splash": {
      "image": "./assets/splash.png",
      "resizeMode": "contain",
      "backgroundColor": "#1e40af"
    },
    "android": {
      "package": "com.edrina.resto",
      "versionCode": 1,
      "icon": "./assets/android-icon.png",
      "permissions": [
        "INTERNET",
        "ACCESS_NETWORK_STATE"
      ]
    }
  }
}
```

## 🔧 Fonctionnalités Spécifiques Mobile

### 1. Notifications Push
```bash
npm install expo-notifications
```

### 2. Scanner QR Code (pour évolution future)
```bash
npm install expo-barcode-scanner
```

### 3. Stockage Offline
```bash
npm install @react-native-async-storage/async-storage
npm install react-native-sqlite-storage
```

### 4. Mode Hors Ligne
```javascript
// Synchronisation des données offline
import NetInfo from '@react-native-netinfo';

const useOfflineSync = () => {
  const [isConnected, setIsConnected] = useState(true);

  useEffect(() => {
    const unsubscribe = NetInfo.addEventListener(state => {
      setIsConnected(state.isConnected);
      if (state.isConnected) {
        syncOfflineData();
      }
    });

    return unsubscribe;
  }, []);

  const syncOfflineData = async () => {
    // Synchroniser les commandes en attente
    // Envoyer les données stockées localement
  };
};
```

## 🎨 Design Mobile

### Thème Cohérent
```javascript
const theme = {
  colors: {
    primary: '#1e40af',
    secondary: '#3b82f6',
    success: '#10b981',
    warning: '#f59e0b',
    error: '#ef4444',
    background: '#f9fafb',
    surface: '#ffffff',
    text: '#111827',
  },
  spacing: {
    xs: 4,
    sm: 8,
    md: 16,
    lg: 24,
    xl: 32,
  },
};
```

### Composants Adaptatifs
- **Tables**: Grille de 2x4 pour les 8 tables
- **Menu**: Liste avec images et prix
- **Commandes**: Cards avec statuts colorés
- **Boutons**: Taille tactile optimisée (44px minimum)

## 🚀 Déploiement

### 1. Google Play Store
1. Créer un compte développeur Google Play (25$ unique)
2. Générer l'APK de production
3. Télécharger sur Google Play Console
4. Remplir les métadonnées (description, captures d'écran)
5. Publier

### 2. APK Direct
1. Générer l'APK de production
2. Signer l'APK avec votre clé
3. Distribuer directement aux utilisateurs

## 📊 Fonctionnalités Mobiles Avancées

### Géolocalisation
- Vérification de présence au restaurant
- Limitation d'accès par zone géographique

### Mode Tablette
- Interface optimisée pour les tablettes des serveurs
- Affichage plus grand pour la cuisine

### Sécurité
- Biométrie (empreinte digitale)
- Verrouillage automatique après inactivité
- Chiffrement des données locales

## 🔄 Synchronisation en Temps Réel

### WebSocket pour Notifications
```javascript
import io from 'socket.io-client';

const useRealtimeUpdates = () => {
  useEffect(() => {
    const socket = io('ws://YOUR_SERVER_IP:8000');
    
    socket.on('order_ready', (data) => {
      // Notification pour le serveur
      scheduleNotification('Commande prête!', `Table ${data.table_number}`);
    });

    return () => socket.disconnect();
  }, []);
};
```

---

## 📝 Conclusion

Ce guide fournit une base solide pour développer l'application Android d'EdRina Resto. L'approche React Native est recommandée pour sa rapidité de développement et la réutilisation du code existant.

**Étapes suivantes recommandées :**
1. Configurer l'environnement React Native
2. Implémenter l'authentification et la navigation
3. Développer les écrans spécifiques à chaque rôle
4. Tester sur différents appareils
5. Optimiser les performances
6. Publier sur Google Play Store

---

**© 2024 Marwen Ben Jemaa - All rights reserved by EdRina Resto.**