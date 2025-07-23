import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [currentView, setCurrentView] = useState('home');
  const [menuItems, setMenuItems] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [cart, setCart] = useState([]);
  const [showCart, setShowCart] = useState(false);
  const [customerInfo, setCustomerInfo] = useState({
    name: '',
    phone: '',
    email: '',
    notes: ''
  });
  const [paymentMethod, setPaymentMethod] = useState('cash');
  const [isLoading, setIsLoading] = useState(false);
  const [adminPassword, setAdminPassword] = useState('');
  const [isAdminAuthenticated, setIsAdminAuthenticated] = useState(false);
  const [adminOrders, setAdminOrders] = useState([]);
  const [adminMenu, setAdminMenu] = useState([]);

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  useEffect(() => {
    fetchMenuData();
  }, []);

  const fetchMenuData = async () => {
    try {
      const [menuResponse, categoriesResponse] = await Promise.all([
        fetch(`${BACKEND_URL}/api/menu`),
        fetch(`${BACKEND_URL}/api/menu/categories`)
      ]);
      
      const menuData = await menuResponse.json();
      const categoriesData = await categoriesResponse.json();
      
      // Set all menu items initially
      setMenuItems(menuData.menu_items || []);
      setCategories(categoriesData.categories || []);
      
      // Set first category as selected and show its items
      if (categoriesData.categories.length > 0) {
        const firstCategory = categoriesData.categories[0];
        setSelectedCategory(firstCategory);
        fetchCategoryMenu(firstCategory);
      }
    } catch (error) {
      console.error('Error fetching menu data:', error);
    }
  };

  const fetchCategoryMenu = async (category) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/menu/category/${encodeURIComponent(category)}`);
      const data = await response.json();
      setMenuItems(data.menu_items || []);
      setSelectedCategory(category);
    } catch (error) {
      console.error('Error fetching category menu:', error);
    }
  };

  const addToCart = (item) => {
    const existingItem = cart.find(cartItem => cartItem.menu_item_id === item.id);
    if (existingItem) {
      setCart(cart.map(cartItem =>
        cartItem.menu_item_id === item.id
          ? { ...cartItem, quantity: cartItem.quantity + 1 }
          : cartItem
      ));
    } else {
      setCart([...cart, {
        menu_item_id: item.id,
        name: item.name,
        price: item.price,
        quantity: 1
      }]);
    }
  };

  const updateCartQuantity = (menuItemId, newQuantity) => {
    if (newQuantity === 0) {
      setCart(cart.filter(item => item.menu_item_id !== menuItemId));
    } else {
      setCart(cart.map(item =>
        item.menu_item_id === menuItemId
          ? { ...item, quantity: newQuantity }
          : item
      ));
    }
  };

  const getTotalAmount = () => {
    return cart.reduce((total, item) => total + (item.price * item.quantity), 0).toFixed(2);
  };

  const placeOrder = async () => {
    if (!customerInfo.name || !customerInfo.phone || cart.length === 0) {
      alert('Please fill in your details and add items to cart');
      return;
    }

    setIsLoading(true);
    try {
      const orderData = {
        customer_name: customerInfo.name,
        customer_phone: customerInfo.phone,
        customer_email: customerInfo.email,
        items: cart,
        payment_method: paymentMethod,
        notes: customerInfo.notes
      };

      const response = await fetch(`${BACKEND_URL}/api/orders`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(orderData)
      });

      if (response.ok) {
        const result = await response.json();
        alert(`Order placed successfully! Order ID: ${result.order_id}`);
        
        // Handle payment redirection for Revolut
        if (paymentMethod === 'revolut') {
          window.open('https://revolut.me/kishor571t', '_blank');
        }
        
        // Reset form
        setCart([]);
        setCustomerInfo({ name: '', phone: '', email: '', notes: '' });
        setShowCart(false);
        setCurrentView('home');
      } else {
        throw new Error('Failed to place order');
      }
    } catch (error) {
      console.error('Error placing order:', error);
      alert('Failed to place order. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const adminLogin = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/admin/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ password: adminPassword })
      });

      if (response.ok) {
        setIsAdminAuthenticated(true);
        setCurrentView('admin-dashboard');
        fetchAdminData();
      } else {
        alert('Invalid password');
      }
    } catch (error) {
      console.error('Error logging in:', error);
      alert('Login failed');
    }
  };

  const fetchAdminData = async () => {
    try {
      const [ordersResponse, menuResponse] = await Promise.all([
        fetch(`${BACKEND_URL}/api/admin/orders`),
        fetch(`${BACKEND_URL}/api/admin/menu`)
      ]);
      
      const ordersData = await ordersResponse.json();
      const menuData = await menuResponse.json();
      
      setAdminOrders(ordersData.orders || []);
      setAdminMenu(menuData.menu_items || []);
    } catch (error) {
      console.error('Error fetching admin data:', error);
    }
  };

  const updateMenuItemAvailability = async (itemId, available) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/admin/menu/${itemId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ available })
      });

      if (response.ok) {
        fetchAdminData();
      }
    } catch (error) {
      console.error('Error updating menu item:', error);
    }
  };

  const updateMenuItemPrice = async (itemId, price) => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/admin/menu/${itemId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ price: parseFloat(price) })
      });

      if (response.ok) {
        fetchAdminData();
      }
    } catch (error) {
      console.error('Error updating menu item price:', error);
    }
  };

  // Handle admin access via URL
  useEffect(() => {
    if (window.location.pathname === '/admin') {
      setCurrentView('admin');
    }
  }, []);

  // Render Home View
  const renderHome = () => (
    <div className="home-container">
      {/* Hero Section */}
      <div className="hero-section">
        <div className="hero-content">
          <div className="hero-text">
            <h1 className="hero-title">
              <span className="brand-name">Kansha's Indian Treat</span>
              <span className="brand-tagline">Kansha – Taste the Soul of South India</span>
            </h1>
            <p className="hero-description">
              Experience the rich taste of South Indian cuisine with our traditional recipes and fresh ingredients. From crispy dosas to aromatic biryanis, every dish tells a story of Chennai's culinary heritage.
            </p>
            <div className="hero-buttons">
              <button className="cta-button primary" onClick={() => setCurrentView('menu')}>
                Order Now
              </button>
            </div>
            <div className="contact-info">
              <span className="phone">📞 +353 892760135</span>
            </div>
          </div>
          <div className="hero-image">
            <img src="https://images.unsplash.com/photo-1701579231305-d84d8af9a3fd?crop=entropy&cs=srgb&fm=jpg&ixid=M3w3NTY2Nzd8MHwxfHNlYXJjaHwxfHxiaXJ5YW5pfGVufDB8fHx8MTc1MzI2MDMxN3ww&ixlib=rb-4.1.0&q=85" alt="Delicious Biryani" />
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="features-section">
        <div className="container">
          <h2 className="section-title">Why Choose Kansha's?</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">🍛</div>
              <h3>Authentic Recipes</h3>
              <p>Traditional South Indian recipes passed down through generations</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🌿</div>
              <h3>Fresh Ingredients</h3>
              <p>Daily fresh ingredients sourced from trusted local suppliers</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">🚚</div>
              <h3>Daily Service</h3>
              <p>Fresh meals prepared daily with customizable availability</p>
            </div>
          </div>
        </div>
      </div>

      {/* Popular Items Preview */}
      <div className="popular-section">
        <div className="container">
          <h2 className="section-title">Popular Dishes</h2>
          <div className="popular-grid">
            <div className="popular-item">
              <img src="https://images.unsplash.com/photo-1668236543090-82eba5ee5976" alt="Dosa" />
              <h4>Masala Dosa</h4>
              <p>Crispy rice crepe with spiced potato filling</p>
            </div>
            <div className="popular-item">
              <img src="https://images.unsplash.com/photo-1701579231349-d7459c40919d" alt="Biryani" />
              <h4>Chicken Biryani</h4>
              <p>Aromatic basmati rice with tender chicken pieces</p>
            </div>
            <div className="popular-item">
              <img src="https://images.unsplash.com/photo-1589301760014-d929f3979dbc" alt="Idli" />
              <h4>Idli with Sambar</h4>
              <p>Steamed rice cakes served with lentil curry</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  // Render Menu View
  const renderMenu = () => (
    <div className="menu-container">
      <div className="menu-header">
        <h2>Our Menu</h2>
        <button className="cart-toggle" onClick={() => setShowCart(!showCart)}>
          🛒 Cart ({cart.length})
        </button>
      </div>
      
      <div className="categories-nav">
        {categories.map(category => (
          <button
            key={category}
            className={`category-btn ${selectedCategory === category ? 'active' : ''}`}
            onClick={() => fetchCategoryMenu(category)}
          >
            {category}
          </button>
        ))}
      </div>

      <div className="menu-content">
        <div className="menu-items">
          {menuItems.map(item => (
            <div key={item.id} className="menu-item-card">
              {item.image_url && (
                <img src={item.image_url} alt={item.name} className="menu-item-image" />
              )}
              <div className="menu-item-content">
                <h3>{item.name}</h3>
                {item.subcategory && <span className="subcategory">{item.subcategory}</span>}
                <div className="price">€{item.price.toFixed(2)}</div>
                <button className="add-to-cart-btn" onClick={() => addToCart(item)}>
                  Add to Cart
                </button>
              </div>
            </div>
          ))}
        </div>

        {showCart && (
          <div className="cart-sidebar">
            <div className="cart-header">
              <h3>Your Order</h3>
              <button onClick={() => setShowCart(false)}>×</button>
            </div>
            
            <div className="cart-items">
              {cart.map(item => (
                <div key={item.menu_item_id} className="cart-item">
                  <div className="cart-item-info">
                    <span className="item-name">{item.name}</span>
                    <span className="item-price">€{item.price.toFixed(2)}</span>
                  </div>
                  <div className="quantity-controls">
                    <button onClick={() => updateCartQuantity(item.menu_item_id, item.quantity - 1)}>-</button>
                    <span>{item.quantity}</span>
                    <button onClick={() => updateCartQuantity(item.menu_item_id, item.quantity + 1)}>+</button>
                  </div>
                </div>
              ))}
            </div>

            {cart.length > 0 && (
              <div className="cart-footer">
                <div className="total">Total: €{getTotalAmount()}</div>
                <button className="checkout-btn" onClick={() => setCurrentView('checkout')}>
                  Checkout
                </button>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );

  // Render Checkout View
  const renderCheckout = () => (
    <div className="checkout-container">
      <h2>Checkout</h2>
      
      <div className="checkout-content">
        <div className="customer-info">
          <h3>Customer Information</h3>
          <input
            type="text"
            placeholder="Full Name *"
            value={customerInfo.name}
            onChange={(e) => setCustomerInfo({...customerInfo, name: e.target.value})}
          />
          <input
            type="tel"
            placeholder="Phone Number *"
            value={customerInfo.phone}
            onChange={(e) => setCustomerInfo({...customerInfo, phone: e.target.value})}
          />
          <input
            type="email"
            placeholder="Email (Optional)"
            value={customerInfo.email}
            onChange={(e) => setCustomerInfo({...customerInfo, email: e.target.value})}
          />
          <textarea
            placeholder="Special Instructions (Optional)"
            value={customerInfo.notes}
            onChange={(e) => setCustomerInfo({...customerInfo, notes: e.target.value})}
          />
        </div>

        <div className="payment-methods">
          <h3>Payment Method</h3>
          <label className="payment-option">
            <input
              type="radio"
              value="cash"
              checked={paymentMethod === 'cash'}
              onChange={(e) => setPaymentMethod(e.target.value)}
            />
            Cash on Delivery
          </label>
          <label className="payment-option">
            <input
              type="radio"
              value="revolut"
              checked={paymentMethod === 'revolut'}
              onChange={(e) => setPaymentMethod(e.target.value)}
            />
            Revolut Payment
          </label>
          <label className="payment-option">
            <input
              type="radio"
              value="revolut-person"
              checked={paymentMethod === 'revolut-person'}
              onChange={(e) => setPaymentMethod(e.target.value)}
            />
            Pay by Revolut in Person
          </label>
        </div>

        <div className="order-summary">
          <h3>Order Summary</h3>
          {cart.map(item => (
            <div key={item.menu_item_id} className="summary-item">
              <span>{item.name} x{item.quantity}</span>
              <span>€{(item.price * item.quantity).toFixed(2)}</span>
            </div>
          ))}
          <div className="summary-total">
            <strong>Total: €{getTotalAmount()}</strong>
          </div>
        </div>

        <div className="checkout-actions">
          <button className="back-btn" onClick={() => setCurrentView('menu')}>
            Back to Menu
          </button>
          <button 
            className="place-order-btn" 
            onClick={placeOrder}
            disabled={isLoading}
          >
            {isLoading ? 'Placing Order...' : 'Place Order'}
          </button>
        </div>
      </div>
    </div>
  );

  // Render Admin Login
  const renderAdminLogin = () => (
    <div className="admin-login">
      <div className="login-form">
        <h2>Admin Login</h2>
        <input
          type="password"
          placeholder="Admin Password"
          value={adminPassword}
          onChange={(e) => setAdminPassword(e.target.value)}
        />
        <button onClick={adminLogin}>Login</button>
        <button className="back-btn" onClick={() => setCurrentView('home')}>
          Back to Home
        </button>
      </div>
    </div>
  );

  // Render Admin Dashboard
  const renderAdminDashboard = () => (
    <div className="admin-dashboard">
      <div className="admin-header">
        <h2>Admin Dashboard</h2>
        <button onClick={() => { setIsAdminAuthenticated(false); setCurrentView('home'); }}>
          Logout
        </button>
      </div>

      <div className="admin-tabs">
        <button className="tab-btn active">Orders</button>
        <button className="tab-btn">Menu Management</button>
      </div>

      <div className="admin-content">
        <div className="orders-section">
          <h3>Recent Orders</h3>
          <div className="orders-list">
            {adminOrders.map(order => (
              <div key={order.id} className="order-card">
                <div className="order-header">
                  <span className="order-id">Order #{order.id.slice(-8)}</span>
                  <span className="order-date">{new Date(order.order_date).toLocaleDateString()}</span>
                  <span className={`order-status ${order.status}`}>{order.status}</span>
                </div>
                <div className="order-details">
                  <p><strong>Customer:</strong> {order.customer_name}</p>
                  <p><strong>Phone:</strong> {order.customer_phone}</p>
                  <p><strong>Payment:</strong> {order.payment_method}</p>
                  <p><strong>Total:</strong> €{order.total_amount.toFixed(2)}</p>
                  <div className="order-items">
                    <strong>Items:</strong>
                    {order.items.map((item, index) => (
                      <span key={index}> {item.name} x{item.quantity}</span>
                    ))}
                  </div>
                  {order.notes && <p><strong>Notes:</strong> {order.notes}</p>}
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="menu-management">
          <h3>Menu Management</h3>
          <div className="menu-admin-list">
            {adminMenu.map(item => (
              <div key={item.id} className="menu-admin-item">
                <div className="item-info">
                  <h4>{item.name}</h4>
                  <span className="category">{item.category}</span>
                </div>
                <div className="item-controls">
                  <input
                    type="number"
                    step="0.50"
                    value={item.price}
                    onChange={(e) => updateMenuItemPrice(item.id, e.target.value)}
                    className="price-input"
                  />
                  <label className="availability-toggle">
                    <input
                      type="checkbox"
                      checked={item.available}
                      onChange={(e) => updateMenuItemAvailability(item.id, e.target.checked)}
                    />
                    Available
                  </label>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );

  // Main render
  return (
    <div className="App">
      <nav className="navbar">
        <div className="nav-content">
          <div className="logo" onClick={() => setCurrentView('home')}>
            <span className="logo-text">Kansha's Indian Treat</span>
            <span className="logo-tagline">Chennai Flavors</span>
          </div>
          <div className="nav-links">
            <button 
              className={currentView === 'home' ? 'nav-link active' : 'nav-link'}
              onClick={() => setCurrentView('home')}
            >
              Home
            </button>
            <button 
              className={currentView === 'menu' ? 'nav-link active' : 'nav-link'}
              onClick={() => setCurrentView('menu')}
            >
              Menu
            </button>
            {cart.length > 0 && (
              <button className="cart-indicator" onClick={() => { setCurrentView('menu'); setShowCart(true); }}>
                🛒 {cart.length}
              </button>
            )}
          </div>
        </div>
      </nav>

      <main className="main-content">
        {currentView === 'home' && renderHome()}
        {currentView === 'menu' && renderMenu()}
        {currentView === 'checkout' && renderCheckout()}
        {currentView === 'admin' && !isAdminAuthenticated && renderAdminLogin()}
        {currentView === 'admin-dashboard' && isAdminAuthenticated && renderAdminDashboard()}
      </main>

      <footer className="footer">
        <div className="footer-content">
          <div className="footer-info">
            <h3>Kansha's Indian Treat</h3>
            <p>Authentic South Indian Cuisine in Citywest</p>
            <p>📞 +353 892760135</p>
          </div>
          <div className="footer-hours">
            <h4>Operating Hours</h4>
            <p>Daily: 11:00 AM - 9:00 PM</p>
          </div>
        </div>
        <div className="footer-bottom">
          <p>&copy; 2024 Kansha's Indian Treat. Bringing Chennai to your table.</p>
        </div>
      </footer>
    </div>
  );
}

export default App;