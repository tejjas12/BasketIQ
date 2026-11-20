
from pathlib import Path
import os
import ast
import re

import pandas as pd
from flask import Flask, render_template, request, jsonify


# =========================================================
# BASKET IQ - CONFIGURATION
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data" / "processed"

RULES_PATH = DATA_DIR / "association_rules.csv"
ITEMSETS_PATH = DATA_DIR / "frequent_itemsets.csv"
BASKET_PATH = DATA_DIR / "basket_onehot.csv"

app = Flask(__name__)


# =========================================================
# DATA LOADING
# =========================================================

def load_csv(path):
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")
    return pd.read_csv(path)


rules_df = load_csv(RULES_PATH)
itemsets_df = load_csv(ITEMSETS_PATH)
basket_df = load_csv(BASKET_PATH)


# =========================================================
# DATASET INFORMATION
# =========================================================

products = sorted([
    str(col)
    for col in basket_df.columns
    if str(col).strip().lower() != "transactionid"
])

total_transactions = len(basket_df)
total_products = len(products)
total_itemsets = len(itemsets_df)
total_rules = len(rules_df)

product_lookup = {
    product.strip().lower(): product
    for product in products
}


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def safe_float(value, default=0.0):
    try:
        if pd.isna(value):
            return default
        return float(value)
    except (ValueError, TypeError):
        return default


def parse_products(value):
    """Convert a CSV itemset representation into a normalized set."""

    if isinstance(value, (set, frozenset, list, tuple)):
        return {
            str(item).strip().lower()
            for item in value
            if str(item).strip()
        }

    if value is None:
        return set()

    if isinstance(value, float) and pd.isna(value):
        return set()

    text = str(value).strip()

    if not text or text.lower() in {
        "frozenset()", "set()", "nan", "none"
    }:
        return set()

    match = re.search(r"\{(.*?)\}", text)

    if match:
        contents = match.group(1)

        try:
            parsed = ast.literal_eval("{" + contents + "}")
            return {
                str(item).strip().lower()
                for item in parsed
                if str(item).strip()
            }
        except (ValueError, SyntaxError, TypeError):
            quoted_items = re.findall(
                r"""['"]([^'"]+)['"]""",
                contents
            )

            if quoted_items:
                return {
                    item.strip().lower()
                    for item in quoted_items
                    if item.strip()
                }

            return {
                item.strip().lower()
                for item in contents.split(",")
                if item.strip()
            }

    return {
        item.strip().lower()
        for item in text.split(",")
        if item.strip()
    }


def serialize_itemset(value):
    parsed = parse_products(value)
    return ", ".join(sorted(parsed)) if parsed else str(value)


def get_column(df, possible_names):
    column_lookup = {
        str(col).strip().lower(): col
        for col in df.columns
    }

    for name in possible_names:
        actual = column_lookup.get(name.lower())
        if actual is not None:
            return actual

    return None


def normalize_product_name(product):
    if not isinstance(product, str):
        return None

    return product_lookup.get(product.strip().lower())


def is_present(value):
    if isinstance(value, bool):
        return value

    if pd.isna(value):
        return False

    if isinstance(value, (int, float)):
        return value != 0

    return str(value).strip().lower() in {
        "true", "1", "yes", "y"
    }


# =========================================================
# VALIDATE RULE DATA
# =========================================================

required_rule_columns = [
    "antecedents",
    "consequents",
    "support",
    "confidence",
    "lift"
]

missing_rule_columns = [
    col for col in required_rule_columns
    if col not in rules_df.columns
]

if missing_rule_columns:
    raise ValueError(
        "Association rules CSV is missing columns: "
        + ", ".join(missing_rule_columns)
    )


# =========================================================
# PREPARE RULES ONCE
# =========================================================

prepared_rules = []

for _, rule in rules_df.iterrows():

    antecedents = parse_products(rule["antecedents"])
    consequents = parse_products(rule["consequents"])

    if not antecedents or not consequents:
        continue

    confidence = safe_float(rule["confidence"])

    if confidence <= 1:
        confidence *= 100

    prepared_rules.append({
        "antecedents": antecedents,
        "consequents": consequents,
        "support": safe_float(rule["support"]),
        "confidence": confidence,
        "lift": safe_float(rule["lift"])
    })


# =========================================================
# PRODUCT FREQUENCY
# =========================================================

