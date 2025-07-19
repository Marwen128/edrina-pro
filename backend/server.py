from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
import jwt
import bcrypt

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

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
        
        user = await db.users.find_one({"id": user_id})
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return User(**user)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

# Authentication Routes
@api_router.post("/auth/register")
async def register_user(user_data: UserCreate, current_user: User = Depends(get_current_user)):
    # Only admin can register new users
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can register new users")
    
    # Check if username already exists
    existing_user = await db.users.find_one({"username": user_data.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    # Validate role
    if user_data.role not in ["serveur", "chef", "caisse", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    # Create new user
    user = User(
        username=user_data.username,
        password_hash=hash_password(user_data.password),
        role=user_data.role
    )
    
    await db.users.insert_one(user.dict())
    return {"message": "User created successfully", "user": UserResponse(**user.dict())}

@api_router.post("/auth/login")
async def login_user(user_data: UserLogin):
    user = await db.users.find_one({"username": user_data.username})
    if not user or not verify_password(user_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = create_access_token(data={"sub": user["id"], "role": user["role"]})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(**user)
    }

@api_router.get("/auth/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse(**current_user.dict())

# User Management Routes (Admin only)
@api_router.get("/users", response_model=List[UserResponse])
async def get_users(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    users = await db.users.find().to_list(1000)
    return [UserResponse(**user) for user in users]

@api_router.delete("/users/{user_id}")
async def delete_user(user_id: str, current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    result = await db.users.delete_one({"id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {"message": "User deleted successfully"}

# Menu Management Routes
@api_router.post("/menu", response_model=MenuItem)
async def create_menu_item(item: MenuItemCreate, current_user: User = Depends(get_current_user)):
    if current_user.role not in ["admin", "chef"]:
        raise HTTPException(status_code=403, detail="Admin or Chef access required")
    
    menu_item = MenuItem(**item.dict())
    await db.menu_items.insert_one(menu_item.dict())
    return menu_item

@api_router.get("/menu", response_model=List[MenuItem])
async def get_menu_items():
    menu_items = await db.menu_items.find().to_list(1000)
    return [MenuItem(**item) for item in menu_items]

@api_router.put("/menu/{item_id}")
async def update_menu_item(item_id: str, item: MenuItemCreate, current_user: User = Depends(get_current_user)):
    if current_user.role not in ["admin", "chef"]:
        raise HTTPException(status_code=403, detail="Admin or Chef access required")
    
    result = await db.menu_items.update_one(
        {"id": item_id}, 
        {"$set": item.dict()}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
    return {"message": "Menu item updated successfully"}

@api_router.delete("/menu/{item_id}")
async def delete_menu_item(item_id: str, current_user: User = Depends(get_current_user)):
    if current_user.role not in ["admin", "chef"]:
        raise HTTPException(status_code=403, detail="Admin or Chef access required")
    
    result = await db.menu_items.delete_one({"id": item_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Menu item not found")
    
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
    
    order = Order(
        table_number=order_data.table_number,
        server_id=current_user.id,
        server_name=current_user.username,
        items=order_data.items,
        total_amount=total_amount,
        status="in_kitchen"
    )
    
    await db.orders.insert_one(order.dict())
    return order

@api_router.get("/orders", response_model=List[Order])
async def get_orders(current_user: User = Depends(get_current_user)):
    if current_user.role == "serveur":
        # Servers can only see their own orders
        orders = await db.orders.find({"server_id": current_user.id}).to_list(1000)
    elif current_user.role == "chef":
        # Chefs see orders in kitchen and ready
        orders = await db.orders.find({"status": {"$in": ["in_kitchen", "ready"]}}).to_list(1000)
    elif current_user.role == "caisse":
        # Cashiers see ready and paid orders
        orders = await db.orders.find({"status": {"$in": ["ready", "paid"]}}).to_list(1000)
    elif current_user.role == "admin":
        # Admin sees all orders
        orders = await db.orders.find().to_list(1000)
    else:
        orders = []
    
    return [Order(**order) for order in orders]

@api_router.put("/orders/{order_id}")
async def update_order(order_id: str, order_update: OrderUpdate, current_user: User = Depends(get_current_user)):
    order = await db.orders.find_one({"id": order_id})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    update_data = {}
    
    if order_update.items is not None:
        # Only servers can modify items and only if status is in_kitchen
        if current_user.role != "serveur" or order["status"] not in ["in_kitchen"]:
            raise HTTPException(status_code=403, detail="Cannot modify order items")
        
        if order["server_id"] != current_user.id:
            raise HTTPException(status_code=403, detail="Can only modify your own orders")
        
        total_amount = sum(item.price * item.quantity for item in order_update.items)
        update_data["items"] = [item.dict() for item in order_update.items]
        update_data["total_amount"] = total_amount
        update_data["updated_at"] = datetime.utcnow()
    
    if order_update.status is not None:
        if order_update.status == "ready" and current_user.role == "chef":
            # Chef marking order as ready
            update_data["status"] = "ready"
            update_data["kitchen_ready_at"] = datetime.utcnow()
            update_data["updated_at"] = datetime.utcnow()
        elif order_update.status == "paid" and current_user.role == "caisse":
            # Cashier marking order as paid
            update_data["status"] = "paid"
            update_data["paid_at"] = datetime.utcnow()
            update_data["updated_at"] = datetime.utcnow()
        else:
            raise HTTPException(status_code=403, detail="Invalid status change")
    
    if update_data:
        await db.orders.update_one({"id": order_id}, {"$set": update_data})
    
    updated_order = await db.orders.find_one({"id": order_id})
    return Order(**updated_order)

@api_router.get("/orders/table/{table_number}")
async def get_table_orders(table_number: int, current_user: User = Depends(get_current_user)):
    if table_number < 1 or table_number > 8:
        raise HTTPException(status_code=400, detail="Table number must be between 1 and 8")
    
    orders = await db.orders.find({"table_number": table_number}).to_list(1000)
    return [Order(**order) for order in orders]

# Initialize default admin user
@api_router.post("/init")
async def initialize_system():
    # Check if admin already exists
    admin = await db.users.find_one({"role": "admin"})
    if admin:
        return {"message": "System already initialized"}
    
    # Create default admin user
    admin_user = User(
        username="admin",
        password_hash=hash_password("admin123"),
        role="admin"
    )
    
    await db.users.insert_one(admin_user.dict())
    
    # Create some sample menu items
    sample_menu = [
        {"name": "Couscous Traditionnel", "description": "Couscous avec légumes et viande", "price": 15.5},
        {"name": "Tajine Agneau", "description": "Tajine d'agneau aux pruneaux", "price": 18.0},
        {"name": "Brick à l'oeuf", "description": "Brick croustillante à l'oeuf", "price": 8.5},
        {"name": "Salade Mechouia", "description": "Salade grillée tunisienne", "price": 6.0},
        {"name": "Makloub", "description": "Pâtisserie traditionnelle", "price": 4.5}
    ]
    
    for item in sample_menu:
        menu_item = MenuItem(**item)
        await db.menu_items.insert_one(menu_item.dict())
    
    return {"message": "System initialized with admin user (admin/admin123) and sample menu"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()