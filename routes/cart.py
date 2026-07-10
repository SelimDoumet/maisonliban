from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from extensions import db
from models import Product, Order, OrderItem
from sqlalchemy import select

cart = Blueprint('cart', __name__)

def get_cart():
    return session.get('cart', {})

def save_cart(c):
    session['cart'] = c
    session.modified = True

@cart.route('/cart')
def view_cart():
    c = get_cart()
    items = []
    total = 0
    for pid, qty in c.items():
        product = db.session.get(Product, int(pid))
        if product:
            subtotal = product.price * qty
            total += subtotal
            items.append({'product': product, 'qty': qty, 'subtotal': subtotal})
    delivery = 30 if items else 0
    grand_total = total + delivery
    return render_template('cart.html', items=items, total=total, delivery=delivery, grand_total=grand_total)

@cart.route('/cart/add/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        return 'Not found', 404
    qty = int(request.form.get('quantity', 1))
    c = get_cart()
    c[str(product_id)] = c.get(str(product_id), 0) + qty
    save_cart(c)
    flash(f'"{product.name}" added to cart.', 'success')
    return redirect(request.referrer or url_for('products.product_list'))

@cart.route('/cart/remove/<int:product_id>')
def remove_from_cart(product_id):
    c = get_cart()
    c.pop(str(product_id), None)
    save_cart(c)
    flash('Item removed.', 'info')
    return redirect(url_for('cart.view_cart'))

@cart.route('/cart/checkout', methods=['POST'])
@login_required
def checkout():
    c = get_cart()
    if not c:
        flash('Your cart is empty.', 'warning')
        return redirect(url_for('cart.view_cart'))
    total = 0
    order_items = []
    for pid, qty in c.items():
        product = db.session.get(Product, int(pid))
        if product and product.stock >= qty:
            total += product.price * qty
            order_items.append(OrderItem(product_id=product.id, quantity=qty, price_at_purchase=product.price))
            product.stock -= qty
        else:
            flash('An item is out of stock.', 'danger')
            return redirect(url_for('cart.view_cart'))
    grand_total = total + 30
    order = Order(user_id=current_user.id, total=grand_total, status='Confirmed')
    db.session.add(order)
    db.session.flush()
    for item in order_items:
        item.order_id = order.id
        db.session.add(item)
    db.session.commit()
    session.pop('cart', None)
    flash(f'Order #{order.id} placed! Total: ${grand_total:.2f}', 'success')
    return redirect(url_for('products.index'))
