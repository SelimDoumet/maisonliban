from flask import Blueprint, jsonify
from flask_login import current_user
from extensions import db
from models import Product
import pickle
import os

recommend = Blueprint('recommend', __name__)

MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'ml', 'recommendation_model.pkl')
_model = None

def load_model():
    global _model
    if _model is None:
        try:
            with open(MODEL_PATH, 'rb') as f:
                _model = pickle.load(f)
            print("[ML] Recommendation model loaded.")
        except FileNotFoundError:
            print("[ML] Model not found. Run python train_model.py first.")
            _model = {}
    return _model

def enrich(product_ids):
    results = []
    for pid in product_ids:
        p = db.session.get(Product, int(pid))
        if p:
            results.append({
                'product_id': p.id, 'name': p.name, 'category': p.category,
                'color': p.color, 'size': p.size, 'price': p.price, 'image': p.image
            })
    return results

def get_content_based(product_id, n=4):
    model = load_model()
    if not model:
        return []
    try:
        products_df = model['products_df']
        sim = model['content_similarity']
        matches = products_df[products_df['product_id'] == product_id]
        if matches.empty:
            return []
        idx = matches.index[0]
        scores = sorted(enumerate(sim[idx]), key=lambda x: x[1], reverse=True)
        scores = [s for s in scores if int(products_df.iloc[s[0]]['product_id']) != product_id]
        top_pids = [int(products_df.iloc[s[0]]['product_id']) for s in scores[:n]]
        return enrich(top_pids)
    except Exception as e:
        print(f"[ML] Content error: {e}")
        return []

def get_collaborative(user_id, n=4):
    model = load_model()
    if not model:
        return []
    try:
        predicted = model['predicted_ratings']
        rating_matrix = model['rating_matrix']
        idx = user_id % predicted.shape[0]
        user_ratings = predicted[idx]
        product_ids = list(rating_matrix.columns)
        scored = sorted(zip(product_ids, user_ratings), key=lambda x: x[1], reverse=True)
        top_pids = [int(pid) for pid, _ in scored[:n]]
        return enrich(top_pids)
    except Exception as e:
        print(f"[ML] Collab error: {e}")
        return []

def get_popular(n=4):
    model = load_model()
    if not model:
        return []
    try:
        interactions_df = model['interactions_df']
        popular = interactions_df.groupby('product_id')['rating'].mean().sort_values(ascending=False)
        top_pids = [int(pid) for pid in popular.index[:n]]
        return enrich(top_pids)
    except Exception as e:
        print(f"[ML] Popular error: {e}")
        return []

@recommend.route('/api/recommendations/similar/<int:product_id>')
def similar_products(product_id):
    return jsonify({'recommendations': get_content_based(product_id, 4), 'type': 'content-based'})

@recommend.route('/api/recommendations/for-you')
def for_you():
    if current_user.is_authenticated:
        return jsonify({'recommendations': get_collaborative(current_user.id, 4), 'type': 'collaborative'})
    return jsonify({'recommendations': get_popular(4), 'type': 'popular'})
