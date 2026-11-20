
from pathlib import Path
import pickle
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "basket_iq_model.pkl"


def load_model():
    with open(MODEL_PATH, "rb") as file:
        return pickle.load(file)


def recommend_products(selected_products, top_n=5):
    model = load_model()
    rules = model["association_rules"]

    selected = {
        str(product).strip().lower()
        for product in selected_products
    }

    recommendations = []

    for _, rule in rules.iterrows():
        antecedents = {
            str(item).lower()
            for item in rule["antecedents"]
        }

        consequents = rule["consequents"]

        # Recommend only when all antecedent products are selected
        if antecedents and antecedents.issubset(selected):
            for product in consequents:
                product = str(product)

                if product.lower() not in selected:
                    recommendations.append({
                        "product": product,
                        "support": float(rule["support"]),
                        "confidence": float(rule["confidence"]),
                        "lift": float(rule["lift"])
                    })

    if not recommendations:
        return []

    result = pd.DataFrame(recommendations)

    result = (
        result.sort_values(
            ["lift", "confidence", "support"],
            ascending=False
        )
        .drop_duplicates(subset=["product"])
        .head(top_n)
    )

    return result.to_dict(orient="records")


if __name__ == "__main__":
    products = recommend_products(["frankfurter"])

    print("\nBASKET IQ - PRODUCT RECOMMENDATIONS")
    print("=" * 45)

    if products:
        for item in products:
            print(f"\nRecommended: {item['product']}")
            print(f"Confidence: {item['confidence']:.2%}")
            print(f"Lift: {item['lift']:.3f}")
    else:
        print("No recommendations found for this product.")
