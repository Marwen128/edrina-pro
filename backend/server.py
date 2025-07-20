# Backend EdRina Resto - Version complète avec stockage en mémoire
from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timedelta
import jwt
import bcrypt
import json
import os

# Variables globales pour simulation BDD
users_db: Dict[str, Dict] = {}
menu_items_db: Dict[str, Dict] = {}
orders_db: Dict[str, Dict] = {}

# Create the main app
app = FastAPI(title="EdRina Resto API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# JWT Settings
JWT_SECRET = "edrina_resto_secret_key_2024"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Security
security = HTTPBearer()

# Define Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    password_hash: str
    role: str  # serveur, chef, caisse, admin
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    username: str
    password: str
    role: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    role: str
    created_at: datetime

class MenuItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = ""
    price: float  # in Tunisian Dinars
    created_at: datetime = Field(default_factory=datetime.utcnow)

class MenuItemCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    price: float

class OrderItem(BaseModel):
    menu_item_id: str
    menu_item_name: str
    quantity: int
    price: float

class Order(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    table_number: int
    server_id: str
    server_name: str
    items: List[OrderItem]
    total_amount: float
    status: str  # "pending", "in_kitchen", "ready", "paid"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    kitchen_ready_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None

class OrderCreate(BaseModel):
    table_number: int
    items: List[OrderItem]

class OrderUpdate(BaseModel):
    items: Optional[List[OrderItem]] = None
    status: Optional[str] = None

# Helper Functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        if user_id not in users_db:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_data = users_db[user_id]
        return User(**user_data)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def init_default_data():
    """Initialize with default admin user and sample menu items"""
    global users_db, menu_items_db
    
    # Create default admin user
    admin_id = str(uuid.uuid4())
    admin_user = {
        "id": admin_id,
        "username": "admin",
        "password_hash": hash_password("admin123"),
        "role": "admin",
        "created_at": datetime.utcnow()
    }
    users_db[admin_id] = admin_user
    
    # Create sample menu items
    sample_items = [
        {"name": "Couscous Royal", "description": "Couscous avec viande et légumes", "price": 18.5},
        {"name": "Tajine Agneau", "description": "Tajine d'agneau aux pruneaux", "price": 22.0},
        {"name": "Brick à l'oeuf", "description": "Brick tunisienne à l'oeuf", "price": 8.0},
        {"name": "Salade Mechouia", "description": "Salade grillée tunisienne", "price": 12.0},
        {"name": "Makrouda", "description": "Pâtisserie traditionnelle", "price": 6.0},
        {"name": "Thé à la menthe", "description": "Thé traditionnel", "price": 4.0},
    ]
    
    for item_data in sample_items:
        item_id = str(uuid.uuid4())
        menu_item = {
            "id": item_id,
            "name": item_data["name"],
            "description": item_data["description"],
            "price": item_data["price"],
            "created_at": datetime.utcnow()
        }
        menu_items_db[item_id] = menu_item

# Authentication Routes
@api_router.post("/auth/register")
async def register_user(user_data: UserCreate, current_user: User = Depends(get_current_user)):
    # Only admin can register new users
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can register new users")
    
    # Check if username already exists
    for user in users_db.values():
        if user["username"] == user_data.username:
            raise HTTPException(status_code=400, detail="Username already exists")
    
    # Create new user
    user_id = str(uuid.uuid4())
    new_user = {
        "id": user_id,
        "username": user_data.username,
        "password_hash": hash_password(user_data.password),
        "role": user_data.role,
        "created_at": datetime.utcnow()
    }
    users_db[user_id] = new_user
    
    return UserResponse(**new_user)

@api_router.post("/auth/login")
async def login_user(login_data: UserLogin):
    # Find user by username
    user = None
    for user_data in users_db.values():
        if user_data["username"] == login_data.username:
            user = user_data
            break
    
    if not user or not verify_password(login_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user["id"]})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(**user)
    }

