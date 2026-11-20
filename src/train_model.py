
from pathlib import Path
import pickle
import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "processed" / "basket_onehot.csv"
MODEL_DIR = BASE_DIR / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 55)
print("BASKET IQ - APRIORI MODEL TRAINING")
print("=" * 55)

# Step 1: Load dataset
print("\n[1/5] Loading transaction dataset...")

df = pd.read_csv(DATA_PATH)

if "TransactionID" in df.columns:
    df = df.drop(columns=["TransactionID"])

# Ensure the basket matrix is binary
df = df.apply(pd.to_numeric, errors="raise")

if not df.isin([0, 1]).all().all():
    raise ValueError("Basket matrix must contain only 0 and 1.")

basket = df.astype(bool)

print(f"Transactions: {len(basket):,}")
print(f"Products: {len(basket.columns):,}")

# Step 2: Apriori
print("\n[2/5] Finding frequent itemsets...")

frequent_itemsets = apriori(
    basket,
    min_support=0.005,
    use_colnames=True,
    low_memory=True
)

frequent_itemsets["length"] = (
    frequent_itemsets["itemsets"].apply(len)
)

print(f"Frequent itemsets: {len(frequent_itemsets):,}")

# Step 3: Generate association rules
print("\n[3/5] Generating association rules...")

if frequent_itemsets.empty or frequent_itemsets["length"].max() < 2:
    raise ValueError(
        "No frequent product combinations found. "
        "Try lowering min_support."
    )

rules = association_rules(
    frequent_itemsets,
    metric="confidence",
    min_threshold=0.10,
    num_itemsets=len(basket)
)

rules = rules[rules["lift"] > 1.0].copy()

rules = rules.sort_values(
    by=["lift", "confidence", "support"],
    ascending=False
)

print(f"Association rules: {len(rules):,}")

# Step 4: Save readable CSV files
print("\n[4/5] Saving model results...")

itemsets_csv = frequent_itemsets.copy()
itemsets_csv["itemsets"] = itemsets_csv["itemsets"].apply(
    lambda x: ", ".join(sorted(x))
)

rules_csv = rules.copy()

for col in ["antecedents", "consequents"]:
    rules_csv[col] = rules_csv[col].apply(
        lambda x: ", ".join(sorted(x))
    )

itemsets_csv.to_csv(
    MODEL_DIR / "frequent_itemsets.csv",
    index=False
)

rules_csv.to_csv(
    MODEL_DIR / "association_rules.csv",
    index=False
)

# Save actual Python objects for the Flask application
model_data = {
    "algorithm": "Apriori",
    "min_support": 0.005,
    "min_confidence": 0.10,
    "min_lift": 1.0,
    "transaction_count": len(basket),
    "products": list(basket.columns),
    "frequent_itemsets": frequent_itemsets,
    "association_rules": rules
}

with open(MODEL_DIR / "basket_iq_model.pkl", "wb") as f:
    pickle.dump(model_data, f)

# Step 5: Display results
print("\n[5/5] Training summary")
print("=" * 55)

print(f"Total transactions: {len(basket):,}")
print(f"Unique products: {len(basket.columns):,}")
print(f"Frequent itemsets: {len(frequent_itemsets):,}")
print(f"Association rules: {len(rules):,}")

if not rules.empty:
    print("\nTop 5 Association Rules:")

    for _, rule in rules.head(5).iterrows():
        a = ", ".join(sorted(rule["antecedents"]))
        c = ", ".join(sorted(rule["consequents"]))

        print(f"\n{a} -> {c}")
        print(f"Confidence: {rule['confidence']:.3f}")
        print(f"Lift: {rule['lift']:.3f}")

print("\nMODEL TRAINING COMPLETED!")
print(f"Saved outputs to: {MODEL_DIR}")
