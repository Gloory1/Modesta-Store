import uvicorn
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# Setup Templates (looks for HTML files in 'templates' folder)
templates = Jinja2Templates(directory="templates")

# --- DATA MODELS ---
# Same data structure as before
class Product:
    def __init__(self, id, name, name_ar, price, category, image_url, badge=None, description=""):
        self.id = id
        self.name = name
        self.name_ar = name_ar
        self.price = price
        self.category = category
        self.image_url = image_url
        self.badge = badge
        self.description = description

PRODUCTS_DB = [
    Product(1, "Classic Black Abaya", "عباية كلاسيك سوداء", 450, "Abayas", 
            "https://placehold.co/300x380/1a1a2e/white?text=Classic+Abaya", "Bestseller", "Elegant classic black abaya"),
    Product(2, "Butterfly Abaya", "عباية فراشة", 520, "Abayas", 
            "https://placehold.co/300x380/16213e/white?text=Butterfly+Abaya", "New", "Modern butterfly cut"),
    Product(3, "Embroidered Silk Abaya", "عباية حرير مطرزة", 680, "Abayas", 
            "https://placehold.co/300x380/0f3460/white?text=Silk+Abaya", "Premium", "Luxurious silk abaya"),
    Product(4, "Chiffon Khimar", "خمار شيفون", 180, "Khimars", 
            "https://placehold.co/300x380/b8a9c9/white?text=Chiffon+Khimar", None, "Lightweight chiffon khimar"),
    Product(5, "Premium Crepe Khimar", "خمار كريب فاخر", 220, "Khimars", 
            "https://placehold.co/300x380/9c88b8/white?text=Crepe+Khimar", "Popular", "High-quality crepe fabric"),
    Product(6, "French Khimar", "خمار فرنسي", 250, "Khimars", 
            "https://placehold.co/300x380/7b68a6/white?text=French+Khimar", "New", "Elegant French style"),
    Product(7, "Saudi Niqab", "نقاب سعودي", 120, "Niqabs", 
            "https://placehold.co/300x380/2f4858/white?text=Saudi+Niqab", None, "Traditional Saudi style"),
    Product(8, "Butterfly Niqab", "نقاب فراشة", 90, "Niqabs", 
            "https://placehold.co/300x380/34495e/white?text=Butterfly+Niqab", "Bestseller", "Comfortable butterfly niqab"),
    Product(9, "Single Layer Niqab", "نقاب طبقة واحدة", 75, "Niqabs", 
            "https://placehold.co/300x380/2c3e50/white?text=Single+Layer", None, "Simple single layer niqab"),
    Product(10, "Hijab Magnetic Pins Set", "طقم دبابيس مغناطيسية", 45, "Accessories", 
            "https://placehold.co/300x380/f8a5c2/white?text=Magnetic+Pins", "Popular", "Set of 12 magnetic hijab pins"),
    Product(11, "Silk Headband Collection", "مجموعة باندانا حرير", 65, "Accessories", 
            "https://placehold.co/300x380/ff6b81/white?text=Silk+Headband", None, "Pack of 3 silk headbands"),
    Product(12, "Premium Underscarves Pack", "طقم بطانات فاخرة", 85, "Accessories", 
            "https://placehold.co/300x380/f78fb3/white?text=Underscarves", "New", "Set of 5 premium cotton underscarves"),
]

# Order Model for API
class OrderItem(BaseModel):
    product_id: int
    quantity: int

class Order(BaseModel):
    name: str
    phone: str
    address: str
    items: List[OrderItem]

# --- ROUTES ---

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, category: Optional[str] = None):
    """
    Renders the HTML page. 
    If a category is selected, it filters the products.
    """
    if category and category != "All":
        filtered_products = [p for p in PRODUCTS_DB if p.category == category]
    else:
        filtered_products = PRODUCTS_DB
        
    categories = ["Abayas", "Khimars", "Niqabs", "Accessories"]
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "products": filtered_products,
        "categories": categories,
        "current_category": category or "All"
    })

@app.post("/api/checkout")
async def checkout(order: Order):
    """
    API endpoint to receive order data from JavaScript
    """
    order_id = f"MOD-{abs(hash(order.name)) % 100000:05d}"
    print(f"New Order Received: {order_id}")
    print(f"Customer: {order.name}, Items: {len(order.items)}")
    return {"status": "success", "order_id": order_id}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
