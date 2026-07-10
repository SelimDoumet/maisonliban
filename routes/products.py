from flask import Blueprint, render_template, request
from extensions import db
from models import Product
from sqlalchemy import select, or_

products = Blueprint('products', __name__)

CATEGORIES = ['Living Room', 'Bedroom', 'Dining', 'Office', 'Outdoor']
COLORS = ['White', 'Black', 'Brown', 'Beige', 'Gray']
SIZES = ['Small', 'Medium', 'Large']

@products.route('/')
def index():
    stmt = select(Product).order_by(Product.created_at.desc()).limit(8)
    featured = db.session.execute(stmt).scalars().all()
    return render_template('index.html', featured=featured)

@products.route('/products')
def product_list():
    q = request.args.get('q', '').strip()
    category = request.args.get('category', '')
    color = request.args.get('color', '')
    size = request.args.get('size', '')
    min_price = request.args.get('min_price', 0, type=float)
    max_price = request.args.get('max_price', 99999, type=float)
    stmt = select(Product)
    if q:
        stmt = stmt.where(or_(Product.name.ilike(f'%{q}%'), Product.description.ilike(f'%{q}%')))
    if category:
        stmt = stmt.where(Product.category == category)
    if color:
        stmt = stmt.where(Product.color == color)
    if size:
        stmt = stmt.where(Product.size == size)
    stmt = stmt.where(Product.price >= min_price, Product.price <= max_price).order_by(Product.name)
    items = db.session.execute(stmt).scalars().all()
    return render_template('products.html', items=items, categories=CATEGORIES,
                           colors=COLORS, sizes=SIZES,
                           selected={'q': q, 'category': category, 'color': color,
                                     'size': size, 'min_price': min_price, 'max_price': max_price})

@products.route('/products/<int:product_id>')
def product_detail(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        return 'Not found', 404
    related = db.session.execute(
        select(Product).where(Product.category == product.category, Product.id != product_id).limit(4)
    ).scalars().all()
    return render_template('product_detail.html', product=product, related=related)

@products.route('/about')
def about():
    return render_template('about.html')
