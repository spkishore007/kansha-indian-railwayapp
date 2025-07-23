from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import uuid
from contextlib import asynccontextmanager

# Database connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(MONGO_URL)
db = client.kansha_catering

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup - Insert initial menu data if collection is empty
    try:
        count = await db.menu_items.count_documents({})
        if count == 0:
            await insert_initial_menu_data()
            print("Initial menu data inserted successfully")
    except Exception as e:
        print(f"Error inserting initial data: {e}")
    
    yield
    
    # Shutdown
    client.close()

app = FastAPI(lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class MenuItem(BaseModel):
    id: str
    name: str
    category: str
    subcategory: Optional[str] = None
    price: float = 10.0
    description: Optional[str] = None
    image_url: Optional[str] = None
    available: bool = True
    available_days: List[str] = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

class CartItem(BaseModel):
    menu_item_id: str
    quantity: int
    name: str
    price: float

class Order(BaseModel):
    id: str
    customer_name: str
    customer_phone: str
    customer_email: Optional[str] = None
    items: List[CartItem]
    total_amount: float
    payment_method: str
    order_date: datetime
    status: str = "pending"
    notes: Optional[str] = None

class AdminSettings(BaseModel):
    email_notifications: bool = False
    whatsapp_notifications: bool = False
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None

# Admin password
ADMIN_PASSWORD = "kanshka123"

# Helper function to insert initial menu data with complete menu and proper images
async def insert_initial_menu_data():
    menu_data = [
        # Soups
        {"id": str(uuid.uuid4()), "name": "Vegetable Soup", "category": "Soups", "price": 8.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Creamy Mushroom Soup", "category": "Soups", "price": 9.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Chicken Soup", "category": "Soups", "price": 12.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Mutton Soup", "category": "Soups", "price": 14.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Aattu Kal (Goat Leg) Soup", "category": "Soups", "price": 16.0, "available": True},
        
        # Starters - Vegetarian
        {"id": str(uuid.uuid4()), "name": "Gobi 65", "category": "Starters - Vegetarian", "price": 10.0, "image_url": "https://images.unsplash.com/photo-1657196118354-f25f29fe636d", "available": True},
        {"id": str(uuid.uuid4()), "name": "Veg Seekh Kebab", "category": "Starters - Vegetarian", "subcategory": "Kebab", "price": 12.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Veg Seekh Kebab with Cheese", "category": "Starters - Vegetarian", "subcategory": "Kebab", "price": 14.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Gobi Manchurian", "category": "Starters - Vegetarian", "subcategory": "Manchurian", "price": 11.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Mushroom Manchurian", "category": "Starters - Vegetarian", "subcategory": "Manchurian", "price": 12.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Mix Veg Manchurian", "category": "Starters - Vegetarian", "subcategory": "Manchurian", "price": 11.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Masala Vada", "category": "Starters - Vegetarian", "subcategory": "Vadai", "price": 8.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Medhu Vada", "category": "Starters - Vegetarian", "subcategory": "Vadai", "price": 7.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Sambhar Medhu Vada", "category": "Starters - Vegetarian", "subcategory": "Vadai", "price": 9.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Dhahi Vada (Thayir Vada)", "category": "Starters - Vegetarian", "subcategory": "Vadai", "price": 9.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Potato Bonda", "category": "Starters - Vegetarian", "subcategory": "Bonda", "price": 6.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Spinach Bonda", "category": "Starters - Vegetarian", "subcategory": "Bonda", "price": 7.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Potato Bajji", "category": "Starters - Vegetarian", "subcategory": "Bajji", "price": 7.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Raw Banana Bajji", "category": "Starters - Vegetarian", "subcategory": "Bajji", "price": 7.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Ripped Banana Bajji", "category": "Starters - Vegetarian", "subcategory": "Bajji", "price": 8.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Vegetable Puff", "category": "Starters - Vegetarian", "subcategory": "Puffs", "price": 5.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Paneer Puff", "category": "Starters - Vegetarian", "subcategory": "Puffs", "price": 6.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Mushroom Puff", "category": "Starters - Vegetarian", "subcategory": "Puffs", "price": 6.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Paav Bhaji", "category": "Starters - Vegetarian", "subcategory": "Chat Items", "price": 12.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Masala Puri", "category": "Starters - Vegetarian", "subcategory": "Chat Items", "price": 8.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Pani Puri", "category": "Starters - Vegetarian", "subcategory": "Chat Items", "price": 8.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Dhahi Puri", "category": "Starters - Vegetarian", "subcategory": "Chat Items", "price": 9.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Road side Kalan (Mushroom Masala)", "category": "Starters - Vegetarian", "price": 12.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Road style Chickpea Sundal", "category": "Starters - Vegetarian", "price": 8.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Potato Lollipop", "category": "Starters - Vegetarian", "price": 9.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Potato Cheese Ball", "category": "Starters - Vegetarian", "price": 10.0, "available": True},
        
        # Starters - Non Vegetarian
        {"id": str(uuid.uuid4()), "name": "Egg Bonda", "category": "Starters - Non Vegetarian", "subcategory": "Egg", "price": 8.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Egg Puff", "category": "Starters - Non Vegetarian", "subcategory": "Egg", "price": 6.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Egg Masala (Burmese Atho Style)", "category": "Starters - Non Vegetarian", "subcategory": "Egg", "price": 12.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Chilli Cheese Omelette", "category": "Starters - Non Vegetarian", "subcategory": "Egg", "price": 10.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Mushroom Omelette", "category": "Starters - Non Vegetarian", "subcategory": "Egg", "price": 11.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Chicken Puff", "category": "Starters - Non Vegetarian", "subcategory": "Chicken", "price": 7.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Chicken 65", "category": "Starters - Non Vegetarian", "subcategory": "Chicken", "price": 14.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Kaju Chicken 65", "category": "Starters - Non Vegetarian", "subcategory": "Chicken", "price": 16.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Chicken Cheese Ball", "category": "Starters - Non Vegetarian", "subcategory": "Chicken", "price": 15.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Chicken Drumstick (spicy)", "category": "Starters - Non Vegetarian", "subcategory": "Chicken", "price": 16.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Chicken Chukka/Pepper Fry", "category": "Starters - Non Vegetarian", "subcategory": "Chicken", "price": 15.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Chicken Heart Pepper Fry", "category": "Starters - Non Vegetarian", "subcategory": "Chicken", "price": 14.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Mutton Puff", "category": "Starters - Non Vegetarian", "subcategory": "Mutton", "price": 8.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Mutton Seekh Kebab", "category": "Starters - Non Vegetarian", "subcategory": "Mutton", "price": 18.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Mutton Chukka/Pepper Fry", "category": "Starters - Non Vegetarian", "subcategory": "Mutton", "price": 18.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Mutton Brain Pepper Fry", "category": "Starters - Non Vegetarian", "subcategory": "Mutton", "price": 20.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Mutton Livery Fry", "category": "Starters - Non Vegetarian", "subcategory": "Mutton", "price": 18.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Seabass Fish Fry", "category": "Starters - Non Vegetarian", "subcategory": "Seafood", "price": 16.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Salmon Fish Fry", "category": "Starters - Non Vegetarian", "subcategory": "Seafood", "price": 18.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Prawn Fry", "category": "Starters - Non Vegetarian", "subcategory": "Seafood", "price": 16.0, "available": True},
        
        # Rice Varieties - Vegetarian
        {"id": str(uuid.uuid4()), "name": "Vegetable Biryani", "category": "Rice Varieties - Vegetarian", "subcategory": "Biryani", "price": 15.0, "image_url": "https://images.unsplash.com/photo-1701579231305-d84d8af9a3fd", "available": True},
        {"id": str(uuid.uuid4()), "name": "Paneer Biryani", "category": "Rice Varieties - Vegetarian", "subcategory": "Biryani", "price": 16.0, "image_url": "https://images.unsplash.com/photo-1701579231349-d7459c40919d", "available": True},
        {"id": str(uuid.uuid4()), "name": "Mushroom Biryani", "category": "Rice Varieties - Vegetarian", "subcategory": "Biryani", "price": 15.0, "image_url": "https://images.unsplash.com/photo-1589302168068-964664d93dc0", "available": True},
        {"id": str(uuid.uuid4()), "name": "Coconut Milk Rice (Thenga Paal Saadham)", "category": "Rice Varieties - Vegetarian", "subcategory": "Biryani", "price": 14.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Vegetable Pulav", "category": "Rice Varieties - Vegetarian", "subcategory": "Pulav", "price": 13.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Paneer Pulav", "category": "Rice Varieties - Vegetarian", "subcategory": "Pulav", "price": 14.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Tamarind Sevai", "category": "Rice Varieties - Vegetarian", "subcategory": "Sevai", "price": 10.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Sweet Coconut Sevai", "category": "Rice Varieties - Vegetarian", "subcategory": "Sevai", "price": 10.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Dhal Sevai", "category": "Rice Varieties - Vegetarian", "subcategory": "Sevai", "price": 10.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Tomato Rice", "category": "Rice Varieties - Vegetarian", "subcategory": "Mixed Rice", "price": 11.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Puliyotharai (Tamarind Rice)", "category": "Rice Varieties - Vegetarian", "subcategory": "Mixed Rice", "price": 10.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Lemon Rice", "category": "Rice Varieties - Vegetarian", "subcategory": "Mixed Rice", "price": 10.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Mango Rice", "category": "Rice Varieties - Vegetarian", "subcategory": "Mixed Rice", "price": 11.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Coconut Rice", "category": "Rice Varieties - Vegetarian", "subcategory": "Mixed Rice", "price": 10.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Sambhar Rice (Bisebellabath)", "category": "Rice Varieties - Vegetarian", "subcategory": "Mixed Rice", "price": 12.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Curd Rice", "category": "Rice Varieties - Vegetarian", "subcategory": "Mixed Rice", "price": 9.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Sakkarai Pongal / Jaggery Pongal", "category": "Rice Varieties - Vegetarian", "subcategory": "Mixed Rice", "price": 10.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Ven Pongal", "category": "Rice Varieties - Vegetarian", "subcategory": "Mixed Rice", "price": 10.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Basmati White Rice", "category": "Rice Varieties - Vegetarian", "subcategory": "White Rice", "price": 8.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Soona Moosori White Rice", "category": "Rice Varieties - Vegetarian", "subcategory": "White Rice", "price": 8.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Ponni Boiled Rice", "category": "Rice Varieties - Vegetarian", "subcategory": "White Rice", "price": 8.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Veg Fried Rice", "category": "Rice Varieties - Vegetarian", "price": 12.0, "available": True},
        
        # Rice Varieties - Non Vegetarian
        {"id": str(uuid.uuid4()), "name": "Egg Biryani", "category": "Rice Varieties - Non Vegetarian", "subcategory": "Biryani", "price": 14.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Chicken Biryani", "category": "Rice Varieties - Non Vegetarian", "subcategory": "Biryani", "price": 18.0, "image_url": "https://images.unsplash.com/photo-1701579231349-d7459c40919d", "available": True},
        {"id": str(uuid.uuid4()), "name": "Chicken 65 Biryani", "category": "Rice Varieties - Non Vegetarian", "subcategory": "Biryani", "price": 20.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Mutton Biryani", "category": "Rice Varieties - Non Vegetarian", "subcategory": "Biryani", "price": 22.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Prawn Biryani", "category": "Rice Varieties - Non Vegetarian", "subcategory": "Biryani", "price": 20.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Fish Biryani", "category": "Rice Varieties - Non Vegetarian", "subcategory": "Biryani", "price": 19.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Egg Fried Rice", "category": "Rice Varieties - Non Vegetarian", "subcategory": "Fried Rice", "price": 12.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Chicken Fried Rice", "category": "Rice Varieties - Non Vegetarian", "subcategory": "Fried Rice", "price": 15.0, "available": True},
        
        # Sides/Fry/Poriyal
        {"id": str(uuid.uuid4()), "name": "Dhal Spinach (Keerai Kootu)", "category": "Sides/Fry/Poriyal", "price": 8.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Dhal Zucchini Tadka (Suraikkai Kootu)", "category": "Sides/Fry/Poriyal", "price": 8.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Dhal Mangout (Avaraka Kootu)", "category": "Sides/Fry/Poriyal", "price": 9.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Poriyal/Aviyal (Mixed Vegetables)", "category": "Sides/Fry/Poriyal", "price": 8.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Potato Fry", "category": "Sides/Fry/Poriyal", "price": 7.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Ladies Finger Fry", "category": "Sides/Fry/Poriyal", "price": 8.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Soya Chunks Fry (Meal Maker)", "category": "Sides/Fry/Poriyal", "price": 9.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "White Channa Sundal", "category": "Sides/Fry/Poriyal", "subcategory": "Channa Sundal", "price": 7.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Black Channa Sundal", "category": "Sides/Fry/Poriyal", "subcategory": "Channa Sundal", "price": 7.0, "available": True},
        
        # Tiffen Varieties
        {"id": str(uuid.uuid4()), "name": "Idly (4 pieces)", "category": "Tiffen Varieties", "price": 8.0, "image_url": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc", "available": True},
        {"id": str(uuid.uuid4()), "name": "Chapati", "category": "Tiffen Varieties", "price": 6.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Vegetable Hakka Noodles", "category": "Tiffen Varieties", "subcategory": "Hakka Noodles", "price": 12.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Egg Hakka Noodles", "category": "Tiffen Varieties", "subcategory": "Hakka Noodles", "price": 14.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Plain Dosa", "category": "Tiffen Varieties", "subcategory": "Dosa", "price": 10.0, "image_url": "https://images.unsplash.com/photo-1668236543090-82eba5ee5976", "available": True},
        {"id": str(uuid.uuid4()), "name": "Podi Dosa", "category": "Tiffen Varieties", "subcategory": "Dosa", "price": 11.0, "image_url": "https://images.unsplash.com/photo-1694849789325-914b71ab4075", "available": True},
        {"id": str(uuid.uuid4()), "name": "Masala Dosa", "category": "Tiffen Varieties", "subcategory": "Dosa", "price": 12.0, "image_url": "https://images.unsplash.com/photo-1708146464361-5c5ce4f9abb6", "available": True},
        {"id": str(uuid.uuid4()), "name": "Ghee Dosa", "category": "Tiffen Varieties", "subcategory": "Dosa", "price": 12.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Kaaram Dosa (Spicy Tomato Chutney)", "category": "Tiffen Varieties", "subcategory": "Dosa", "price": 12.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Paneer Dosa", "category": "Tiffen Varieties", "subcategory": "Dosa", "price": 14.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Onion Dosa", "category": "Tiffen Varieties", "subcategory": "Dosa", "price": 11.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Appam", "category": "Tiffen Varieties", "subcategory": "Dosa", "price": 10.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Pessarattu (Green Lentils)", "category": "Tiffen Varieties", "subcategory": "Dosa", "price": 11.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Adai (Mixed Lentils)", "category": "Tiffen Varieties", "subcategory": "Dosa", "price": 11.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Egg Dosa", "category": "Tiffen Varieties", "subcategory": "Dosa", "price": 13.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Plain Parotta", "category": "Tiffen Varieties", "subcategory": "Parotta", "price": 9.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Veg Kothu Parotta", "category": "Tiffen Varieties", "subcategory": "Parotta", "price": 13.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Chicken Kothu Parotta", "category": "Tiffen Varieties", "subcategory": "Parotta", "price": 16.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Mutton Kothu Parotta", "category": "Tiffen Varieties", "subcategory": "Parotta", "price": 18.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Spinach Paratha", "category": "Tiffen Varieties", "subcategory": "Paratha", "price": 10.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Aloo Paratha (Potato)", "category": "Tiffen Varieties", "subcategory": "Paratha", "price": 10.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Paneer Paratha", "category": "Tiffen Varieties", "subcategory": "Paratha", "price": 12.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Vermicelli Upma", "category": "Tiffen Varieties", "subcategory": "Upma", "price": 8.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Rava Upma", "category": "Tiffen Varieties", "subcategory": "Upma", "price": 8.0, "available": True},
        
        # Gravy - Vegetarian
        {"id": str(uuid.uuid4()), "name": "Paneer Butter Masala", "category": "Gravy - Vegetarian", "price": 14.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Vegetable Kuruma", "category": "Gravy - Vegetarian", "price": 12.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Vegetable Salna", "category": "Gravy - Vegetarian", "price": 11.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Vegetable Makhanwala", "category": "Gravy - Vegetarian", "price": 13.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Aloo Gobi Masala", "category": "Gravy - Vegetarian", "price": 11.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Dal Tadka", "category": "Gravy - Vegetarian", "price": 9.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "White Chana Masala", "category": "Gravy - Vegetarian", "subcategory": "Chana Masala", "price": 10.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Black Chana Masala", "category": "Gravy - Vegetarian", "subcategory": "Chana Masala", "price": 10.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Moong Dal Masala", "category": "Gravy - Vegetarian", "subcategory": "Chana Masala", "price": 9.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Sambhar", "category": "Gravy - Vegetarian", "price": 8.0, "image_url": "https://images.unsplash.com/photo-1632104667384-06f58cb7ad44", "available": True},
        {"id": str(uuid.uuid4()), "name": "Pepper Rasam", "category": "Gravy - Vegetarian", "subcategory": "Rasam", "price": 7.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Dal Rasam", "category": "Gravy - Vegetarian", "subcategory": "Rasam", "price": 7.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Moor Kulambu (Yogurt Curry)", "category": "Gravy - Vegetarian", "price": 9.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Ladies Finger Kara Kulambu", "category": "Gravy - Vegetarian", "subcategory": "Kara Kulambu", "price": 10.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Ennai Kathirikai (Stuffed Brinjal)", "category": "Gravy - Vegetarian", "subcategory": "Kara Kulambu", "price": 11.0, "available": True},
        
        # Gravy - Non Vegetarian
        {"id": str(uuid.uuid4()), "name": "Scrambled Egg Chettinad Curry", "category": "Gravy - Non Vegetarian", "subcategory": "Egg", "price": 12.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Boiled Egg Chettinad Curry", "category": "Gravy - Non Vegetarian", "subcategory": "Egg", "price": 12.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Chicken Chettinad Curry", "category": "Gravy - Non Vegetarian", "subcategory": "Chicken", "price": 16.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Chicken Pepper Curry", "category": "Gravy - Non Vegetarian", "subcategory": "Chicken", "price": 16.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Chicken Karahi Curry", "category": "Gravy - Non Vegetarian", "subcategory": "Chicken", "price": 16.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Chicken Salna", "category": "Gravy - Non Vegetarian", "subcategory": "Chicken", "price": 15.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Chicken Butter Masala", "category": "Gravy - Non Vegetarian", "subcategory": "Chicken", "price": 17.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Mutton Chettinad Curry", "category": "Gravy - Non Vegetarian", "subcategory": "Mutton", "price": 20.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Mutton Salna", "category": "Gravy - Non Vegetarian", "subcategory": "Mutton", "price": 19.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Mutton Liver (Semi Gravy)", "category": "Gravy - Non Vegetarian", "subcategory": "Mutton", "price": 18.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Mutton Brain Pepper Fry (Semi Gravy)", "category": "Gravy - Non Vegetarian", "subcategory": "Mutton", "price": 20.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Prawn Thokku/Prawn Karahi (Mini Prawn)", "category": "Gravy - Non Vegetarian", "subcategory": "Seafood", "price": 18.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Mackerel Madras Curry", "category": "Gravy - Non Vegetarian", "subcategory": "Seafood", "price": 16.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Sea Bass Curry", "category": "Gravy - Non Vegetarian", "subcategory": "Seafood", "price": 18.0, "available": True},
        
        # Desserts
        {"id": str(uuid.uuid4()), "name": "Carrot Halwa", "category": "Desserts", "price": 8.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Beetroot Halwa", "category": "Desserts", "price": 8.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Gulab Jamun (2 pieces)", "category": "Desserts", "price": 6.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Fruit Custard", "category": "Desserts", "price": 7.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Rasmalai (2 pieces)", "category": "Desserts", "price": 7.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Basundi", "category": "Desserts", "price": 7.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Mango Lassi", "category": "Desserts", "price": 5.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Vermicelli kheer (Semiya Payasam)", "category": "Desserts", "price": 8.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Yellow Moong Dhal Payasam", "category": "Desserts", "price": 8.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Rava Kesari", "category": "Desserts", "price": 7.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Kesar Badam Pista Kulfi", "category": "Desserts", "subcategory": "Kulfi", "price": 6.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Chocolate Kulfi", "category": "Desserts", "subcategory": "Kulfi", "price": 6.0, "available": True},
        {"id": str(uuid.uuid4()), "name": "Mango Kulfi", "category": "Desserts", "subcategory": "Kulfi", "price": 6.0, "available": True},
    ]
    
    await db.menu_items.insert_many(menu_data)

# API Routes

@app.get("/api/menu")
async def get_menu():
    try:
        menu_items = await db.menu_items.find({"available": True}, {"_id": 0}).to_list(length=None)
        return {"menu_items": menu_items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/menu/categories")
async def get_categories():
    try:
        pipeline = [
            {"$group": {"_id": "$category", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}}
        ]
        categories = await db.menu_items.aggregate(pipeline).to_list(length=None)
        return {"categories": [cat["_id"] for cat in categories]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/menu/category/{category}")
async def get_menu_by_category(category: str):
    try:
        menu_items = await db.menu_items.find({"category": category, "available": True}, {"_id": 0}).to_list(length=None)
        return {"menu_items": menu_items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class OrderRequest(BaseModel):
    customer_name: str
    customer_phone: str
    customer_email: Optional[str] = None
    items: List[CartItem]
    payment_method: str
    notes: Optional[str] = None

@app.post("/api/orders")
async def create_order(order_request: OrderRequest):
    try:
        # Calculate total amount
        total_amount = sum(item.price * item.quantity for item in order_request.items)
        
        # Create order
        order = {
            "id": str(uuid.uuid4()),
            "customer_name": order_request.customer_name,
            "customer_phone": order_request.customer_phone,
            "customer_email": order_request.customer_email,
            "items": [item.dict() for item in order_request.items],
            "total_amount": total_amount,
            "payment_method": order_request.payment_method,
            "order_date": datetime.utcnow(),
            "status": "pending",
            "notes": order_request.notes
        }
        
        result = await db.orders.insert_one(order)
        return {"message": "Order placed successfully", "order_id": order["id"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Admin routes
class AdminLoginRequest(BaseModel):
    password: str

@app.post("/api/admin/login")
async def admin_login(login_request: AdminLoginRequest):
    if login_request.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid password")
    return {"message": "Login successful", "token": "admin_authenticated"}

@app.get("/api/admin/orders")
async def get_all_orders():
    try:
        orders = await db.orders.find({}, {"_id": 0}).sort("order_date", -1).to_list(length=None)
        return {"orders": orders}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/admin/menu")
async def get_admin_menu():
    try:
        menu_items = await db.menu_items.find({}, {"_id": 0}).to_list(length=None)
        return {"menu_items": menu_items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class MenuItemUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    available: Optional[bool] = None
    available_days: Optional[List[str]] = None

@app.put("/api/admin/menu/{item_id}")
async def update_menu_item(item_id: str, update_data: MenuItemUpdate):
    try:
        update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
        if not update_dict:
            raise HTTPException(status_code=400, detail="No update data provided")
        
        result = await db.menu_items.update_one(
            {"id": item_id},
            {"$set": update_dict}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Menu item not found")
        
        return {"message": "Menu item updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/admin/orders/{order_id}/status")
async def update_order_status(order_id: str, status: dict):
    try:
        result = await db.orders.update_one(
            {"id": order_id},
            {"$set": {"status": status["status"]}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Order not found")
        
        return {"message": "Order status updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)