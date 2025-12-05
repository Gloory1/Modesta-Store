from pywebio import start_server, config
from pywebio.output import put_html, put_buttons, put_row, put_markdown, clear, use_scope, popup, toast
from pywebio.session import run_js, set_env
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class Product:
    id: int
    name: str
    price: float
    category: str
    image_url: str

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

    def get_total(self) -> float:
        return sum(item.total_price for item in self.items)

    def get_count(self) -> int:
        return sum(item.quantity for item in self.items)

    def clear(self):
        self.items = []

PRODUCTS_DB = [
    Product(1, "Classic Abaya", 450, "Abayas", "https://placehold.co/200x250/2d3436/white?text=Classic+Abaya"),
    Product(2, "Butterfly Abaya", 520, "Abayas", "https://placehold.co/200x250/636e72/white?text=Butterfly+Abaya"),
    Product(3, "Silk Abaya", 480, "Abayas", "https://placehold.co/200x250/2d3436/white?text=Silk+Abaya"),
    Product(4, "Chiffon Khimar", 180, "Khimars", "https://placehold.co/200x250/b8a9c9/white?text=Chiffon+Khimar"),
    Product(5, "Crepe Khimar", 150, "Khimars", "https://placehold.co/200x250/d4a5d6/white?text=Crepe+Khimar"),
    Product(6, "Saudi Niqab", 120, "Niqabs", "https://placehold.co/200x250/2f4858/white?text=Saudi+Niqab"),
    Product(7, "Butterfly Niqab", 90, "Niqabs", "https://placehold.co/200x250/34495e/white?text=Butterfly+Niqab"),
    Product(8, "Hijab Pins Set", 30, "Accessories", "https://placehold.co/200x250/f8a5c2/white?text=Hijab+Pins"),
    Product(9, "Silk Headband", 50, "Accessories", "https://placehold.co/200x250/ff6b81/white?text=Headband"),
]

