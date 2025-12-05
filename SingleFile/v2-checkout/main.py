from pywebio import start_server, config
from pywebio.output import put_html, put_buttons, put_row, put_markdown, clear, use_scope, popup, toast, put_table, close_popup, put_column
from pywebio.input import input_group, input, select, textarea, NUMBER
from pywebio.session import run_js, set_env
from dataclasses import dataclass, field
from typing import List, Dict, Optional

# ==========================================
# 1. MODELS & DATA LAYER
# ==========================================

@dataclass
class Product:
    id: int
    name: str
    name_ar: str
    price: float
    category: str
    image_url: str
    badge: Optional[str] = None
    description: str = ""

@dataclass
class CartItem:
    product: Product
    quantity: int = 1

    @property
    def total_price(self) -> float:
        return self.product.price * self.quantity

class Cart:
    def __init__(self):
        self.items: List[CartItem] = []

    def add_product(self, product: Product):
        for item in self.items:
            if item.product.id == product.id:
                item.quantity += 1
                return
        self.items.append(CartItem(product=product))

    def remove_product(self, product_id: int):
        self.items = [item for item in self.items if item.product.id != product_id]

    def update_quantity(self, product_id: int, quantity: int):
        for item in self.items:
            if item.product.id == product_id:
                if quantity <= 0:
                    self.remove_product(product_id)
                else:
                    item.quantity = quantity
                return

    def get_total(self) -> float:
        return sum(item.total_price for item in self.items)

    def get_count(self) -> int:
        return sum(item.quantity for item in self.items)

    def clear_cart(self):
        self.items = []

PRODUCTS_DB = [
    Product(1, "Classic Black Abaya", "عباية كلاسيك سوداء", 450, "Abayas", 
            "https://placehold.co/300x380/1a1a2e/white?text=Classic+Abaya", "Bestseller",
            "Elegant classic black abaya with premium fabric"),
    Product(2, "Butterfly Abaya", "عباية فراشة", 520, "Abayas", 
            "https://placehold.co/300x380/16213e/white?text=Butterfly+Abaya", "New",
            "Modern butterfly cut with flowing sleeves"),
    Product(3, "Embroidered Silk Abaya", "عباية حرير مطرزة", 680, "Abayas", 
            "https://placehold.co/300x380/0f3460/white?text=Silk+Abaya", "Premium",
            "Luxurious silk abaya with delicate embroidery"),
    Product(4, "Chiffon Khimar", "خمار شيفون", 180, "Khimars", 
            "https://placehold.co/300x380/b8a9c9/white?text=Chiffon+Khimar", None,
            "Lightweight chiffon khimar for daily wear"),
    Product(5, "Premium Crepe Khimar", "خمار كريب فاخر", 220, "Khimars", 
            "https://placehold.co/300x380/9c88b8/white?text=Crepe+Khimar", "Popular",
            "High-quality crepe fabric with beautiful drape"),
    Product(6, "French Khimar", "خمار فرنسي", 250, "Khimars", 
            "https://placehold.co/300x380/7b68a6/white?text=French+Khimar", "New",
            "Elegant French style khimar"),
    Product(7, "Saudi Niqab", "نقاب سعودي", 120, "Niqabs", 
            "https://placehold.co/300x380/2f4858/white?text=Saudi+Niqab", None,
            "Traditional Saudi style niqab"),
    Product(8, "Butterfly Niqab", "نقاب فراشة", 90, "Niqabs", 
            "https://placehold.co/300x380/34495e/white?text=Butterfly+Niqab", "Bestseller",
            "Comfortable butterfly niqab design"),
    Product(9, "Single Layer Niqab", "نقاب طبقة واحدة", 75, "Niqabs", 
            "https://placehold.co/300x380/2c3e50/white?text=Single+Layer", None,
            "Simple single layer niqab"),
    Product(10, "Hijab Magnetic Pins Set", "طقم دبابيس مغناطيسية", 45, "Accessories", 
            "https://placehold.co/300x380/f8a5c2/white?text=Magnetic+Pins", "Popular",
            "Set of 12 magnetic hijab pins"),
    Product(11, "Silk Headband Collection", "مجموعة باندانا حرير", 65, "Accessories", 
            "https://placehold.co/300x380/ff6b81/white?text=Silk+Headband", None,
            "Pack of 3 silk headbands"),
    Product(12, "Premium Underscarves Pack", "طقم بطانات فاخرة", 85, "Accessories", 
            "https://placehold.co/300x380/f78fb3/white?text=Underscarves", "New",
            "Set of 5 premium cotton underscarves"),
]

# ==========================================
# 2. UI / PRESENTATION LAYER
# ==========================================

