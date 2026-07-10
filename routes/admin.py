from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from functools import wraps
from extensions import db
from models import Product, User, Order
from sqlalchemy import select, func

admin = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required.', 'danger')
            return redirect(url_for('products.index'))
        return f(*args, **kwargs)
    return decorated

@admin.route('/')
@login_required
@admin_required
def dashboard():
    total_products = db.session.execute(select(func.count(Product.id))).scalar()
    total_users = db.session.execute(select(func.count(User.id)).where(User.is_admin == False)).scalar()
    total_orders = db.session.execute(select(func.count(Order.id))).scalar()
    revenue = db.session.execute(select(func.sum(Order.total))).scalar() or 0
    recent_orders = db.session.execute(select(Order).order_by(Order.created_at.desc()).limit(10)).scalars().all()
    return render_template('admin/dashboard.html', total_products=total_products,
                           total_users=total_users, total_orders=total_orders,
                           revenue=revenue, recent_orders=recent_orders)

@admin.route('/products')
@login_required
@admin_required
def products():
    items = db.session.execute(select(Product).order_by(Product.created_at.desc())).scalars().all()
    return render_template('admin/products.html', items=items)

@admin.route('/products/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        category = request.form.get('category', '')
        color = request.form.get('color', '')
        size = request.form.get('size', '')
        price = float(request.form.get('price', 0))
        stock = int(request.form.get('stock', 0))
        description = request.form.get('description', '')
        image = request.form.get('image', '').strip()
        if not name or not category or price <= 0:
            flash('Name, category, and price are required.', 'danger')
            return render_template('admin/product_form.html', product=None)
        db.session.add(Product(name=name, category=category, color=color, size=size,
                               price=price, stock=stock, description=description, image=image))
        db.session.commit()
        flash(f'Product "{name}" added.', 'success')
        return redirect(url_for('admin.products'))
    return render_template('admin/product_form.html', product=None)

@admin.route('/products/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        return 'Not found', 404
    if request.method == 'POST':
        product.name = request.form.get('name', '').strip()
        product.category = request.form.get('category', '')
        product.color = request.form.get('color', '')
        product.size = request.form.get('size', '')
        product.price = float(request.form.get('price', 0))
        product.stock = int(request.form.get('stock', 0))
        product.description = request.form.get('description', '')
        product.image = request.form.get('image', '').strip()
        db.session.commit()
        flash('Product updated.', 'success')
        return redirect(url_for('admin.products'))
    return render_template('admin/product_form.html', product=product)

@admin.route('/products/delete/<int:product_id>', methods=['POST'])
@login_required
@admin_required
def delete_product(product_id):
    product = db.session.get(Product, product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
    flash('Product deleted.', 'info')
    return redirect(url_for('admin.products'))

@admin.route('/users')
@login_required
@admin_required
def users():
    all_users = db.session.execute(select(User).where(User.is_admin == False).order_by(User.created_at.desc())).scalars().all()
    return render_template('admin/users.html', users=all_users)

@admin.route('/orders')
@login_required
@admin_required
def orders():
    all_orders = db.session.execute(select(Order).order_by(Order.created_at.desc())).scalars().all()
    return render_template('admin/orders.html', orders=all_orders)
