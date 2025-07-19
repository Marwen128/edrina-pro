import React, { useState, useEffect, createContext, useContext } from 'react';
import axios from 'axios';
import './App.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Auth Context
const AuthContext = createContext();

const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      fetchUser();
    } else {
      setLoading(false);
    }
  }, [token]);

  const fetchUser = async () => {
    try {
      const response = await axios.get(`${API}/auth/me`);
      setUser(response.data);
    } catch (error) {
      console.error('Failed to fetch user:', error);
      logout();
    } finally {
      setLoading(false);
    }
  };

  const login = async (username, password) => {
    try {
      const response = await axios.post(`${API}/auth/login`, { username, password });
      const { access_token, user: userData } = response.data;
      
      localStorage.setItem('token', access_token);
      setToken(access_token);
      setUser(userData);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      return true;
    } catch (error) {
      console.error('Login failed:', error);
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    delete axios.defaults.headers.common['Authorization'];
  };

  const value = {
    user,
    token,
    loading,
    login,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Login Component
const LoginPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const success = await login(username, password);
    if (!success) {
      setError('Nom d\'utilisateur ou mot de passe incorrect');
    }
    setLoading(false);
  };

  const initializeSystem = async () => {
    try {
      await axios.post(`${API}/init`);
      alert('Système initialisé avec l\'utilisateur admin (admin/admin123)');
    } catch (error) {
      console.error('Failed to initialize system:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 to-blue-600 flex items-center justify-center">
      <div className="bg-white p-8 rounded-xl shadow-2xl w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-blue-900 mb-2">EdRina Resto</h1>
          <p className="text-gray-600">Système de Gestion Restaurant</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Nom d'utilisateur
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Mot de passe
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>

          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 focus:ring-4 focus:ring-blue-200 font-medium transition-colors disabled:opacity-50"
          >
            {loading ? 'Connexion...' : 'Se connecter'}
          </button>
        </form>

        <div className="mt-6 text-center">
          <button
            onClick={initializeSystem}
            className="text-sm text-blue-600 hover:text-blue-800 underline"
          >
            Initialiser le système
          </button>
        </div>
      </div>
    </div>
  );
};

// Server Dashboard
const ServerDashboard = () => {
  const [orders, setOrders] = useState([]);
  const [menu, setMenu] = useState([]);
  const [selectedTable, setSelectedTable] = useState(1);
  const [currentOrder, setCurrentOrder] = useState([]);
  const [showCreateOrder, setShowCreateOrder] = useState(false);
  const [showEditOrder, setShowEditOrder] = useState(false);
  const [editingOrder, setEditingOrder] = useState(null);
  const { user, logout } = useAuth();

  useEffect(() => {
    fetchOrders();
    fetchMenu();
  }, []);

  const fetchOrders = async () => {
    try {
      const response = await axios.get(`${API}/orders`);
      setOrders(response.data);
    } catch (error) {
      console.error('Failed to fetch orders:', error);
    }
  };

  const fetchMenu = async () => {
    try {
      const response = await axios.get(`${API}/menu`);
      setMenu(response.data);
    } catch (error) {
      console.error('Failed to fetch menu:', error);
    }
  };

  const addToOrder = (menuItem) => {
    const existingItem = currentOrder.find(item => item.menu_item_id === menuItem.id);
    if (existingItem) {
      setCurrentOrder(currentOrder.map(item =>
        item.menu_item_id === menuItem.id
          ? { ...item, quantity: item.quantity + 1 }
          : item
      ));
    } else {
      setCurrentOrder([...currentOrder, {
        menu_item_id: menuItem.id,
        menu_item_name: menuItem.name,
        quantity: 1,
        price: menuItem.price
      }]);
    }
  };

  const removeFromOrder = (menuItemId) => {
    setCurrentOrder(currentOrder.filter(item => item.menu_item_id !== menuItemId));
  };

  const updateQuantity = (menuItemId, quantity) => {
    if (quantity === 0) {
      removeFromOrder(menuItemId);
    } else {
      setCurrentOrder(currentOrder.map(item =>
        item.menu_item_id === menuItemId
          ? { ...item, quantity }
          : item
      ));
    }
  };

  const submitOrder = async () => {
    if (currentOrder.length === 0) {
      alert('Veuillez ajouter des articles à la commande');
      return;
    }

    try {
      await axios.post(`${API}/orders`, {
        table_number: selectedTable,
        items: currentOrder
      });
      setCurrentOrder([]);
      setShowCreateOrder(false);
      fetchOrders();
      alert('Commande envoyée avec succès!');
    } catch (error) {
      console.error('Failed to create order:', error);
      alert('Erreur lors de la création de la commande');
    }
  };

  const startEditOrder = (order) => {
    setEditingOrder(order);
    setCurrentOrder([...order.items]);
    setSelectedTable(order.table_number);
    setShowEditOrder(true);
  };

  const updateExistingOrder = async () => {
    if (currentOrder.length === 0) {
      alert('Une commande doit contenir au moins un article');
      return;
    }

    try {
      await axios.put(`${API}/orders/${editingOrder.id}`, {
        items: currentOrder
      });
      setCurrentOrder([]);
      setShowEditOrder(false);
      setEditingOrder(null);
      fetchOrders();
      alert('Commande modifiée avec succès!');
    } catch (error) {
      console.error('Failed to update order:', error);
      alert('Erreur lors de la modification de la commande');
    }
  };

  const cancelEdit = () => {
    setCurrentOrder([]);
    setShowEditOrder(false);
    setEditingOrder(null);
  };

  const getOrderTotal = () => {
    return currentOrder.reduce((total, item) => total + (item.price * item.quantity), 0);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-blue-600 text-white p-4 flex justify-between items-center">
        <h1 className="text-xl font-bold">Serveur - {user.username}</h1>
        <button
          onClick={logout}
          className="bg-blue-700 px-4 py-2 rounded hover:bg-blue-800"
        >
          Déconnexion
        </button>
      </div>

      <div className="p-6">
        {/* Action Buttons */}
        <div className="mb-6 flex gap-4">
          <button
            onClick={() => setShowCreateOrder(true)}
            className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 font-medium"
          >
            Nouvelle Commande
          </button>
          <button
            onClick={fetchOrders}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 font-medium"
          >
            Actualiser
          </button>
        </div>

        {/* Orders List */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-bold text-gray-800 mb-4">Mes Commandes</h2>
          <div className="grid gap-4">
            {orders.map(order => (
              <div key={order.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <h3 className="font-semibold text-lg">Table {order.table_number}</h3>
                    <p className="text-gray-600">Commande #{order.id.slice(-6)}</p>
                  </div>
                  <div className="text-right">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                      order.status === 'in_kitchen' ? 'bg-orange-100 text-orange-800' :
                      order.status === 'ready' ? 'bg-green-100 text-green-800' :
                      order.status === 'paid' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                      {order.status === 'in_kitchen' ? 'En cuisine' :
                       order.status === 'ready' ? 'Prête' :
                       order.status === 'paid' ? 'Payée' : order.status}
                    </span>
                    <p className="text-lg font-bold mt-1">{order.total_amount.toFixed(2)} TND</p>
                  </div>
                </div>
                <div className="text-sm text-gray-600">
                  {order.items.map(item => (
                    <span key={item.menu_item_id} className="mr-4">
                      {item.menu_item_name} x{item.quantity}
                    </span>
                  ))}
                </div>
                <div className="flex justify-between items-center mt-2">
                  <p className="text-xs text-gray-500">
                    Créée: {new Date(order.created_at).toLocaleString('fr-FR')}
                  </p>
                  {order.status === 'in_kitchen' && (
                    <button
                      onClick={() => startEditOrder(order)}
                      className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700"
                    >
                      Modifier
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Create Order Modal */}
      {showCreateOrder && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-2xl font-bold">Nouvelle Commande</h2>
              <button
                onClick={() => setShowCreateOrder(false)}
                className="text-gray-500 hover:text-gray-700 text-2xl"
              >
                ×
              </button>
            </div>

            {/* Table Selection */}
            <div className="mb-6">
              <label className="block text-sm font-medium mb-2">Sélectionner la table:</label>
              <select
                value={selectedTable}
                onChange={(e) => setSelectedTable(Number(e.target.value))}
                className="border rounded px-3 py-2"
              >
                {[1, 2, 3, 4, 5, 6, 7, 8].map(num => (
                  <option key={num} value={num}>Table {num}</option>
                ))}
              </select>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              {/* Menu */}
              <div>
                <h3 className="text-lg font-semibold mb-4">Menu</h3>
                <div className="grid gap-3">
                  {menu.map(item => (
                    <div key={item.id} className="border rounded p-3 hover:shadow-md transition-shadow">
                      <div className="flex justify-between items-start">
                        <div>
                          <h4 className="font-medium">{item.name}</h4>
                          <p className="text-sm text-gray-600">{item.description}</p>
                          <p className="text-lg font-bold text-blue-600">{item.price.toFixed(2)} TND</p>
                        </div>
                        <button
                          onClick={() => addToOrder(item)}
                          className="bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 text-sm"
                        >
                          Ajouter
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Current Order */}
              <div>
                <h3 className="text-lg font-semibold mb-4">Commande en cours</h3>
                <div className="border rounded p-4 min-h-[300px]">
                  {currentOrder.length === 0 ? (
                    <p className="text-gray-500">Aucun article sélectionné</p>
                  ) : (
                    <div className="space-y-3">
                      {currentOrder.map(item => (
                        <div key={item.menu_item_id} className="flex justify-between items-center border-b pb-2">
                          <div>
                            <h4 className="font-medium">{item.menu_item_name}</h4>
                            <p className="text-sm text-gray-600">{item.price.toFixed(2)} TND chacun</p>
                          </div>
                          <div className="flex items-center gap-2">
                            <button
                              onClick={() => updateQuantity(item.menu_item_id, item.quantity - 1)}
                              className="bg-gray-200 w-8 h-8 rounded-full hover:bg-gray-300"
                            >
                              -
                            </button>
                            <span className="w-8 text-center">{item.quantity}</span>
                            <button
                              onClick={() => updateQuantity(item.menu_item_id, item.quantity + 1)}
                              className="bg-gray-200 w-8 h-8 rounded-full hover:bg-gray-300"
                            >
                              +
                            </button>
                            <button
                              onClick={() => removeFromOrder(item.menu_item_id)}
                              className="bg-red-500 text-white w-8 h-8 rounded-full hover:bg-red-600 ml-2"
                            >
                              ×
                            </button>
                          </div>
                        </div>
                      ))}
                      <div className="pt-3 border-t">
                        <p className="text-xl font-bold text-right">Total: {getOrderTotal().toFixed(2)} TND</p>
                      </div>
                    </div>
                  )}
                </div>
                
                <div className="mt-4 flex gap-3">
                  <button
                    onClick={submitOrder}
                    disabled={currentOrder.length === 0}
                    className="flex-1 bg-green-600 text-white py-2 px-4 rounded hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Envoyer la commande
                  </button>
                  <button
                    onClick={() => setCurrentOrder([])}
                    className="bg-gray-500 text-white py-2 px-4 rounded hover:bg-gray-600"
                  >
                    Vider
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Edit Order Modal */}
      {showEditOrder && editingOrder && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <div>
                <h2 className="text-2xl font-bold text-orange-600">Modifier la Commande</h2>
                <p className="text-gray-600">Table {editingOrder.table_number} - Commande #{editingOrder.id.slice(-6)}</p>
              </div>
              <button
                onClick={cancelEdit}
                className="text-gray-500 hover:text-gray-700 text-2xl"
              >
                ×
              </button>
            </div>

            <div className="bg-orange-50 border border-orange-200 p-3 rounded-lg mb-6">
              <p className="text-orange-800 text-sm">
                💡 <strong>Modification possible</strong> - Cette commande est en cours de préparation en cuisine. 
                Vous pouvez ajouter, supprimer ou modifier les quantités.
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-6">
              {/* Menu */}
              <div>
                <h3 className="text-lg font-semibold mb-4">Menu - Ajouter des articles</h3>
                <div className="grid gap-3">
                  {menu.map(item => (
                    <div key={item.id} className="border rounded p-3 hover:shadow-md transition-shadow">
                      <div className="flex justify-between items-start">
                        <div>
                          <h4 className="font-medium">{item.name}</h4>
                          <p className="text-sm text-gray-600">{item.description}</p>
                          <p className="text-lg font-bold text-blue-600">{item.price.toFixed(2)} TND</p>
                        </div>
                        <button
                          onClick={() => addToOrder(item)}
                          className="bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 text-sm"
                        >
                          Ajouter
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Current Order */}
              <div>
                <h3 className="text-lg font-semibold mb-4">Commande modifiée</h3>
                <div className="border rounded p-4 min-h-[300px]">
                  {currentOrder.length === 0 ? (
                    <p className="text-gray-500">La commande ne peut pas être vide</p>
                  ) : (
                    <div className="space-y-3">
                      {currentOrder.map(item => (
                        <div key={item.menu_item_id} className="flex justify-between items-center border-b pb-2">
                          <div>
                            <h4 className="font-medium">{item.menu_item_name}</h4>
                            <p className="text-sm text-gray-600">{item.price.toFixed(2)} TND chacun</p>
                          </div>
                          <div className="flex items-center gap-2">
                            <button
                              onClick={() => updateQuantity(item.menu_item_id, item.quantity - 1)}
                              className="bg-gray-200 w-8 h-8 rounded-full hover:bg-gray-300"
                            >
                              -
                            </button>
                            <span className="w-8 text-center">{item.quantity}</span>
                            <button
                              onClick={() => updateQuantity(item.menu_item_id, item.quantity + 1)}
                              className="bg-gray-200 w-8 h-8 rounded-full hover:bg-gray-300"
                            >
                              +
                            </button>
                            <button
                              onClick={() => removeFromOrder(item.menu_item_id)}
                              className="bg-red-500 text-white w-8 h-8 rounded-full hover:bg-red-600 ml-2"
                              title="Supprimer cet article"
                            >
                              ×
                            </button>
                          </div>
                        </div>
                      ))}
                      <div className="pt-3 border-t">
                        <div className="flex justify-between text-sm text-gray-600">
                          <span>Ancien total: {editingOrder.total_amount.toFixed(2)} TND</span>
                          <span className="text-lg font-bold text-blue-600">
                            Nouveau total: {getOrderTotal().toFixed(2)} TND
                          </span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
                
                <div className="mt-4 flex gap-3">
                  <button
                    onClick={updateExistingOrder}
                    disabled={currentOrder.length === 0}
                    className="flex-1 bg-orange-600 text-white py-2 px-4 rounded hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Confirmer les modifications
                  </button>
                  <button
                    onClick={cancelEdit}
                    className="bg-gray-500 text-white py-2 px-4 rounded hover:bg-gray-600"
                  >
                    Annuler
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer className="bg-gray-800 text-white p-4 text-center mt-8">
        <p>Marwen Ben Jemaa - All rights reserved by EdRina Resto.</p>
      </footer>
    </div>
  );
};

// Chef Dashboard
const ChefDashboard = () => {
  const [orders, setOrders] = useState([]);
  const { user, logout } = useAuth();

  useEffect(() => {
    fetchOrders();
    // Auto-refresh orders every 30 seconds
    const interval = setInterval(fetchOrders, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchOrders = async () => {
    try {
      const response = await axios.get(`${API}/orders`);
      setOrders(response.data);
    } catch (error) {
      console.error('Failed to fetch orders:', error);
    }
  };

  const markOrderReady = async (orderId) => {
    try {
      await axios.put(`${API}/orders/${orderId}`, {
        status: 'ready'
      });
      fetchOrders();
      alert('Commande marquée comme prête!');
    } catch (error) {
      console.error('Failed to mark order ready:', error);
      alert('Erreur lors de la mise à jour');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-blue-600 text-white p-4 flex justify-between items-center">
        <h1 className="text-xl font-bold">Cuisine - {user.username}</h1>
        <div className="flex gap-4">
          <button
            onClick={fetchOrders}
            className="bg-blue-700 px-4 py-2 rounded hover:bg-blue-800"
          >
            Actualiser
          </button>
          <button
            onClick={logout}
            className="bg-blue-700 px-4 py-2 rounded hover:bg-blue-800"
          >
            Déconnexion
          </button>
        </div>
      </div>

      <div className="p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">Commandes à préparer</h2>
        
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {orders.filter(order => order.status === 'in_kitchen').map(order => (
            <div key={order.id} className="bg-white rounded-lg shadow-md p-6 border-l-4 border-orange-500">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-xl font-bold text-orange-600">Table {order.table_number}</h3>
                  <p className="text-gray-600">Serveur: {order.server_name}</p>
                  <p className="text-sm text-gray-500">
                    Commande #{order.id.slice(-6)}
                  </p>
                </div>
                <span className="bg-orange-100 text-orange-800 px-3 py-1 rounded-full text-sm font-medium">
                  En préparation
                </span>
              </div>
              
              <div className="mb-4">
                <h4 className="font-semibold mb-2">Articles:</h4>
                <ul className="space-y-1">
                  {order.items.map(item => (
                    <li key={item.menu_item_id} className="flex justify-between">
                      <span>{item.menu_item_name}</span>
                      <span className="font-medium">x{item.quantity}</span>
                    </li>
                  ))}
                </ul>
              </div>
              
              <div className="flex justify-between items-center pt-4 border-t">
                <p className="text-sm text-gray-500">
                  Reçue: {new Date(order.created_at).toLocaleString('fr-FR')}
                </p>
                <button
                  onClick={() => markOrderReady(order.id)}
                  className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 font-medium"
                >
                  Marquer prête
                </button>
              </div>
            </div>
          ))}
        </div>

        {orders.filter(order => order.status === 'in_kitchen').length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">Aucune commande en attente</p>
          </div>
        )}

        {/* Ready Orders */}
        <div className="mt-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">Commandes prêtes</h2>
          
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {orders.filter(order => order.status === 'ready').map(order => (
              <div key={order.id} className="bg-white rounded-lg shadow-md p-6 border-l-4 border-green-500">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-xl font-bold text-green-600">Table {order.table_number}</h3>
                    <p className="text-gray-600">Serveur: {order.server_name}</p>
                  </div>
                  <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
                    Prête
                  </span>
                </div>
                
                <p className="text-sm text-gray-500">
                  Prête depuis: {order.kitchen_ready_at && new Date(order.kitchen_ready_at).toLocaleString('fr-FR')}
                </p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-800 text-white p-4 text-center mt-8">
        <p>Marwen Ben Jemaa - All rights reserved by EdRina Resto.</p>
      </footer>
    </div>
  );
};

// Cashier Dashboard
const CashierDashboard = () => {
  const [orders, setOrders] = useState([]);
  const { user, logout } = useAuth();

  useEffect(() => {
    fetchOrders();
    // Auto-refresh orders every 30 seconds
    const interval = setInterval(fetchOrders, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchOrders = async () => {
    try {
      const response = await axios.get(`${API}/orders`);
      setOrders(response.data);
    } catch (error) {
      console.error('Failed to fetch orders:', error);
    }
  };

  const markOrderPaid = async (orderId) => {
    try {
      await axios.put(`${API}/orders/${orderId}`, {
        status: 'paid'
      });
      fetchOrders();
      alert('Commande marquée comme payée!');
    } catch (error) {
      console.error('Failed to mark order paid:', error);
      alert('Erreur lors de la mise à jour');
    }
  };

  const getTotalRevenue = () => {
    return orders.filter(order => order.status === 'paid')
                 .reduce((total, order) => total + order.total_amount, 0);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-blue-600 text-white p-4 flex justify-between items-center">
        <h1 className="text-xl font-bold">Caisse - {user.username}</h1>
        <div className="flex gap-4">
          <div className="bg-blue-700 px-4 py-2 rounded">
            <span className="text-sm">Recettes: {getTotalRevenue().toFixed(2)} TND</span>
          </div>
          <button
            onClick={fetchOrders}
            className="bg-blue-700 px-4 py-2 rounded hover:bg-blue-800"
          >
            Actualiser
          </button>
          <button
            onClick={logout}
            className="bg-blue-700 px-4 py-2 rounded hover:bg-blue-800"
          >
            Déconnexion
          </button>
        </div>
      </div>

      <div className="p-6">
        {/* Ready to Pay Orders */}
        <h2 className="text-2xl font-bold text-gray-800 mb-6">Commandes prêtes à encaisser</h2>
        
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {orders.filter(order => order.status === 'ready').map(order => (
            <div key={order.id} className="bg-white rounded-lg shadow-md p-6 border-l-4 border-green-500">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-xl font-bold text-green-600">Table {order.table_number}</h3>
                  <p className="text-gray-600">Serveur: {order.server_name}</p>
                  <p className="text-sm text-gray-500">
                    Commande #{order.id.slice(-6)}
                  </p>
                </div>
                <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">
                  Prête
                </span>
              </div>
              
              <div className="mb-4">
                <h4 className="font-semibold mb-2">Articles:</h4>
                <ul className="space-y-1">
                  {order.items.map(item => (
                    <li key={item.menu_item_id} className="flex justify-between text-sm">
                      <span>{item.menu_item_name} x{item.quantity}</span>
                      <span>{(item.price * item.quantity).toFixed(2)} TND</span>
                    </li>
                  ))}
                </ul>
              </div>
              
              <div className="flex justify-between items-center pt-4 border-t">
                <p className="text-xl font-bold text-blue-600">
                  Total: {order.total_amount.toFixed(2)} TND
                </p>
                <button
                  onClick={() => markOrderPaid(order.id)}
                  className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 font-medium"
                >
                  Encaisser
                </button>
              </div>
              
              <p className="text-xs text-gray-500 mt-2">
                Prête depuis: {order.kitchen_ready_at && new Date(order.kitchen_ready_at).toLocaleString('fr-FR')}
              </p>
            </div>
          ))}
        </div>

        {orders.filter(order => order.status === 'ready').length === 0 && (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">Aucune commande prête à encaisser</p>
          </div>
        )}

        {/* Paid Orders History */}
        <div className="mt-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">Historique des paiements</h2>
          
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Table
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Serveur
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Montant
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Payée le
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {orders.filter(order => order.status === 'paid').map(order => (
                    <tr key={order.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="text-sm font-medium text-gray-900">Table {order.table_number}</div>
                        <div className="text-sm text-gray-500">#{order.id.slice(-6)}</div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {order.server_name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-green-600">
                        {order.total_amount.toFixed(2)} TND
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {order.paid_at && new Date(order.paid_at).toLocaleString('fr-FR')}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-800 text-white p-4 text-center mt-8">
        <p>Marwen Ben Jemaa - All rights reserved by EdRina Resto.</p>
      </footer>
    </div>
  );
};

// Admin Dashboard
const AdminDashboard = () => {
  const [activeTab, setActiveTab] = useState('orders');
  const [orders, setOrders] = useState([]);
  const [users, setUsers] = useState([]);
  const [menu, setMenu] = useState([]);
  const [showCreateUser, setShowCreateUser] = useState(false);
  const [showCreateMenuItem, setShowCreateMenuItem] = useState(false);
  const { user, logout } = useAuth();

  useEffect(() => {
    fetchOrders();
    fetchUsers();
    fetchMenu();
  }, []);

  const fetchOrders = async () => {
    try {
      const response = await axios.get(`${API}/orders`);
      setOrders(response.data);
    } catch (error) {
      console.error('Failed to fetch orders:', error);
    }
  };

  const fetchUsers = async () => {
    try {
      const response = await axios.get(`${API}/users`);
      setUsers(response.data);
    } catch (error) {
      console.error('Failed to fetch users:', error);
    }
  };

  const fetchMenu = async () => {
    try {
      const response = await axios.get(`${API}/menu`);
      setMenu(response.data);
    } catch (error) {
      console.error('Failed to fetch menu:', error);
    }
  };

  const deleteUser = async (userId) => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer cet utilisateur?')) {
      try {
        await axios.delete(`${API}/users/${userId}`);
        fetchUsers();
        alert('Utilisateur supprimé avec succès!');
      } catch (error) {
        console.error('Failed to delete user:', error);
        alert('Erreur lors de la suppression');
      }
    }
  };

  const deleteMenuItem = async (itemId) => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer cet article du menu?')) {
      try {
        await axios.delete(`${API}/menu/${itemId}`);
        fetchMenu();
        alert('Article supprimé avec succès!');
      } catch (error) {
        console.error('Failed to delete menu item:', error);
        alert('Erreur lors de la suppression');
      }
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-blue-600 text-white p-4 flex justify-between items-center">
        <h1 className="text-xl font-bold">Administration - {user.username}</h1>
        <button
          onClick={logout}
          className="bg-blue-700 px-4 py-2 rounded hover:bg-blue-800"
        >
          Déconnexion
        </button>
      </div>

      {/* Tabs */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4">
          <nav className="flex space-x-8">
            {[
              { id: 'orders', label: 'Commandes' },
              { id: 'users', label: 'Utilisateurs' },
              { id: 'menu', label: 'Menu' },
              { id: 'stats', label: 'Statistiques' }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>
      </div>

      <div className="p-6">
        {/* Orders Tab */}
        {activeTab === 'orders' && (
          <div>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-bold text-gray-800">Toutes les commandes</h2>
              <button
                onClick={fetchOrders}
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
              >
                Actualiser
              </button>
            </div>
            
            <div className="bg-white rounded-lg shadow-md overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Commande
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Table
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Serveur
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Montant
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Date
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {orders.map(order => (
                      <tr key={order.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-medium text-gray-900">#{order.id.slice(-6)}</div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          Table {order.table_number}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {order.server_name}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                            order.status === 'in_kitchen' ? 'bg-orange-100 text-orange-800' :
                            order.status === 'ready' ? 'bg-green-100 text-green-800' :
                            order.status === 'paid' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'
                          }`}>
                            {order.status === 'in_kitchen' ? 'En cuisine' :
                             order.status === 'ready' ? 'Prête' :
                             order.status === 'paid' ? 'Payée' : order.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-green-600">
                          {order.total_amount.toFixed(2)} TND
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {new Date(order.created_at).toLocaleString('fr-FR')}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Users Tab */}
        {activeTab === 'users' && <UserManagement users={users} fetchUsers={fetchUsers} deleteUser={deleteUser} />}
        
        {/* Menu Tab */}
        {activeTab === 'menu' && <MenuManagement menu={menu} fetchMenu={fetchMenu} deleteMenuItem={deleteMenuItem} />}
        
        {/* Stats Tab */}
        {activeTab === 'stats' && <Statistics orders={orders} />}
      </div>

      {/* Footer */}
      <footer className="bg-gray-800 text-white p-4 text-center mt-8">
        <p>Marwen Ben Jemaa - All rights reserved by EdRina Resto.</p>
      </footer>
    </div>
  );
};

// User Management Component
const UserManagement = ({ users, fetchUsers, deleteUser }) => {
  const [showCreateUser, setShowCreateUser] = useState(false);
  const [newUser, setNewUser] = useState({ username: '', password: '', role: 'serveur' });

  const createUser = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/auth/register`, newUser);
      setNewUser({ username: '', password: '', role: 'serveur' });
      setShowCreateUser(false);
      fetchUsers();
      alert('Utilisateur créé avec succès!');
    } catch (error) {
      console.error('Failed to create user:', error);
      alert('Erreur lors de la création de l\'utilisateur');
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Gestion des utilisateurs</h2>
        <button
          onClick={() => setShowCreateUser(true)}
          className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
        >
          Nouvel utilisateur
        </button>
      </div>
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {users.map(user => (
          <div key={user.id} className="bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h3 className="text-lg font-semibold">{user.username}</h3>
                <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                  user.role === 'admin' ? 'bg-red-100 text-red-800' :
                  user.role === 'chef' ? 'bg-yellow-100 text-yellow-800' :
                  user.role === 'caisse' ? 'bg-blue-100 text-blue-800' :
                  'bg-green-100 text-green-800'
                }`}>
                  {user.role.charAt(0).toUpperCase() + user.role.slice(1)}
                </span>
              </div>
              <button
                onClick={() => deleteUser(user.id)}
                className="text-red-600 hover:text-red-800"
              >
                Supprimer
              </button>
            </div>
            <p className="text-sm text-gray-500">
              Créé: {new Date(user.created_at).toLocaleString('fr-FR')}
            </p>
          </div>
        ))}
      </div>

      {/* Create User Modal */}
      {showCreateUser && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">Créer un nouvel utilisateur</h3>
            <form onSubmit={createUser} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Nom d'utilisateur</label>
                <input
                  type="text"
                  value={newUser.username}
                  onChange={(e) => setNewUser({...newUser, username: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Mot de passe</label>
                <input
                  type="password"
                  value={newUser.password}
                  onChange={(e) => setNewUser({...newUser, password: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Rôle</label>
                <select
                  value={newUser.role}
                  onChange={(e) => setNewUser({...newUser, role: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                >
                  <option value="serveur">Serveur</option>
                  <option value="chef">Chef</option>
                  <option value="caisse">Caisse</option>
                  <option value="admin">Admin</option>
                </select>
              </div>
              <div className="flex gap-3">
                <button
                  type="submit"
                  className="flex-1 bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700"
                >
                  Créer
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreateUser(false)}
                  className="bg-gray-500 text-white py-2 px-4 rounded hover:bg-gray-600"
                >
                  Annuler
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

// Menu Management Component
const MenuManagement = ({ menu, fetchMenu, deleteMenuItem }) => {
  const [showCreateMenuItem, setShowCreateMenuItem] = useState(false);
  const [newMenuItem, setNewMenuItem] = useState({ name: '', description: '', price: 0 });

  const createMenuItem = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API}/menu`, newMenuItem);
      setNewMenuItem({ name: '', description: '', price: 0 });
      setShowCreateMenuItem(false);
      fetchMenu();
      alert('Article ajouté avec succès!');
    } catch (error) {
      console.error('Failed to create menu item:', error);
      alert('Erreur lors de la création de l\'article');
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-800">Gestion du menu</h2>
        <button
          onClick={() => setShowCreateMenuItem(true)}
          className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
        >
          Nouvel article
        </button>
      </div>
      
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {menu.map(item => (
          <div key={item.id} className="bg-white rounded-lg shadow-md p-6">
            <div className="flex justify-between items-start mb-4">
              <div className="flex-1">
                <h3 className="text-lg font-semibold">{item.name}</h3>
                <p className="text-gray-600 text-sm">{item.description}</p>
                <p className="text-xl font-bold text-blue-600 mt-2">{item.price.toFixed(2)} TND</p>
              </div>
              <button
                onClick={() => deleteMenuItem(item.id)}
                className="text-red-600 hover:text-red-800 ml-2"
              >
                Supprimer
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Create Menu Item Modal */}
      {showCreateMenuItem && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">Ajouter un nouvel article</h3>
            <form onSubmit={createMenuItem} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Nom</label>
                <input
                  type="text"
                  value={newMenuItem.name}
                  onChange={(e) => setNewMenuItem({...newMenuItem, name: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Description</label>
                <textarea
                  value={newMenuItem.description}
                  onChange={(e) => setNewMenuItem({...newMenuItem, description: e.target.value})}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 h-20"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">Prix (TND)</label>
                <input
                  type="number"
                  step="0.01"
                  value={newMenuItem.price}
                  onChange={(e) => setNewMenuItem({...newMenuItem, price: parseFloat(e.target.value)})}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div className="flex gap-3">
                <button
                  type="submit"
                  className="flex-1 bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700"
                >
                  Ajouter
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreateMenuItem(false)}
                  className="bg-gray-500 text-white py-2 px-4 rounded hover:bg-gray-600"
                >
                  Annuler
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

// Statistics Component
const Statistics = ({ orders }) => {
  const getTotalRevenue = () => {
    return orders.filter(order => order.status === 'paid')
                 .reduce((total, order) => total + order.total_amount, 0);
  };

  const getOrdersByStatus = () => {
    const counts = {};
    orders.forEach(order => {
      counts[order.status] = (counts[order.status] || 0) + 1;
    });
    return counts;
  };

  const getRevenueByDay = () => {
    const revenueByDay = {};
    orders.filter(order => order.status === 'paid').forEach(order => {
      const date = new Date(order.paid_at).toLocaleDateString('fr-FR');
      revenueByDay[date] = (revenueByDay[date] || 0) + order.total_amount;
    });
    return revenueByDay;
  };

  const orderCounts = getOrdersByStatus();
  const dailyRevenue = getRevenueByDay();

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-800 mb-6">Statistiques</h2>
      
      {/* Summary Cards */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 mb-8">
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-green-100 text-green-600">
              💰
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Recettes totales</p>
              <p className="text-2xl font-bold text-green-600">{getTotalRevenue().toFixed(2)} TND</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-blue-100 text-blue-600">
              📊
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total commandes</p>
              <p className="text-2xl font-bold text-blue-600">{orders.length}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-orange-100 text-orange-600">
              🍳
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">En cuisine</p>
              <p className="text-2xl font-bold text-orange-600">{orderCounts.in_kitchen || 0}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-md p-6">
          <div className="flex items-center">
            <div className="p-3 rounded-full bg-green-100 text-green-600">
              ✅
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Commandes prêtes</p>
              <p className="text-2xl font-bold text-green-600">{orderCounts.ready || 0}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Daily Revenue */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-lg font-semibold mb-4">Recettes par jour</h3>
        <div className="space-y-3">
          {Object.entries(dailyRevenue).map(([date, revenue]) => (
            <div key={date} className="flex justify-between items-center p-3 bg-gray-50 rounded">
              <span className="font-medium">{date}</span>
              <span className="text-green-600 font-bold">{revenue.toFixed(2)} TND</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Main App Component
function App() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-blue-600 flex items-center justify-center">
        <div className="bg-white p-8 rounded-xl shadow-2xl">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Chargement...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!user) {
    return <LoginPage />;
  }

  // Render role-specific dashboard
  switch (user.role) {
    case 'serveur':
      return <ServerDashboard />;
    case 'chef':
      return <ChefDashboard />;
    case 'caisse':
      return <CashierDashboard />;
    case 'admin':
      return <AdminDashboard />;
    default:
      return <LoginPage />;
  }
}

// Wrap App with AuthProvider
export default function AppWithAuth() {
  return (
    <AuthProvider>
      <App />
    </AuthProvider>
  );
}