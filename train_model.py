"""
MaisonLiban — ML Recommendation Engine
=======================================
This script:
1. Generates a realistic synthetic dataset of user-product interactions
2. Trains a hybrid recommendation model (collaborative + content-based)
3. Saves the model and data as .pkl files for use in Flask

Run this ONCE to generate the model:
    python train_model.py

The model is then loaded automatically by Flask on startup.
"""

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import LabelEncoder, MinMaxScaler
from sklearn.decomposition import TruncatedSVD
import pickle
import os
import random

random.seed(42)
np.random.seed(42)

print("=" * 60)
print("MaisonLiban Recommendation Engine — Training")
print("=" * 60)

# ─────────────────────────────────────────────────────────────
# STEP 1: Define the product catalogue (mirrors your database)
# ─────────────────────────────────────────────────────────────

products = [
    {"product_id": 1,  "name": "Nordic 3-Seat Sofa",      "category": "Living Room", "color": "Gray",  "size": "Large",  "price": 649},
    {"product_id": 2,  "name": "Velvet 2-Seat Sofa",      "category": "Living Room", "color": "Beige", "size": "Medium", "price": 480},
    {"product_id": 3,  "name": "Leather Armchair",        "category": "Living Room", "color": "Brown", "size": "Small",  "price": 199},
    {"product_id": 4,  "name": "Rattan Lounge Chair",     "category": "Living Room", "color": "Brown", "size": "Small",  "price": 245},
    {"product_id": 5,  "name": "Marble Coffee Table",     "category": "Living Room", "color": "White", "size": "Medium", "price": 320},
    {"product_id": 6,  "name": "Open Bookshelf",          "category": "Living Room", "color": "White", "size": "Large",  "price": 210},
    {"product_id": 7,  "name": "Arc Floor Lamp",          "category": "Living Room", "color": "Black", "size": "Large",  "price": 159},
    {"product_id": 8,  "name": "Levant Queen Bed",        "category": "Bedroom",     "color": "Beige", "size": "Large",  "price": 520},
    {"product_id": 9,  "name": "King Tufted Bed",         "category": "Bedroom",     "color": "Gray",  "size": "Large",  "price": 720},
    {"product_id": 10, "name": "2-Door Wardrobe",         "category": "Bedroom",     "color": "White", "size": "Large",  "price": 439},
    {"product_id": 11, "name": "Bedside Table Set x2",   "category": "Bedroom",     "color": "Brown", "size": "Small",  "price": 129},
    {"product_id": 12, "name": "5-Drawer Dresser",        "category": "Bedroom",     "color": "White", "size": "Medium", "price": 290},
    {"product_id": 13, "name": "Vanity Desk with Mirror", "category": "Bedroom",     "color": "White", "size": "Medium", "price": 345},
    {"product_id": 14, "name": "Walnut Dining Table",     "category": "Dining",      "color": "Brown", "size": "Medium", "price": 289},
    {"product_id": 15, "name": "Oak Dining Table 6-Seat", "category": "Dining",      "color": "Brown", "size": "Large",  "price": 540},
    {"product_id": 16, "name": "Marble Dining Table",     "category": "Dining",      "color": "White", "size": "Large",  "price": 890},
    {"product_id": 17, "name": "Dining Chair Set x4",     "category": "Dining",      "color": "Beige", "size": "Small",  "price": 320},
    {"product_id": 18, "name": "Bar Stool Set x2",        "category": "Dining",      "color": "Black", "size": "Small",  "price": 180},
    {"product_id": 19, "name": "Oak Sideboard",           "category": "Dining",      "color": "Brown", "size": "Large",  "price": 420},
    {"product_id": 20, "name": "Executive Office Desk",   "category": "Office",      "color": "Black", "size": "Large",  "price": 349},
    {"product_id": 21, "name": "Ergonomic Office Chair",  "category": "Office",      "color": "Black", "size": "Medium", "price": 280},
    {"product_id": 22, "name": "Compact Study Desk",      "category": "Office",      "color": "White", "size": "Small",  "price": 189},
    {"product_id": 23, "name": "Filing Cabinet",          "category": "Office",      "color": "Gray",  "size": "Small",  "price": 145},
    {"product_id": 24, "name": "Bookcase with Glass Doors","category": "Office",     "color": "Brown", "size": "Large",  "price": 390},
    {"product_id": 25, "name": "Cedar Outdoor Dining Set","category": "Outdoor",     "color": "Brown", "size": "Large",  "price": 780},
    {"product_id": 26, "name": "Rattan Garden Sofa",      "category": "Outdoor",     "color": "Gray",  "size": "Large",  "price": 620},
    {"product_id": 27, "name": "Sun Lounger Set x2",      "category": "Outdoor",     "color": "Beige", "size": "Large",  "price": 340},
    {"product_id": 28, "name": "Folding Bistro Table",    "category": "Outdoor",     "color": "Black", "size": "Small",  "price": 95},
    {"product_id": 29, "name": "Teak Garden Bench",       "category": "Outdoor",     "color": "Brown", "size": "Medium", "price": 210},
    {"product_id": 30, "name": "Outdoor Bar Cart",        "category": "Outdoor",     "color": "Black", "size": "Small",  "price": 175},
]