def calculate_product_frequency():

    frequency = {}

    for product in products:
        frequency[product] = int(
            basket_df[product].apply(is_present).sum()
        )

    result = pd.DataFrame(
        frequency.items(),
        columns=["product", "frequency"]
    )

    return result.sort_values(
        "frequency",
        ascending=False
    ).reset_index(drop=True)


product_frequency_df = calculate_product_frequency()


# =========================================================
# RECOMMENDATION ENGINE
# =========================================================

def get_recommendations(selected_products, top_n=8):

    selected = {
        product.strip().lower()
        for product in selected_products
        if isinstance(product, str) and product.strip()
    }

    if not selected:
        return []

    recommendations = {}

    for rule in prepared_rules:

        antecedents = rule["antecedents"]
        consequents = rule["consequents"]

        # Selected basket must contain all antecedents
        if not antecedents.issubset(selected):
            continue

        for product in consequents:

            # Skip products already selected
            if product in selected:
                continue

            # Skip products outside dataset
            if product not in product_lookup:
                continue

            result = {
                "product": product_lookup[product],
                "support": round(rule["support"], 6),
                "confidence": round(rule["confidence"], 2),
                "lift": round(rule["lift"], 3),
                "matched_antecedents": sorted(antecedents)
            }

            existing = recommendations.get(product)

            # Keep strongest available rule
            if existing is None or (
                result["lift"],
                result["confidence"],
                result["support"]
            ) > (
                existing["lift"],
                existing["confidence"],
                existing["support"]
            ):
                recommendations[product] = result

    return sorted(
        recommendations.values(),
        key=lambda x: (
            x["lift"],
            x["confidence"],
            x["support"]
        ),
        reverse=True
    )[:top_n]


# =========================================================
# PAGE ROUTES
# =========================================================

@app.route("/")
def home():
    return render_template(
        "overview.html",
        active_page="overview",
        total_transactions=total_transactions,
        total_products=total_products,
        total_itemsets=total_itemsets,
        total_rules=total_rules
    )


@app.route("/recommendations")
def recommendations_page():
    return render_template(
        "recommendations.html",
        active_page="recommendations",
        products=products
    )


@app.route("/market-analysis")
def market_analysis_page():
    return render_template(
        "market_analysis.html",
        active_page="market-analysis"
    )


@app.route("/product-insights")
def product_insights_page():
    return render_template(
        "product_insights.html",
        active_page="product-insights"
    )


@app.route("/about")
def about_page():
    return render_template(
        "about.html",
        active_page="about"
    )


# =========================================================
# AI RECOMMENDATIONS API
# =========================================================

@app.route("/recommend", methods=["POST"])
def recommend():

    data = request.get_json(silent=True) or {}
    selected_products = data.get("products", [])

    if not isinstance(selected_products, list) or not selected_products:
        return jsonify({
            "success": False,
            "message": "Please select at least one product."
        }), 400

    valid_products = []

    for product in selected_products:
        normalized = normalize_product_name(product)

        if normalized:
            valid_products.append(normalized)

    valid_products = list(dict.fromkeys(valid_products))

    if not valid_products:
        return jsonify({
            "success": False,
            "message": "No valid products selected."
        }), 400

    recommendations = get_recommendations(
        valid_products,
        top_n=8
    )

    return jsonify({
        "success": True,
        "selected": valid_products,
        "recommendations": recommendations,
        "total_recommendations": len(recommendations),
        "message": (
            "Recommendations generated successfully."
            if recommendations
            else "No matching association rules found. Try another product or combination."
        )
    })


# =========================================================
# DEBUG API - CHECK A PRODUCT'S RULES
# =========================================================

@app.route("/api/debug-product/<path:product>")
def debug_product(product):

    normalized = normalize_product_name(product)

    if not normalized:
        return jsonify({
            "success": False,
            "message": "Product not found in dataset."
        }), 404

    key = normalized.lower()
    matching_rules = []

    for rule in prepared_rules:

        if key in rule["antecedents"]:
            matching_rules.append({
                "antecedents": sorted(rule["antecedents"]),
                "consequents": sorted(rule["consequents"]),
                "support": round(rule["support"], 6),
                "confidence": round(rule["confidence"], 2),
                "lift": round(rule["lift"], 3)
            })

        elif key in rule["consequents"]:
            matching_rules.append({
                "antecedents": sorted(rule["antecedents"]),
                "consequents": sorted(rule["consequents"]),
                "support": round(rule["support"], 6),
                "confidence": round(rule["confidence"], 2),
                "lift": round(rule["lift"], 3)
            })

    return jsonify({
        "success": True,
        "product": normalized,
        "matching_rules": matching_rules,
        "total_matching_rules": len(matching_rules)
    })