class UI:
    @staticmethod
    def get_styles():
        return """
        <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&family=Playfair+Display:wght@400;600;700&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            * { box-sizing: border-box; }

            body, .pywebio {
                font-family: 'Tajawal', sans-serif !important;
                background: linear-gradient(135deg, #fff0f5 0%, #ffe4ec 50%, #fff5f8 100%) !important;
                min-height: 100vh;
                padding-top: 85px !important;
                padding-bottom: 120px !important;
            }

            .markdown-body { font-family: 'Tajawal', sans-serif !important; }

            @keyframes fadeInUp {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }

            .product-card { animation: fadeInUp 0.5s ease-out; }

            .product-card:hover {
                transform: translateY(-8px) !important;
                box-shadow: 0 20px 60px rgba(232, 67, 147, 0.25) !important;
            }

            .product-card:hover img { transform: scale(1.05); }

            .badge-bestseller { background: linear-gradient(135deg, #e84393, #fd79a8) !important; }
            .badge-new { background: linear-gradient(135deg, #00b894, #55efc4) !important; }
            .badge-premium { background: linear-gradient(135deg, #fdcb6e, #f39c12) !important; }
            .badge-popular { background: linear-gradient(135deg, #a55eea, #8854d0) !important; }
        </style>
        """

    @staticmethod
    def load_resources():
        put_html(UI.get_styles())

        run_js("""
            var style = document.createElement('style');
            style.innerHTML = `
                .btn, .btn-primary, .btn-secondary, .btn-link,
                button.btn, button.btn-primary, button.btn-secondary,
                .btn.btn-primary, .btn.btn-secondary,
                input[type="button"], input[type="submit"] {
                    background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%) !important;
                    background-color: #ff9a9e !important;
                    border: none !important;
                    color: white !important;
                    font-weight: 600 !important;
                    border-radius: 25px !important;
                    padding: 12px 25px !important;
                    transition: all 0.3s ease !important;
                    box-shadow: 0 4px 15px rgba(232, 67, 147, 0.25) !important;
                    font-family: 'Tajawal', sans-serif !important;
                    font-size: 15px !important;
                    text-decoration: none !important;
                }

                .btn:hover, .btn-primary:hover, .btn-secondary:hover,
                button.btn:hover, button.btn-primary:hover,
                .btn.btn-primary:hover, .btn.btn-secondary:hover {
                    background: linear-gradient(135deg, #e84393 0%, #ff9a9e 100%) !important;
                    background-color: #e84393 !important;
                    transform: translateY(-2px) !important;
                    box-shadow: 0 6px 20px rgba(232, 67, 147, 0.35) !important;
                    color: white !important;
                }

                .btn:focus, .btn-primary:focus, .btn-secondary:focus {
                    box-shadow: 0 0 0 3px rgba(232, 67, 147, 0.3) !important;
                    outline: none !important;
                }

                input, select, textarea {
                    border: 2px solid #fecfef !important;
                    border-radius: 15px !important;
                    padding: 12px 18px !important;
                    font-family: 'Tajawal', sans-serif !important;
                    transition: all 0.3s ease !important;
                }

                input:focus, select:focus, textarea:focus {
                    border-color: #e84393 !important;
                    box-shadow: 0 0 0 3px rgba(232, 67, 147, 0.15) !important;
                    outline: none !important;
                }

                .form-label {
                    color: #5f27cd !important;
                    font-weight: 600 !important;
                }
            `;
            document.head.appendChild(style);
        """)

    @staticmethod
    def render_header(cart_count: int, on_cart_click, on_home_click):
        with use_scope('header', clear=True):
            put_html(f"""
            <div id="sticky-header" style="
                position: fixed; top: 0; left: 0; right: 0;
                background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 50%, #fad0c4 100%);
                padding: 18px 30px;
                box-shadow: 0 4px 30px rgba(255, 154, 158, 0.4);
                z-index: 1000;
                display: flex; justify-content: space-between; align-items: center;
            ">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <i class="fas fa-mosque" style="font-size: 28px; color: white; text-shadow: 2px 2px 4px rgba(0,0,0,0.15);"></i>
                    <div style="
                        font-size: 28px; font-weight: 700; color: white;
                        text-shadow: 2px 2px 4px rgba(0,0,0,0.15);
                        letter-spacing: 2px; font-family: 'Playfair Display', serif;
                    ">Modesta</div>
                </div>
                <div id="nav-buttons-container"></div>
            </div>
            """)

            put_row([
                put_buttons([{'label': ' Home', 'value': 'home'}], onclick=[lambda: on_home_click()]),
                put_buttons([{'label': f' Cart ({cart_count})', 'value': 'cart'}], onclick=[lambda: on_cart_click()])
            ], size='auto').style('''
                position: fixed; top: 18px; right: 30px; z-index: 1001; display: flex; gap: 10px;
            ''')

    @staticmethod
    def render_hero_section():
        put_html("""
        <div style="text-align: center; padding: 50px 20px 30px 20px; animation: fadeInUp 0.6s ease-out;">
            <h1 style="
                font-size: 52px; font-weight: 700;
                background: linear-gradient(135deg, #e84393, #a55eea, #e84393);
                background-size: 200% auto;
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                margin-bottom: 15px; font-family: 'Playfair Display', serif; letter-spacing: 3px;
            ">MODESTA</h1>

            <p style="
                font-size: 20px; color: #a55eea; font-weight: 500;
                margin-bottom: 5px; letter-spacing: 4px; text-transform: uppercase;
            ">Where Modesty Meets Elegance</p>

            <div style="
                height: 4px; background: linear-gradient(90deg, transparent, #fecfef, #ff9a9e, #e84393, #ff9a9e, #fecfef, transparent);
                margin: 30px auto; max-width: 300px; border-radius: 2px;
            "></div>
        </div>
        """)

        put_html("""
        <div style="
            background: linear-gradient(135deg, #ffffff 0%, #fff9fc 100%);
            border-radius: 25px; padding: 40px 50px; max-width: 850px;
            margin: 0 auto 50px auto; box-shadow: 0 20px 60px rgba(232, 67, 147, 0.12);
            border-left: 5px solid #e84393; position: relative; overflow: hidden;
            animation: fadeInUp 0.8s ease-out;
        ">
            <div style="
                position: absolute; top: -20px; left: 20px; font-size: 100px;
                color: rgba(232, 67, 147, 0.06); font-family: Georgia, serif; line-height: 1;
            ">"</div>

            <p style="
                font-size: 18px; line-height: 2.2; color: #5f27cd;
                font-weight: 500; position: relative; z-index: 1; font-style: italic;
            ">
                O Prophet, tell your wives and your daughters and the women of the believers 
                to bring down over themselves [part] of their outer garments. That is more suitable 
                that they will be known and not be abused.
            </p>

            <p style="
                color: #e84393; font-size: 14px; margin-top: 25px; font-weight: 700;
                text-align: right; letter-spacing: 1px;
            "><i class="fas fa-book-quran" style="margin-right: 8px;"></i>[Al-Ahzab: 59]</p>
        </div>
        """)

        put_html("""
        <div style="
            display: flex; justify-content: center; gap: 40px; flex-wrap: wrap;
            padding: 30px 20px; max-width: 900px; margin: 0 auto 40px auto;
        ">
            <div style="text-align: center;">
                <div style="
                    width: 70px; height: 70px; background: linear-gradient(135deg, #ff9a9e, #fecfef);
                    border-radius: 50%; display: flex; align-items: center; justify-content: center;
                    margin: 0 auto 15px auto; box-shadow: 0 8px 25px rgba(232, 67, 147, 0.2);
                ">
                    <i class="fas fa-truck-fast" style="font-size: 28px; color: white;"></i>
                </div>
                <p style="color: #5f27cd; font-weight: 600; font-size: 14px;">Free Shipping</p>
                <p style="color: #999; font-size: 12px;">Orders over 500 EGP</p>
            </div>
            <div style="text-align: center;">
                <div style="
                    width: 70px; height: 70px; background: linear-gradient(135deg, #a55eea, #8854d0);
                    border-radius: 50%; display: flex; align-items: center; justify-content: center;
                    margin: 0 auto 15px auto; box-shadow: 0 8px 25px rgba(165, 94, 234, 0.2);
                ">
                    <i class="fas fa-shield-heart" style="font-size: 28px; color: white;"></i>
                </div>
                <p style="color: #5f27cd; font-weight: 600; font-size: 14px;">Quality Guarantee</p>
                <p style="color: #999; font-size: 12px;">Premium fabrics only</p>
            </div>
            <div style="text-align: center;">
                <div style="
                    width: 70px; height: 70px; background: linear-gradient(135deg, #00b894, #55efc4);
                    border-radius: 50%; display: flex; align-items: center; justify-content: center;
                    margin: 0 auto 15px auto; box-shadow: 0 8px 25px rgba(0, 184, 148, 0.2);
                ">
                    <i class="fas fa-rotate-left" style="font-size: 28px; color: white;"></i>
                </div>
                <p style="color: #5f27cd; font-weight: 600; font-size: 14px;">Easy Returns</p>
                <p style="color: #999; font-size: 12px;">14-day return policy</p>
            </div>
        </div>
        """)

    @staticmethod
    def render_categories(categories: List[str], on_select):
        category_icons = {
            "Abayas": "fa-person-dress",
            "Khimars": "fa-user-nurse",
            "Niqabs": "fa-mask",
            "Accessories": "fa-gem"
        }

        put_html("""
        <div style="text-align: center; padding: 20px;">
            <h2 style="
                font-size: 32px; color: #5f27cd; margin-bottom: 10px;
                font-weight: 700; font-family: 'Playfair Display', serif;
            ">Shop by Category</h2>
            <p style="color: #a55eea; font-size: 16px; margin-bottom: 35px;">Find your perfect modest wear</p>
        </div>
        """)

        cats_html = '<div style="display: flex; justify-content: center; flex-wrap: wrap; gap: 25px; padding: 10px 20px; max-width: 900px; margin: 0 auto;">'
        for cat in categories:
            icon = category_icons.get(cat, "fa-tag")
            cats_html += f"""
            <div class="category-card" id="cat-{cat}" style="
                background: white; border-radius: 20px; padding: 30px 40px; text-align: center;
                cursor: pointer; transition: all 0.3s ease; box-shadow: 0 8px 30px rgba(232, 67, 147, 0.1);
                border: 2px solid transparent; min-width: 180px;
            " onmouseover="this.style.transform='translateY(-5px)'; this.style.borderColor='#e84393'; this.style.boxShadow='0 15px 40px rgba(232, 67, 147, 0.2)';"
               onmouseout="this.style.transform='translateY(0)'; this.style.borderColor='transparent'; this.style.boxShadow='0 8px 30px rgba(232, 67, 147, 0.1)';">
                <i class="fas {icon}" style="font-size: 40px; color: #e84393; margin-bottom: 15px;"></i>
                <p style="color: #2d3436; font-weight: 700; font-size: 18px; margin: 0;">{cat}</p>
            </div>
            """
        cats_html += '</div>'
        put_html(cats_html)

        with use_scope('hidden_cats', clear=True):
            put_buttons([{'label': cat, 'value': cat} for cat in categories], onclick=on_select)

        run_js("""
            var hiddenScope = document.querySelector('[id*="hidden_cats"]');
            if(hiddenScope) {
                hiddenScope.style.display = 'none';
                hiddenScope.style.visibility = 'hidden';
                hiddenScope.style.height = '0';
                hiddenScope.style.overflow = 'hidden';
            }
        """)

        for cat in categories:
            run_js(f"""
                document.getElementById('cat-{cat}').onclick = function() {{
                    var btns = document.querySelectorAll('button.btn');
                    btns.forEach(function(btn) {{
                        if(btn.innerText.trim() === '{cat}') btn.click();
                    }});
                }};
            """)

    @staticmethod
    def render_products(products: List[Product], on_add_to_cart, on_back):
        put_html('<div style="text-align: center; margin: 30px 0;">')
        put_buttons([{'label': ' Back to Categories', 'value': 'back'}], onclick=[lambda: on_back()]).style('''
            display: inline-flex; align-items: center; gap: 8px;
        ''')
        put_html("</div>")

        if not products:
            put_html('''
            <div style="
                text-align: center; padding: 60px 40px; background: white; border-radius: 25px;
                max-width: 500px; margin: 20px auto; box-shadow: 0 10px 40px rgba(232, 67, 147, 0.1);
            ">
                <i class="fas fa-box-open" style="font-size: 60px; color: #fecfef; margin-bottom: 20px;"></i>
                <p style="color: #a55eea; font-size: 20px; font-weight: 600;">No products found</p>
                <p style="color: #999; font-size: 14px;">Check back soon for new arrivals!</p>
            </div>
            ''')
            return

        put_html('<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 35px; padding: 30px; max-width: 1300px; margin: 0 auto;">')

        for i, p in enumerate(products):
            badge_html = ""
            if p.badge:
                badge_html = f"""
                <div style="
                    position: absolute; top: 15px; left: 15px; padding: 6px 14px;
                    border-radius: 20px; color: white; font-size: 12px; font-weight: 700;
                    letter-spacing: 0.5px; z-index: 10;
                    background: linear-gradient(135deg, #e84393, #fd79a8);
                " class="badge-{p.badge.lower()}">{p.badge}</div>
                """

            put_html(f"""
            <div class="product-card" style="
                background: white; border-radius: 25px; overflow: hidden;
                box-shadow: 0 10px 40px rgba(232, 67, 147, 0.1); transition: all 0.4s ease;
                border: 2px solid rgba(232, 67, 147, 0.08); position: relative;
                animation-delay: {i * 0.1}s;
            ">
                {badge_html}
                <div style="position: relative; overflow: hidden;">
                    <img src="{p.image_url}" alt="{p.name}" style="
                        width: 100%; height: 280px; object-fit: cover; transition: transform 0.5s ease;
                    ">
                    <div style="
                        position: absolute; bottom: 0; left: 0; right: 0; height: 80px;
                        background: linear-gradient(to top, white, transparent);
                    "></div>
                </div>
                <div style="padding: 25px; text-align: center; background: white;">
                    <h3 style="
                        font-size: 20px; font-weight: 700; color: #2d3436; margin-bottom: 5px;
                    ">{p.name}</h3>
                    <p style="
                        font-size: 14px; color: #a55eea; margin-bottom: 8px; font-weight: 500;
                    ">{p.name_ar}</p>
                    <p style="
                        font-size: 13px; color: #999; margin-bottom: 15px; line-height: 1.5;
                    ">{p.description}</p>
                    <p style="
                        font-size: 28px; font-weight: 800; color: #e84393; margin-bottom: 5px;
                    ">{int(p.price)} <span style="font-size: 16px; font-weight: 600;">EGP</span></p>
                </div>
            </div>
            """)
            put_buttons([{'label': ' Add to Cart', 'value': p.id}], 
                       onclick=[lambda p=p: on_add_to_cart(p)]).style('''
                display: block; margin: -10px 25px 25px 25px; text-align: center;
            ''')

        put_html('</div>')

    @staticmethod
    def render_footer():
        put_html("""
        <footer style="
            background: linear-gradient(135deg, #2d3436 0%, #1a1a2e 100%);
            padding: 60px 30px 30px 30px; margin-top: 80px; color: white;
        ">
            <div style="
                max-width: 1200px; margin: 0 auto; display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 40px;
            ">
                <div>
                    <h3 style="
                        font-size: 28px; font-family: 'Playfair Display', serif; margin-bottom: 20px;
                        background: linear-gradient(135deg, #ff9a9e, #fecfef);
                        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                    ">Modesta</h3>
                    <p style="color: #b2bec3; line-height: 1.8; font-size: 14px;">
                        Your destination for elegant modest fashion. 
                        We believe in empowering women through beautiful, 
                        comfortable, and stylish modest wear.
                    </p>
                </div>

                <div>
                    <h4 style="color: #fecfef; margin-bottom: 20px; font-size: 16px;">Quick Links</h4>
                    <ul style="list-style: none; padding: 0; margin: 0;">
                        <li style="margin-bottom: 12px;"><span style="color: #b2bec3; font-size: 14px;"><i class="fas fa-chevron-right" style="color: #e84393; margin-right: 8px; font-size: 10px;"></i>About Us</span></li>
                        <li style="margin-bottom: 12px;"><span style="color: #b2bec3; font-size: 14px;"><i class="fas fa-chevron-right" style="color: #e84393; margin-right: 8px; font-size: 10px;"></i>Size Guide</span></li>
                        <li style="margin-bottom: 12px;"><span style="color: #b2bec3; font-size: 14px;"><i class="fas fa-chevron-right" style="color: #e84393; margin-right: 8px; font-size: 10px;"></i>Shipping Policy</span></li>
                        <li style="margin-bottom: 12px;"><span style="color: #b2bec3; font-size: 14px;"><i class="fas fa-chevron-right" style="color: #e84393; margin-right: 8px; font-size: 10px;"></i>Return Policy</span></li>
                    </ul>
                </div>

                <div>
                    <h4 style="color: #fecfef; margin-bottom: 20px; font-size: 16px;">Contact Us</h4>
                    <p style="color: #b2bec3; margin-bottom: 12px; font-size: 14px;">
                        <i class="fas fa-envelope" style="color: #e84393; margin-right: 10px;"></i>
                        support@modesta.com
                    </p>
                    <p style="color: #b2bec3; margin-bottom: 12px; font-size: 14px;">
                        <i class="fas fa-phone" style="color: #e84393; margin-right: 10px;"></i>
                        +20 123 456 7890
                    </p>
                    <p style="color: #b2bec3; font-size: 14px;">
                        <i class="fas fa-location-dot" style="color: #e84393; margin-right: 10px;"></i>
                        Cairo, Egypt
                    </p>
                </div>

                <div>
                    <h4 style="color: #fecfef; margin-bottom: 20px; font-size: 16px;">Follow Us</h4>
                    <div style="display: flex; gap: 15px;">
                        <div style="
                            width: 45px; height: 45px; background: linear-gradient(135deg, #ff9a9e, #fecfef);
                            border-radius: 50%; display: flex; align-items: center; justify-content: center;
                            cursor: pointer; transition: transform 0.3s ease;
                        "><i class="fab fa-instagram" style="color: white; font-size: 20px;"></i></div>
                        <div style="
                            width: 45px; height: 45px; background: linear-gradient(135deg, #a55eea, #8854d0);
                            border-radius: 50%; display: flex; align-items: center; justify-content: center;
                            cursor: pointer; transition: transform 0.3s ease;
                        "><i class="fab fa-facebook-f" style="color: white; font-size: 20px;"></i></div>
                        <div style="
                            width: 45px; height: 45px; background: linear-gradient(135deg, #00b894, #55efc4);
                            border-radius: 50%; display: flex; align-items: center; justify-content: center;
                            cursor: pointer; transition: transform 0.3s ease;
                        "><i class="fab fa-whatsapp" style="color: white; font-size: 20px;"></i></div>
                    </div>
                </div>
            </div>

            <div style="border-top: 1px solid rgba(255,255,255,0.1); margin-top: 50px; padding-top: 25px; text-align: center;">
                <p style="color: #636e72; font-size: 13px;">
                    © 2024 Modesta Store. All rights reserved. Made with <i class="fas fa-heart" style="color: #e84393;"></i> for modest fashion
                </p>
            </div>
        </footer>
        """)