products_df = pd.DataFrame(products)
print(f"\n[1/5] Product catalogue loaded: {len(products_df)} products")

# ─────────────────────────────────────────────────────────────
# STEP 2: Generate synthetic user interaction dataset
# ─────────────────────────────────────────────────────────────
# We simulate 500 users with realistic purchasing patterns.
# Users have preferences: some prefer Living Room, some prefer Bedroom, etc.
# Ratings: 1-5 stars (implicit from interaction type)

NUM_USERS = 500
NUM_INTERACTIONS = 8000

categories = ["Living Room", "Bedroom", "Dining", "Office", "Outdoor"]
colors = ["Gray", "Beige", "Brown", "White", "Black"]

# Assign each user a primary category and color preference
user_profiles = []
for uid in range(1, NUM_USERS + 1):
    user_profiles.append({
        "user_id": uid,
        "preferred_category": random.choice(categories),
        "preferred_color": random.choice(colors),
        "budget": random.choice(["low", "medium", "high"])
    })

user_profiles_df = pd.DataFrame(user_profiles)

interactions = []
for _ in range(NUM_INTERACTIONS):
    user = random.choice(user_profiles)
    uid = user["user_id"]
    pref_cat = user["preferred_category"]
    pref_color = user["preferred_color"]
    budget = user["budget"]

    # 60% chance user picks from preferred category (realistic behavior)
    if random.random() < 0.60:
        candidates = products_df[products_df["category"] == pref_cat]
    else:
        candidates = products_df

    if len(candidates) == 0:
        candidates = products_df

    product = candidates.sample(1).iloc[0]
    pid = product["product_id"]

    # Rating logic: higher if matches preferences
    base_rating = random.uniform(2.5, 4.0)
    if product["category"] == pref_cat:
        base_rating += 0.8
    if product["color"] == pref_color:
        base_rating += 0.4
    if budget == "low" and product["price"] < 250:
        base_rating += 0.3
    elif budget == "medium" and 200 < product["price"] < 600:
        base_rating += 0.3
    elif budget == "high" and product["price"] > 500:
        base_rating += 0.3

    rating = min(5.0, round(base_rating, 1))

    interactions.append({
        "user_id": uid,
        "product_id": int(pid),
        "rating": rating,
        "category": product["category"],
        "color": product["color"],
        "price": product["price"]
    })

interactions_df = pd.DataFrame(interactions).drop_duplicates(subset=["user_id", "product_id"])
print(f"[2/5] Synthetic dataset generated: {len(interactions_df)} interactions from {NUM_USERS} users")