@api_router.get("/auth/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return UserResponse(**current_user.dict())

@api_router.post("/init")
async def initialize_system():
    """Initialize the system with default data"""
    init_default_data()
    return {"message": "System initialized successfully"}

# User Management Routes
@api_router.get("/users", response_model=List[UserResponse])
async def get_users(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return [UserResponse(**user) for user in users_db.values()]

@api_router.delete("/users/{user_id}")
async def delete_user(user_id: str, current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    del users_db[user_id]
    return {"message": "User deleted successfully"}

# Menu Management Routes
@api_router.post("/menu", response_model=MenuItem)
async def create_menu_item(item: MenuItemCreate, current_user: User = Depends(get_current_user)):
    if current_user.role not in ["admin", "chef"]:
        raise HTTPException(status_code=403, detail="Admin or Chef access required")
    
    item_id = str(uuid.uuid4())
    menu_item = {
        "id": item_id,
        "name": item.name,
        "description": item.description,
        "price": item.price,
        "created_at": datetime.utcnow()
    }
    menu_items_db[item_id] = menu_item
    return MenuItem(**menu_item)

@api_router.get("/menu", response_model=List[MenuItem])
async def get_menu_items():
    return [MenuItem(**item) for item in menu_items_db.values()]

@api_router.put("/menu/{item_id}")
async def update_menu_item(item_id: str, item: MenuItemCreate, current_user: User = Depends(get_current_user)):
    if current_user.role not in ["admin", "chef"]:
        raise HTTPException(status_code=403, detail="Admin or Chef access required")
    
    if item_id not in menu_items_db:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    menu_items_db[item_id].update({
        "name": item.name,
        "description": item.description,
        "price": item.price
    })
    
    return {"message": "Menu item updated successfully"}

@api_router.delete("/menu/{item_id}")
async def delete_menu_item(item_id: str, current_user: User = Depends(get_current_user)):
    if current_user.role not in ["admin", "chef"]:
        raise HTTPException(status_code=403, detail="Admin or Chef access required")
    
    if item_id not in menu_items_db:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    del menu_items_db[item_id]
    return {"message": "Menu item deleted successfully"}

# Order Management Routes
@api_router.post("/orders", response_model=Order)
async def create_order(order_data: OrderCreate, current_user: User = Depends(get_current_user)):
    if current_user.role != "serveur":
        raise HTTPException(status_code=403, detail="Only servers can create orders")
    
    # Validate table number (1-8)
    if order_data.table_number < 1 or order_data.table_number > 8:
        raise HTTPException(status_code=400, detail="Table number must be between 1 and 8")
    
    # Calculate total amount
    total_amount = sum(item.price * item.quantity for item in order_data.items)
    
    order_id = str(uuid.uuid4())
    order = {
        "id": order_id,
        "table_number": order_data.table_number,
        "server_id": current_user.id,
        "server_name": current_user.username,
        "items": [item.dict() for item in order_data.items],
        "total_amount": total_amount,
        "status": "in_kitchen",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "kitchen_ready_at": None,
        "paid_at": None
    }
    
    orders_db[order_id] = order
    return Order(**order)

@api_router.get("/orders", response_model=List[Order])
async def get_orders(current_user: User = Depends(get_current_user)):
    filtered_orders = []
    
    if current_user.role == "serveur":
        # Servers can only see their own orders
        filtered_orders = [order for order in orders_db.values() if order["server_id"] == current_user.id]
    elif current_user.role == "chef":
        # Chefs see orders in kitchen and ready
        filtered_orders = [order for order in orders_db.values() if order["status"] in ["in_kitchen", "ready"]]
    elif current_user.role == "caisse":
        # Cashiers see ready and paid orders
        filtered_orders = [order for order in orders_db.values() if order["status"] in ["ready", "paid"]]
    elif current_user.role == "admin":
        # Admin sees all orders
        filtered_orders = list(orders_db.values())
    
    return [Order(**order) for order in filtered_orders]

@api_router.put("/orders/{order_id}")
async def update_order(order_id: str, order_update: OrderUpdate, current_user: User = Depends(get_current_user)):
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order = orders_db[order_id]
    
    # Check permissions
    if current_user.role == "serveur" and order["server_id"] != current_user.id:
        raise HTTPException(status_code=403, detail="You can only modify your own orders")
    
    if current_user.role == "serveur" and order["status"] not in ["pending", "in_kitchen"]:
        raise HTTPException(status_code=403, detail="Cannot modify order that is already prepared")
    
    if order_update.items is not None and current_user.role in ["serveur", "admin"]:
        order["items"] = [item.dict() for item in order_update.items]
        order["total_amount"] = sum(item.price * item.quantity for item in order_update.items)
    
    if order_update.status is not None:
        if current_user.role == "chef" and order_update.status == "ready":
            order["status"] = "ready"
            order["kitchen_ready_at"] = datetime.utcnow()
        elif current_user.role == "caisse" and order_update.status == "paid":
            order["status"] = "paid" 
            order["paid_at"] = datetime.utcnow()
        elif current_user.role == "admin":
            order["status"] = order_update.status
    
    order["updated_at"] = datetime.utcnow()
    orders_db[order_id] = order
    
    return Order(**order)

@api_router.delete("/orders/{order_id}")
async def delete_order(order_id: str, current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can delete orders")
    
    if order_id not in orders_db:
        raise HTTPException(status_code=404, detail="Order not found")
    
    del orders_db[order_id]
    return {"message": "Order deleted successfully"}

# Statistics Routes
@api_router.get("/stats/daily")
async def get_daily_stats(current_user: User = Depends(get_current_user)):
    if current_user.role not in ["admin", "caisse"]:
        raise HTTPException(status_code=403, detail="Admin or Cashier access required")
    
    today = datetime.utcnow().date()
    daily_orders = [order for order in orders_db.values() 
                   if order["created_at"].date() == today]
    
    total_orders = len(daily_orders)
    total_revenue = sum(order["total_amount"] for order in daily_orders if order["status"] == "paid")
    paid_orders = len([order for order in daily_orders if order["status"] == "paid"])
    
    return {
        "date": today,
        "total_orders": total_orders,
        "paid_orders": paid_orders,
        "total_revenue": total_revenue
    }

# Export data
@api_router.get("/export/orders")
async def export_orders(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return {"orders": list(orders_db.values())}

# Include the router in the main app
app.include_router(api_router)

# Initialize data on startup
@app.on_event("startup")
async def startup_event():
    init_default_data()
    print("✅ EdRina Resto backend started successfully!")
    print("📊 Default admin user: admin / admin123")
    print("🍽️ Sample menu items loaded")

@app.get("/")
async def root():
    return {
        "message": "🍽️ EdRina Resto API",
        "version": "1.0.0",
        "status": "running",
        "features": [
            "✅ Authentication with roles (serveur, chef, caisse, admin)",
            "🍽️ Menu management",
            "📝 Order management with 8 fixed tables",
            "👥 User management (admin only)",
            "📊 Daily statistics",
            "🔐 JWT token security",
            "💰 Payments in Tunisian Dinars (TND)"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)