# ==========================================
# 3. CONTROLLER
# ==========================================

class ShopController:
    def __init__(self):
        self.cart = Cart()
        self.ui = UI()
        self.categories = ["Abayas", "Khimars", "Niqabs", "Accessories"]

    def start(self):
        set_env(title="Modesta Store - Elegant Modest Fashion")
        self.ui.load_resources()
        self.show_home()

    def refresh_header(self):
        self.ui.render_header(
            cart_count=self.cart.get_count(),
            on_cart_click=self.show_cart,
            on_home_click=self.show_home
        )

    def show_home(self):
        clear()
        run_js('window.scrollTo(0,0);')  # <<<<< Added Fix
        self.refresh_header()
        self.ui.render_hero_section()
        self.ui.render_categories(self.categories, self.show_category_page)
        self.ui.render_footer()

    def show_category_page(self, category_name):
        clear()
        run_js('window.scrollTo(0,0);')  # <<<<< Added Fix
        self.refresh_header()

        filtered_products = [p for p in PRODUCTS_DB if p.category == category_name]

        category_icons = {
            "Abayas": "fa-person-dress",
            "Khimars": "fa-user-nurse",
            "Niqabs": "fa-mask",
            "Accessories": "fa-gem"
        }
        icon = category_icons.get(category_name, "fa-tag")

        put_html(f'''
        <div style="text-align: center; padding: 100px 20px 20px 20px;">
            <div style="
                width: 80px; height: 80px; background: linear-gradient(135deg, #ff9a9e, #fecfef);
                border-radius: 50%; display: flex; align-items: center; justify-content: center;
                margin: 0 auto 20px auto; box-shadow: 0 10px 30px rgba(232, 67, 147, 0.2);
            ">
                <i class="fas {icon}" style="font-size: 35px; color: white;"></i>
            </div>
            <h1 style="
                font-size: 38px; color: #5f27cd; margin-bottom: 10px;
                font-weight: 700; font-family: 'Playfair Display', serif;
            ">{category_name}</h1>
            <p style="color: #a55eea; font-size: 16px;">{len(filtered_products)} products available</p>
            <div style="
                height: 4px; background: linear-gradient(90deg, transparent, #fecfef, #e84393, #fecfef, transparent);
                margin: 25px auto; max-width: 150px; border-radius: 2px;
            "></div>
        </div>
        ''')

        self.ui.render_products(
            products=filtered_products,
            on_add_to_cart=self.add_to_cart,
            on_back=self.show_home
        )
        self.ui.render_footer()

    def add_to_cart(self, product: Product):
        self.cart.add_product(product)
        toast(f"Added {product.name} to cart!", color='success')
        self.refresh_header()

    def show_cart(self):
        if not self.cart.items:
            popup('Shopping Cart', [
                put_html('''
                <div style="text-align: center; padding: 50px 30px;">
                    <i class="fas fa-shopping-bag" style="font-size: 70px; color: #fecfef; margin-bottom: 25px;"></i>
                    <h3 style="color: #5f27cd; font-size: 22px; margin-bottom: 10px;">Your cart is empty</h3>
                    <p style="color: #999; font-size: 15px;">Start shopping to add beautiful items!</p>
                </div>
                ''')
            ])
            return

        content = []
        content.append(put_html('''
        <div style="
            background: linear-gradient(135deg, #ff9a9e, #fecfef); padding: 20px;
            margin: -20px -20px 25px -20px; text-align: center;
        ">
            <h2 style="
                color: white; font-size: 24px; font-weight: 700; margin: 0;
                text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
            "><i class="fas fa-shopping-bag" style="margin-right: 10px;"></i>Your Shopping Cart</h2>
        </div>
        '''))

        for item in self.cart.items:
            content.append(put_html(f'''
            <div style="
                display: flex; align-items: center; padding: 20px; background: #fff9fc;
                border-radius: 15px; margin-bottom: 15px; gap: 20px;
            ">
                <img src="{item.product.image_url}" style="
                    width: 80px; height: 80px; object-fit: cover; border-radius: 12px;
                ">
                <div style="flex: 1;">
                    <h4 style="color: #2d3436; margin: 0 0 5px 0; font-size: 16px;">{item.product.name}</h4>
                    <p style="color: #a55eea; margin: 0; font-size: 14px;">{item.product.name_ar}</p>
                    <p style="color: #e84393; font-weight: 700; margin: 8px 0 0 0;">{int(item.product.price)} EGP</p>
                </div>
                <div style="text-align: center;">
                    <p style="color: #5f27cd; font-weight: 600; margin: 0 0 5px 0;">Qty: {item.quantity}</p>
                    <p style="color: #e84393; font-weight: 700; font-size: 18px; margin: 0;">{int(item.total_price)} EGP</p>
                </div>
            </div>
            '''))

        content.append(put_html(f'''
        <div style="
            background: linear-gradient(135deg, #d5f5e3 0%, #abebc6 100%);
            padding: 25px; border-radius: 20px; margin-top: 20px;
            display: flex; justify-content: space-between; align-items: center;
        ">
            <span style="color: #27ae60; font-size: 18px; font-weight: 600;">Total Amount:</span>
            <span style="color: #27ae60; font-size: 28px; font-weight: 800;">{int(self.cart.get_total())} EGP</span>
        </div>
        '''))

        content.append(put_buttons([
            {'label': ' Proceed to Checkout', 'value': 'checkout'}
        ], onclick=[lambda: self.show_checkout()]).style('margin-top: 25px;'))

        popup('Shopping Cart', content)

    def show_checkout(self):
        close_popup()
        clear()
        run_js('window.scrollTo(0,0);')  # <<<<< Added Fix
        self.refresh_header()

        put_html('''
        <div style="max-width: 1100px; margin: 0 auto; padding: 100px 20px;">
            <div style="text-align: center; margin-bottom: 40px;">
                <div style="
                    width: 80px; height: 80px; background: linear-gradient(135deg, #00b894, #55efc4);
                    border-radius: 50%; display: flex; align-items: center; justify-content: center;
                    margin: 0 auto 20px auto; box-shadow: 0 10px 30px rgba(0, 184, 148, 0.2);
                ">
                    <i class="fas fa-credit-card" style="font-size: 35px; color: white;"></i>
                </div>
                <h1 style="
                    font-size: 36px; color: #5f27cd; margin-bottom: 10px;
                    font-family: 'Playfair Display', serif;
                ">Checkout</h1>
                <p style="color: #a55eea;">Complete your order</p>
            </div>
        </div>
        ''')

        cart_items_html = ""
        for item in self.cart.items:
            cart_items_html += f'''
            <div style="
                display: flex; align-items: center; padding: 15px; background: #fff9fc;
                border-radius: 12px; margin-bottom: 12px; gap: 15px;
            ">
                <img src="{item.product.image_url}" style="
                    width: 60px; height: 60px; object-fit: cover; border-radius: 10px;
                ">
                <div style="flex: 1;">
                    <h4 style="color: #2d3436; margin: 0 0 3px 0; font-size: 14px;">{item.product.name}</h4>
                    <p style="color: #a55eea; margin: 0; font-size: 12px;">{item.product.name_ar}</p>
                </div>
                <div style="text-align: right;">
                    <p style="color: #666; margin: 0; font-size: 12px;">x{item.quantity}</p>
                    <p style="color: #e84393; font-weight: 700; margin: 0;">{int(item.total_price)} EGP</p>
                </div>
            </div>
            '''

        put_html(f'''
        <div style="
            max-width: 1100px; margin: 0 auto; display: grid;
            grid-template-columns: 1fr 400px; gap: 30px; padding: 0 20px;
        ">
            <div style="
                background: white; border-radius: 25px; padding: 30px;
                box-shadow: 0 10px 40px rgba(232, 67, 147, 0.1);
            ">
                <h3 style="color: #5f27cd; margin-bottom: 25px; font-size: 20px;">
                    <i class="fas fa-user" style="color: #e84393; margin-right: 10px;"></i>
                    Shipping Information
                </h3>
                <div id="form-container"></div>
            </div>

            <div>
                <div style="
                    background: white; border-radius: 25px; padding: 25px;
                    box-shadow: 0 10px 40px rgba(232, 67, 147, 0.1); margin-bottom: 20px;
                ">
                    <h3 style="color: #5f27cd; margin-bottom: 20px; font-size: 18px;">
                        <i class="fas fa-shopping-bag" style="color: #e84393; margin-right: 10px;"></i>
                        Order Summary ({self.cart.get_count()} items)
                    </h3>

                    <div style="max-height: 300px; overflow-y: auto;">
                        {cart_items_html}
                    </div>

                    <div style="border-top: 2px dashed #fecfef; margin-top: 15px; padding-top: 15px;">
                        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                            <span style="color: #666;">Subtotal</span>
                            <span style="color: #2d3436; font-weight: 600;">{int(self.cart.get_total())} EGP</span>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                            <span style="color: #666;">Shipping</span>
                            <span style="color: #27ae60; font-weight: 600;">FREE</span>
                        </div>
                        <div style="
                            display: flex; justify-content: space-between; margin-top: 15px;
                            padding-top: 15px; border-top: 2px solid #fecfef;
                        ">
                            <span style="color: #5f27cd; font-weight: 700; font-size: 18px;">Total</span>
                            <span style="color: #e84393; font-weight: 800; font-size: 22px;">{int(self.cart.get_total())} EGP</span>
                        </div>
                    </div>
                </div>

                <div style="
                    background: white; border-radius: 25px; padding: 25px;
                    box-shadow: 0 10px 40px rgba(232, 67, 147, 0.1);
                ">
                    <h3 style="color: #5f27cd; margin-bottom: 20px; font-size: 18px;">
                        <i class="fas fa-wallet" style="color: #e84393; margin-right: 10px;"></i>
                        Payment Method
                    </h3>

                    <div style="
                        padding: 15px; background: linear-gradient(135deg, #fff9fc, #fff0f5);
                        border-radius: 12px; border: 2px solid #e84393; margin-bottom: 12px; cursor: pointer;
                    ">
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <i class="fas fa-money-bill-wave" style="font-size: 24px; color: #27ae60;"></i>
                            <div>
                                <p style="color: #2d3436; font-weight: 600; margin: 0;">Cash on Delivery</p>
                                <p style="color: #666; font-size: 12px; margin: 0;">Pay when you receive</p>
                            </div>
                            <i class="fas fa-check-circle" style="color: #e84393; margin-left: auto; font-size: 20px;"></i>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        ''')

        try:
            info = input_group("", [
                input("Full Name", name="name", placeholder="Enter your full name"),
                input("Phone Number", name="phone", placeholder="+20 XXX XXX XXXX"),
                input("Email", name="email", type="email", placeholder="your@email.com"),
                textarea("Shipping Address", name="address", placeholder="Street, Building, Floor, Apartment..."),
                select("City", name="city", options=["Cairo", "Alexandria", "Giza", "Other"]),
            ])

            if info:
                clear()
                run_js('window.scrollTo(0,0);')  # <<<<< Added Fix
                self.refresh_header()
                self.show_order_confirmation(info)
        except:
            pass

    def show_order_confirmation(self, info):
        order_id = f"MOD-{hash(info['name']) % 100000:05d}"

        put_html(f'''
        <div style="
            max-width: 700px; margin: 50px auto; padding: 50px; background: white;
            border-radius: 30px; box-shadow: 0 20px 60px rgba(232, 67, 147, 0.15); text-align: center;
        ">
            <div style="
                width: 100px; height: 100px; background: linear-gradient(135deg, #00b894, #55efc4);
                border-radius: 50%; display: flex; align-items: center; justify-content: center;
                margin: 0 auto 30px auto; box-shadow: 0 15px 40px rgba(0, 184, 148, 0.3);
            ">
                <i class="fas fa-check" style="font-size: 50px; color: white;"></i>
            </div>

            <h1 style="
                font-size: 36px; color: #27ae60; margin-bottom: 15px; font-family: 'Playfair Display', serif;
            ">Order Confirmed!</h1>

            <p style="color: #666; font-size: 18px; margin-bottom: 30px;">
                Thank you for shopping with Modesta
            </p>

            <div style="
                background: linear-gradient(135deg, #fff9fc, #fff0f5);
                padding: 25px; border-radius: 20px; margin-bottom: 30px;
            ">
                <p style="color: #a55eea; font-size: 14px; margin-bottom: 5px;">Order Number</p>
                <p style="color: #e84393; font-size: 28px; font-weight: 800; letter-spacing: 2px;">{order_id}</p>
            </div>

            <div style="
                background: #f8f9fa; padding: 25px; border-radius: 15px; text-align: left; margin-bottom: 30px;
            ">
                <h4 style="color: #5f27cd; margin-bottom: 15px;">
                    <i class="fas fa-truck" style="color: #e84393; margin-right: 10px;"></i>
                    Delivery Details
                </h4>
                <p style="color: #666; margin: 5px 0;"><strong>Name:</strong> {info['name']}</p>
                <p style="color: #666; margin: 5px 0;"><strong>Phone:</strong> {info['phone']}</p>
                <p style="color: #666; margin: 5px 0;"><strong>City:</strong> {info['city']}</p>
                <p style="color: #666; margin: 5px 0;"><strong>Address:</strong> {info['address']}</p>
            </div>

            <div style="
                background: linear-gradient(135deg, #d5f5e3, #abebc6);
                padding: 20px; border-radius: 15px; margin-bottom: 30px;
            ">
                <p style="color: #27ae60; font-size: 22px; font-weight: 700; margin: 0;">
                    Total: {int(self.cart.get_total())} EGP
                </p>
            </div>

            <p style="color: #999; font-size: 14px; margin-bottom: 25px;">
                <i class="fas fa-info-circle" style="margin-right: 5px;"></i>
                You will receive a confirmation email shortly
            </p>
        </div>
        ''')

        self.cart.clear_cart()
        self.refresh_header()

        put_buttons([{'label': ' Continue Shopping', 'value': 'home'}], 
                   onclick=[lambda: self.show_home()]).style('text-align: center; margin: 20px auto; display: block;')

        self.ui.render_footer()

def main():
    app = ShopController()
    app.start()

if __name__ == '__main__':
    start_server(main, port=5000, debug=True)