# ─────────────────────────────────────────────────────────────
# STEP 3: Build Content-Based Feature Matrix
# ─────────────────────────────────────────────────────────────

cat_encoder = LabelEncoder()
color_encoder = LabelEncoder()
size_encoder = LabelEncoder()
scaler = MinMaxScaler()

products_df["cat_encoded"] = cat_encoder.fit_transform(products_df["category"])
products_df["color_encoded"] = color_encoder.fit_transform(products_df["color"])
products_df["size_encoded"] = size_encoder.fit_transform(products_df["size"])
products_df["price_scaled"] = scaler.fit_transform(products_df[["price"]])

feature_matrix = products_df[["cat_encoded", "color_encoded", "size_encoded", "price_scaled"]].values
content_similarity = cosine_similarity(feature_matrix)

print(f"[3/5] Content-based similarity matrix built: {content_similarity.shape}")

# ─────────────────────────────────────────────────────────────
# STEP 4: Collaborative Filtering with SVD
# ─────────────────────────────────────────────────────────────

# Build user-product rating matrix
rating_matrix = interactions_df.pivot_table(
    index="user_id", columns="product_id", values="rating", fill_value=0
)

# Ensure all 30 products are columns
for pid in range(1, 31):
    if pid not in rating_matrix.columns:
        rating_matrix[pid] = 0
rating_matrix = rating_matrix[sorted(rating_matrix.columns)]

# Apply SVD for dimensionality reduction (collaborative filtering)
svd = TruncatedSVD(n_components=15, random_state=42)
user_factors = svd.fit_transform(rating_matrix)
item_factors = svd.components_.T

# Reconstruct predicted ratings matrix
predicted_ratings = np.dot(user_factors, svd.components_)

print(f"[4/5] Collaborative filtering model trained (SVD, {svd.n_components} components)")
print(f"      Explained variance ratio: {svd.explained_variance_ratio_.sum():.3f}")

# ─────────────────────────────────────────────────────────────
# STEP 5: Save everything as .pkl
# ─────────────────────────────────────────────────────────────

model_data = {
    "products_df": products_df,
    "content_similarity": content_similarity,
    "rating_matrix": rating_matrix,
    "svd_model": svd,
    "user_factors": user_factors,
    "predicted_ratings": predicted_ratings,
    "cat_encoder": cat_encoder,
    "color_encoder": color_encoder,
    "size_encoder": size_encoder,
    "scaler": scaler,
    "interactions_df": interactions_df,
    "num_users": NUM_USERS,
}

os.makedirs("ml", exist_ok=True)
with open("ml/recommendation_model.pkl", "wb") as f:
    pickle.dump(model_data, f)

interactions_df.to_csv("ml/interactions_dataset.csv", index=False)
products_df.to_csv("ml/products_dataset.csv", index=False)

print(f"[5/5] Model saved to ml/recommendation_model.pkl")
print(f"      Dataset saved to ml/interactions_dataset.csv")
print(f"      Products saved to ml/products_dataset.csv")

# ─────────────────────────────────────────────────────────────
# QUICK TEST: show sample recommendations
# ─────────────────────────────────────────────────────────────

def get_content_based_recommendations(product_id, n=4):
    """Get products similar to a given product based on features."""
    idx = products_df[products_df["product_id"] == product_id].index[0]
    sim_scores = list(enumerate(content_similarity[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = [s for s in sim_scores if products_df.iloc[s[0]]["product_id"] != product_id]
    top_indices = [s[0] for s in sim_scores[:n]]
    return products_df.iloc[top_indices][["product_id", "name", "category", "price"]].to_dict("records")

print("\n--- Sample: Products similar to 'Nordic 3-Seat Sofa' ---")
recs = get_content_based_recommendations(1, 4)
for r in recs:
    print(f"  -> [{r['product_id']}] {r['name']} ({r['category']}, ${r['price']})")

print("\n=== Training complete! Run 'python app.py' to start the website. ===\n")