# =========================================================
# DASHBOARD STATISTICS API
# =========================================================

@app.route("/api/stats")
def stats():

    return jsonify({
        "success": True,
        "transactions": total_transactions,
        "products": total_products,
        "itemsets": total_itemsets,
        "rules": total_rules,
        "original_records": 38765,
        "cleaned_records": 38006,
        "duplicates_removed": 759,
        "unique_customers": 3898,
        "algorithm": "Apriori",
        "learning_type": "Unsupervised Learning"
    })


# =========================================================
# ASSOCIATION RULES API
# =========================================================

@app.route("/api/rules")
def get_rules():

    result = rules_df.copy()

    result["antecedents"] = result["antecedents"].apply(
        serialize_itemset
    )

    result["consequents"] = result["consequents"].apply(
        serialize_itemset
    )

    result = result[
        [
            "antecedents",
            "consequents",
            "support",
            "confidence",
            "lift"
        ]
    ].fillna("")

    return jsonify({
        "success": True,
        "rules": result.to_dict(orient="records")
    })


# =========================================================
# FREQUENT ITEMSETS API
# =========================================================

@app.route("/api/itemsets")
def get_itemsets():

    result = itemsets_df.copy()

    itemset_col = get_column(
        result,
        ["itemsets", "items"]
    )

    if itemset_col is not None:
        result[itemset_col] = result[itemset_col].apply(
            serialize_itemset
        )

    result = result.fillna("")

    return jsonify({
        "success": True,
        "total": len(result),
        "itemsets": result.to_dict(orient="records")
    })


# =========================================================
# PRODUCT INSIGHTS API
# =========================================================

@app.route("/api/product-insights")
def get_product_insights():

    top_products = product_frequency_df.head(15)

    bottom_products = product_frequency_df.tail(10).sort_values(
        "frequency",
        ascending=True
    )

    return jsonify({
        "success": True,
        "top_products": top_products.to_dict(orient="records"),
        "least_frequent_products": bottom_products.to_dict(
            orient="records"
        ),
        "all_products": product_frequency_df.to_dict(
            orient="records"
        ),
        "total_products": total_products,
        "total_transactions": total_transactions
    })


# =========================================================
# PROJECT INFORMATION API
# =========================================================

@app.route("/api/project-info")
def project_info():

    return jsonify({
        "name": "BASKET IQ",
        "full_name": "AI-Powered Retail Recommendation & Market Basket Analysis System",
        "tagline": "Discover Patterns. Connect Products. Recommend Smarter.",
        "algorithm": "Apriori",
        "learning_type": "Unsupervised Machine Learning",
        "dataset": "Groceries Dataset by Heeral Dedhia",
        "original_records": 38765,
        "cleaned_records": 38006,
        "duplicates_removed": 759,
        "customers": 3898,
        "products": total_products,
        "transactions": total_transactions,
        "frequent_itemsets": total_itemsets,
        "association_rules": total_rules,
        "technologies": [
            "Python",
            "Pandas",
            "NumPy",
            "MLxtend",
            "Flask",
            "HTML",
            "CSS",
            "JavaScript",
            "Plotly",
            "GitHub",
            "Render"
        ]
    })


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route("/health")
def health():

    return jsonify({
        "status": "healthy",
        "application": "BASKET IQ",
        "model_loaded": True,
        "total_rules": total_rules,
        "total_products": total_products
    })


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    print("\n" + "=" * 55)
    print("       BASKET IQ - RETAIL INTELLIGENCE PLATFORM")
    print("=" * 55)

    print(f"Transactions : {total_transactions}")
    print(f"Products     : {total_products}")
    print(f"Itemsets     : {total_itemsets}")
    print(f"Rules        : {total_rules}")

    print("\nTRAINED ASSOCIATION RULES:")

    for rule in prepared_rules:
        print(
            f"{sorted(rule['antecedents'])} "
            f"---> {sorted(rule['consequents'])} "
            f"| Confidence: {rule['confidence']}% "
            f"| Lift: {rule['lift']}"
        )

    print("=" * 55)

    port = int(os.environ.get("PORT", 5050))

    app.run(
        debug=True,
        host="0.0.0.0",
        port=port
    )