class UI:
    @staticmethod
    def load_resources():
        put_html("""
        <link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap" rel="stylesheet">
        <style>
            body, .pywebio {
                font-family: 'Tajawal', sans-serif !important;
                background: linear-gradient(135deg, #fff0f5 0%, #ffe4ec 50%, #fff5f8 100%) !important;
                min-height: 100vh;
                padding-top: 80px !important;
            }
            
            .markdown-body {
                font-family: 'Tajawal', sans-serif !important;
            }
        </style>
        """)
        
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
                
                .nav-btn {
                    background: rgba(255,255,255,0.25) !important;
                    border: 2px solid rgba(255,255,255,0.5) !important;
                    color: white !important;
                    padding: 10px 20px !important;
                    border-radius: 20px !important;
                    font-weight: 600 !important;
                    box-shadow: none !important;
                    backdrop-filter: blur(5px) !important;
                }
                
                .nav-btn:hover {
                    background: rgba(255,255,255,0.4) !important;
                    border-color: white !important;
                    transform: none !important;
                }
            `;
            document.head.appendChild(style);
        """)

    @staticmethod
    def render_header(cart_count: int, on_cart_click, on_home_click):
        with use_scope('header', clear=True):
            put_html("""
            <div id="sticky-header" style="
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 50%, #fad0c4 100%);
                padding: 15px 30px;
                box-shadow: 0 4px 25px rgba(255, 154, 158, 0.4);
                z-index: 1000;
                display: flex;
                justify-content: space-between;
                align-items: center;
            ">
                <div style="
                    font-size: 28px;
                    font-weight: 700;
                    color: white;
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.15);
                    letter-spacing: 2px;
                ">
                    Modesta
                </div>
                <div id="nav-buttons-container"></div>
            </div>
            """)
            
            put_row([
                put_buttons(['Home'], onclick=[lambda: on_home_click()]),
                put_buttons([f'Cart ({cart_count})'], onclick=[lambda: on_cart_click()])
            ], size='auto').style('''
                position: fixed;
                top: 15px;
                right: 30px;
                z-index: 1001;
                display: flex;
                gap: 10px;
            ''')

    @staticmethod
    def render_hero_section():
        put_html("""
        <div style="
            text-align: center;
            padding: 40px 20px;
        ">
            <h1 style="
                font-size: 48px;
                font-weight: 700;
                background: linear-gradient(135deg, #e84393, #a55eea);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                margin-bottom: 10px;
                text-shadow: none;
            ">Modesta Store</h1>
            
            <p style="
                font-size: 22px;
                color: #a55eea;
                font-weight: 500;
                margin-bottom: 10px;
            ">Where Modesty Meets Elegance</p>
            
            <div style="
                height: 4px;
                background: linear-gradient(90deg, transparent, #fecfef, #ff9a9e, #e84393, #ff9a9e, #fecfef, transparent);
                margin: 25px auto;
                max-width: 400px;
                border-radius: 2px;
            "></div>
        </div>
        """)

        put_html("""
        <div style="
            background: linear-gradient(135deg, #ffffff 0%, #fff9fc 100%);
            border-radius: 25px;
            padding: 35px 45px;
            max-width: 800px;
            margin: 10px auto 40px auto;
            box-shadow: 0 15px 50px rgba(232, 67, 147, 0.15);
            border-left: 6px solid #e84393;
            position: relative;
            overflow: hidden;
        ">
            <div style="
                position: absolute;
                top: -30px;
                left: 15px;
                font-size: 120px;
                color: rgba(232, 67, 147, 0.08);
                font-family: Georgia, serif;
                line-height: 1;
            ">"</div>
            
            <p style="
                font-size: 19px;
                line-height: 2;
                color: #5f27cd;
                font-weight: 500;
                position: relative;
                z-index: 1;
            ">
                O Prophet, tell your wives and your daughters and the women of the believers 
                to bring down over themselves [part] of their outer garments. That is more suitable 
                that they will be known and not be abused.
            </p>
            
            <p style="
                color: #e84393;
                font-size: 15px;
                margin-top: 20px;
                font-weight: 700;
                text-align: right;
            ">[Al-Ahzab: 59]</p>
        </div>
        """)

    @staticmethod
    def render_categories(categories: List[str], on_select):
        put_html("""
        <div style="
            text-align: center;
            padding: 20px;
        ">
            <h2 style="
                font-size: 28px;
                color: #5f27cd;
                margin-bottom: 30px;
                font-weight: 700;
            ">Shop by Category</h2>
        </div>
        """)

        btns = []
        for cat in categories:
            btns.append({'label': f'  {cat}  ', 'value': cat})

        put_buttons(btns, onclick=on_select).style('''
            display: flex; 
            justify-content: center; 
            flex-wrap: wrap; 
            gap: 20px;
            padding: 10px;
        ''')

    @staticmethod
    def render_products(products: List[Product], on_add_to_cart, on_back):
        put_html("""
        <div style="text-align: center; margin: 30px 0;">
        """)
        put_buttons(['Back to Categories'], onclick=[lambda: on_back()]).style('''
            display: inline-flex;
            align-items: center;
            gap: 8px;
        ''')
        put_html("</div>")

        if not products:
            put_html('''
            <p style="
                text-align: center; 
                color: #a55eea; 
                font-size: 18px;
                padding: 40px;
            ">No products found in this category.</p>
            ''')
            return

        put_html('<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 30px; padding: 30px; max-width: 1200px; margin: 0 auto;">')

        for p in products:
            put_html(f"""
            <div style="
                background: white;
                border-radius: 25px;
                overflow: hidden;
                box-shadow: 0 10px 40px rgba(232, 67, 147, 0.12);
                transition: all 0.4s ease;
                border: 2px solid rgba(232, 67, 147, 0.1);
            ">
                <img src="{p.image_url}" alt="{p.name}" style="
                    width: 100%;
                    height: 220px;
                    object-fit: cover;
                    border-bottom: 4px solid #fecfef;
                ">
                <div style="
                    padding: 25px;
                    text-align: center;
                    background: linear-gradient(180deg, #fff 0%, #fff9fc 100%);
                ">
                    <h3 style="
                        font-size: 22px;
                        font-weight: 700;
                        color: #2d3436;
                        margin-bottom: 12px;
                    ">{p.name}</h3>
                    <p style="
                        font-size: 26px;
                        font-weight: 700;
                        color: #e84393;
                        margin-bottom: 20px;
                    ">{p.price} EGP</p>
                </div>
            </div>
            """)
            put_buttons(['Add to Cart'], onclick=[lambda p=p: on_add_to_cart(p)]).style('''
                display: block;
                margin: -15px 20px 20px 20px;
                text-align: center;
            ''')

        put_html('</div>')

    @staticmethod
    def render_cart_modal(cart: Cart, on_close):
        content = []
        if not cart.items:
            content.append(put_html('''
            <div style="
                text-align: center;
                padding: 50px 30px;
                color: #a55eea;
            ">
                <p style="font-size: 20px; font-weight: 600;">Your cart is empty</p>
                <p style="font-size: 16px; color: #999; margin-top: 10px;">Start shopping to add items!</p>
            </div>
            '''))
        else:
            content.append(put_html('''
            <h2 style="
                font-size: 26px;
                color: #e84393;
                font-weight: 700;
                margin-bottom: 25px;
                text-align: center;
            ">Your Shopping Cart</h2>
            '''))
            
            rows = [['Product', 'Price', 'Qty', 'Total']]
            for item in cart.items:
                rows.append([
                    item.product.name, 
                    f"{item.product.price} EGP", 
                    item.quantity, 
                    f"{item.total_price} EGP"
                ])

            from pywebio.output import put_table
            content.append(put_table(rows))
            
            content.append(put_html(f'''
            <div style="
                font-size: 24px;
                color: #27ae60;
                font-weight: 700;
                text-align: right;
                margin-top: 25px;
                padding: 20px;
                background: linear-gradient(135deg, #d5f5e3 0%, #abebc6 100%);
                border-radius: 15px;
            ">Total: {cart.get_total()} EGP</div>
            '''))
            
            content.append(put_buttons(['Proceed to Checkout'], onclick=lambda: toast("Checkout feature coming soon!", color='info')))

        popup('Shopping Cart', content)

class ShopController:
    def __init__(self):
        self.cart = Cart()
        self.ui = UI()
        self.categories = list(set(p.category for p in PRODUCTS_DB))

    def start(self):
        set_env(title="Modesta Store")
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
        self.refresh_header()
        self.ui.render_hero_section()
        self.ui.render_categories(self.categories, self.show_category_page)

    def show_category_page(self, category_name):
        clear()
        self.refresh_header()

        filtered_products = [p for p in PRODUCTS_DB if p.category == category_name]

        put_html(f'''
        <h1 style="
            font-size: 36px;
            color: #5f27cd;
            text-align: center;
            margin: 30px 0 10px 0;
            font-weight: 700;
        ">{category_name}</h1>
        
        <div style="
            height: 4px;
            background: linear-gradient(90deg, transparent, #fecfef, #e84393, #fecfef, transparent);
            margin: 15px auto 30px auto;
            max-width: 200px;
            border-radius: 2px;
        "></div>
        ''')

        self.ui.render_products(
            products=filtered_products,
            on_add_to_cart=self.add_to_cart,
            on_back=self.show_home
        )

    def add_to_cart(self, product: Product):
        self.cart.add_product(product)
        toast(f"Added {product.name} to cart!", color='success')
        self.refresh_header()

    def show_cart(self):
        self.ui.render_cart_modal(self.cart, on_close=None)

def main():
    app = ShopController()
    app.start()

if __name__ == '__main__':
    start_server(main, port=5000, debug=True)
