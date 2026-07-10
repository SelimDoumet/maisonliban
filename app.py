from flask import Flask
import os
import secrets
from dotenv import load_dotenv
from extensions import db, bcrypt, login_manager

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///furniture.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

from routes.auth import auth
from routes.products import products
from routes.ai_chat import ai_chat
from routes.admin import admin
from routes.cart import cart
from routes.recommend import recommend

app.register_blueprint(auth)
app.register_blueprint(products)
app.register_blueprint(ai_chat)
app.register_blueprint(admin)
app.register_blueprint(cart)
app.register_blueprint(recommend)

with app.app_context():
    from models import User, Product, Order, OrderItem
    db.create_all()
    from sqlalchemy import text
    if db.session.execute(text('SELECT COUNT(*) FROM product')).scalar() == 0:
        items = [
            Product(name='Nordic 3-Seat Sofa', category='Living Room', color='Gray', size='Large', price=649.00, description='Scandinavian 3-seat sofa in soft gray fabric with solid oak legs. Deep seats for maximum comfort.', stock=12, image='https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=800&q=80'),
            Product(name='Velvet 2-Seat Sofa', category='Living Room', color='Beige', size='Medium', price=480.00, description='Luxurious cream velvet 2-seater sofa with gold-tipped tapered legs. A centrepiece for elegant interiors.', stock=7, image='https://images.unsplash.com/photo-1493663284031-b7e3aefcae8e?w=800&q=80'),
            Product(name='Leather Armchair', category='Living Room', color='Brown', size='Small', price=199.00, description='Classic brown leather armchair with solid oak legs. Timeless and durable.', stock=20, image='https://images.unsplash.com/photo-1506439773649-6e0eb8cfb237?w=800&q=80'),
            Product(name='Rattan Lounge Chair', category='Living Room', color='Brown', size='Small', price=245.00, description='Handwoven natural rattan lounge chair with cream cushioned seat. Bohemian and airy.', stock=9, image='https://images.unsplash.com/photo-1531835551805-16d864c8d311?w=800&q=80'),
            Product(name='Marble Coffee Table', category='Living Room', color='White', size='Medium', price=320.00, description='Round white marble-top coffee table with brushed brass legs. Elegant and functional.', stock=6, image='https://images.unsplash.com/photo-1616486338812-3dadae4b4ace?w=800&q=80'),
            Product(name='Open Bookshelf', category='Living Room', color='White', size='Large', price=210.00, description='5-tier open bookshelf in white finish, 160 cm tall. Holds books, plants, and decor.', stock=11, image='https://images.unsplash.com/photo-1588854337236-6889d631faa8?w=800&q=80'),
            Product(name='Arc Floor Lamp', category='Living Room', color='Black', size='Large', price=159.00, description='Modern black arc floor lamp with 180-degree adjustable head. Creates warm ambient light.', stock=14, image='https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=800&q=80'),
            Product(name='Levant Queen Bed', category='Bedroom', color='Beige', size='Large', price=520.00, description='Queen-size bed frame upholstered in warm beige linen with a padded headboard.', stock=9, image='https://images.unsplash.com/photo-1588046130717-0eb0c9a3ba15?w=800&q=80'),
            Product(name='King Tufted Bed', category='Bedroom', color='Gray', size='Large', price=720.00, description='King-size bed with deep button-tufted headboard in soft gray fabric. Hotel-quality comfort.', stock=4, image='https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=800&q=80'),
            Product(name='2-Door Wardrobe', category='Bedroom', color='White', size='Large', price=439.00, description='White 2-door wardrobe with full-length mirror and soft-close hinges, 180 cm tall.', stock=6, image='https://images.unsplash.com/photo-1558997519-83ea9252edf8?w=800&q=80'),
            Product(name='Bedside Table Set x2', category='Bedroom', color='Brown', size='Small', price=129.00, description='Set of 2 solid walnut bedside tables each with one storage drawer.', stock=15, image='https://images.unsplash.com/photo-1578683010236-d716f9a3f461?w=800&q=80'),
            Product(name='5-Drawer Dresser', category='Bedroom', color='White', size='Medium', price=290.00, description='5-drawer dresser in white lacquer with chrome handles. Smooth gliding drawers.', stock=8, image='https://images.unsplash.com/photo-1595428774223-ef52624120d2?w=800&q=80'),
            Product(name='Vanity Desk with Mirror', category='Bedroom', color='White', size='Medium', price=345.00, description='White vanity desk with large mirror and single storage drawer. Perfect for a morning routine.', stock=5, image='https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=800&q=80'),
            Product(name='Walnut Dining Table', category='Dining', color='Brown', size='Medium', price=289.00, description='Solid walnut dining table, 120x75 cm. Seats 4. Beautiful natural wood grain.', stock=8, image='https://images.unsplash.com/photo-1567538096630-e0c55bd6374c?w=800&q=80'),
            Product(name='Oak Dining Table 6-Seat', category='Dining', color='Brown', size='Large', price=540.00, description='Extendable solid oak dining table. Seats 6 normally, extends to seat 8.', stock=5, image='https://images.unsplash.com/photo-1519947486511-46149fa0a254?w=800&q=80'),
            Product(name='Marble Dining Table', category='Dining', color='White', size='Large', price=890.00, description='Stunning white Carrara marble top dining table with matte black steel base. Seats 6.', stock=3, image='https://images.unsplash.com/photo-1617806118233-18e1de247200?w=800&q=80'),
            Product(name='Dining Chair Set x4', category='Dining', color='Beige', size='Small', price=320.00, description='Set of 4 upholstered dining chairs in warm beige with solid beech wood legs.', stock=10, image='https://images.unsplash.com/photo-1551298370-9d3d53740c72?w=800&q=80'),
            Product(name='Bar Stool Set x2', category='Dining', color='Black', size='Small', price=180.00, description='Set of 2 adjustable black bar stools with footrest and faux leather padded seat.', stock=12, image='https://images.unsplash.com/photo-1503602642458-232111445657?w=800&q=80'),
            Product(name='Oak Sideboard', category='Dining', color='Brown', size='Large', price=420.00, description='3-door solid oak sideboard with brass handles. Ideal for tableware and linens.', stock=6, image='https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=800&q=80'),
            Product(name='Executive Office Desk', category='Office', color='Black', size='Large', price=349.00, description='Large black executive desk with built-in cable management, 140 cm wide.', stock=15, image='https://images.unsplash.com/photo-1518455027359-f3f8164ba6bd?w=800&q=80'),
            Product(name='Ergonomic Office Chair', category='Office', color='Black', size='Medium', price=280.00, description='Full ergonomic office chair with lumbar support and adjustable armrests.', stock=18, image='https://images.unsplash.com/photo-1541558869434-2840d308329a?w=800&q=80'),
            Product(name='Compact Study Desk', category='Office', color='White', size='Small', price=189.00, description='Space-saving white study desk, 100 cm wide. Perfect for apartments and students.', stock=11, image='https://images.unsplash.com/photo-1593642632559-0c6d3fc62b89?w=800&q=80'),
            Product(name='Filing Cabinet', category='Office', color='Gray', size='Small', price=145.00, description='3-drawer gray steel filing cabinet with key lock for secure document storage.', stock=9, image='https://images.unsplash.com/photo-1573165231977-3f0e27806045?w=800&q=80'),
            Product(name='Bookcase with Glass Doors', category='Office', color='Brown', size='Large', price=390.00, description='Tall brown wooden bookcase with glass doors, 200 cm. Protects books in style.', stock=4, image='https://images.unsplash.com/photo-1594620302200-9a762244a156?w=800&q=80'),
            Product(name='Cedar Outdoor Dining Set', category='Outdoor', color='Brown', size='Large', price=780.00, description='4-seat outdoor cedar wood dining set. Treated for weather resistance. Table and 4 chairs.', stock=4, image='https://images.unsplash.com/photo-1600585152220-90363fe7e115?w=800&q=80'),
            Product(name='Rattan Garden Sofa', category='Outdoor', color='Gray', size='Large', price=620.00, description='3-seat gray rattan garden sofa with thick weather-proof cushions.', stock=5, image='https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?w=800&q=80'),
            Product(name='Sun Lounger Set x2', category='Outdoor', color='Beige', size='Large', price=340.00, description='Set of 2 adjustable beige cushioned sun loungers with rust-proof aluminum frame.', stock=7, image='https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80'),
            Product(name='Folding Bistro Table', category='Outdoor', color='Black', size='Small', price=95.00, description='Compact black powder-coated steel bistro table. Folds flat for easy storage.', stock=16, image='https://images.unsplash.com/photo-1567016376408-0226e4d0c1ea?w=800&q=80'),
            Product(name='Teak Garden Bench', category='Outdoor', color='Brown', size='Medium', price=210.00, description='Classic 2-seat teak garden bench. Naturally weather-resistant, no treatment needed.', stock=8, image='https://images.unsplash.com/photo-1564540574859-0dfb63985953?w=800&q=80'),
            Product(name='Outdoor Bar Cart', category='Outdoor', color='Black', size='Small', price=175.00, description='Black powder-coated rolling bar cart with 2 tiers. Perfect for terrace entertaining.', stock=10, image='https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?w=800&q=80'),
        ]
        for item in items:
            db.session.add(item)
    admin_email = os.environ.get('ADMIN_EMAIL', 'admin@maisonliban.com')
    admin_password = os.environ.get('ADMIN_PASSWORD', secrets.token_urlsafe(12))
    if db.session.execute(text("SELECT COUNT(*) FROM user WHERE email=:email"), {"email": admin_email}).scalar() == 0:
        admin_user = User(
            name='Admin',
            email=admin_email,
            password=bcrypt.generate_password_hash(admin_password).decode('utf-8'),
            is_admin=True
        )
        db.session.add(admin_user)
        db.session.commit()
        if 'ADMIN_PASSWORD' not in os.environ:
            print(f"[MaisonLiban] Generated admin account -> {admin_email} / {admin_password}")
            print("[MaisonLiban] Set ADMIN_EMAIL and ADMIN_PASSWORD in .env to control this yourself.")
    else:
        db.session.commit()

if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(debug=debug_mode)
