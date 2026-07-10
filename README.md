# MaisonLiban — AI-Powered Furniture E-Commerce Platform

A full-stack e-commerce web application for a furniture retailer, built with Flask and powered by a hybrid machine learning recommendation engine and an LLM shopping assistant. Built as a course project (Web Applications, Dr. Anthony Tannoury, USJ) covering data science, data analysis, and data management end-to-end — from schema design to a working ML pipeline serving live predictions.

## Features

- **Product catalogue** across 5 categories (Living Room, Bedroom, Dining, Office, Outdoor) with filtering by category, color, and size
- **ML-powered recommendations**, two models running in production:
  - *Content-based filtering*: cosine similarity over encoded product features (category, color, size, price) to power "similar products"
  - *Collaborative filtering*: truncated SVD (matrix factorization) over a synthetic user-interaction dataset (500 users, ~8,000 interactions) to power personalized "for you" recommendations, falling back to popularity ranking for anonymous users
- **AI shopping assistant** — an LLM chat widget (Llama 3.3 70B via Groq) that gives interior-design style suggestions and steers customers toward relevant categories
- **Authentication** with hashed passwords (bcrypt) and session-based login (Flask-Login)
- **Shopping cart and checkout flow**
- **Admin panel** for managing products, orders, and users, gated behind an admin role
- **Responsive UI** in vanilla HTML/CSS/JS (no frontend framework)

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask, Flask-SQLAlchemy, Flask-Login, Flask-Bcrypt |
| ML | scikit-learn (TruncatedSVD, cosine similarity, LabelEncoder), pandas, numpy |
| AI Assistant | Groq API (Llama 3.3 70B) |
| Database | SQLite |
| Frontend | HTML, CSS, JavaScript |

## Architecture

```
app.py                  # App factory, config, DB seeding
extensions.py           # Shared Flask extension instances (db, bcrypt, login_manager)
models.py               # SQLAlchemy models: User, Product, Order, OrderItem
train_model.py          # Offline training script for the recommendation engine
routes/
  auth.py               # Signup / login / logout
  products.py            # Catalogue browsing, filtering, product detail
  cart.py                # Cart and checkout
  recommend.py           # Recommendation API (serves the trained model)
  ai_chat.py             # LLM shopping assistant endpoint
  admin.py               # Admin dashboard, product/order/user management
templates/               # Jinja2 templates (customer-facing + admin/)
static/                  # CSS and JS
```

The recommendation engine is trained **offline** (`train_model.py`) and serialized to `ml/recommendation_model.pkl`, which Flask loads at request time — the web app never retrains on the fly, keeping request latency low while still serving personalized, model-backed recommendations.

## Setup

1. **Clone and install dependencies**
   ```bash
   git clone https://github.com/<your-username>/maisonliban.git
   cd maisonliban
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```
   Fill in `.env` with your own `SECRET_KEY`, admin credentials, and a free [Groq API key](https://console.groq.com) for the AI assistant.

3. **Train the recommendation model** (run once)
   ```bash
   python train_model.py
   ```

4. **Run the app**
   ```bash
   python app.py
   ```
   Visit `http://127.0.0.1:5000`. An admin account is created automatically on first run using the credentials from your `.env` file.

## Notes

- The user-interaction dataset used to train the collaborative filtering model is synthetic (generated in `train_model.py` with a fixed random seed), simulating realistic preference-driven purchasing behavior across category, color, and budget.
- Without a `GROQ_API_KEY` set, the site still runs fully — the AI assistant simply returns a message indicating it needs to be configured.

## Author

Selim Doumet — BSc Mathematics, Data Science option, Université Saint-Joseph de Beyrouth
