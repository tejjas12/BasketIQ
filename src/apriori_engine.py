
from pathlib import Path

import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules


# =========================================================
# BASKET IQ - APRIORI ENGINE V2
# =========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = BASE_DIR / "data" / "processed" / "basket_onehot.csv"
OUTPUT_DIR = BASE_DIR / "data" / "processed"

# Updated experimental parameters
MIN_SUPPORT = 0.002
MIN_CONFIDENCE = 0.01
MIN_LIFT = 1.0
MAX_LEN = 3


# =========================================================
# BOOLEAN CONVERSION
# =========================================================

def convert_to_boolean(series):

    if pd.api.types.is_bool_dtype(series):
        return series.fillna(False)

    if pd.api.types.is_numeric_dtype(series):
        return series.fillna(0).ne(0)

    return (
        series.astype(str)
        .str.strip()
        .str.lower()
        .isin(["true", "1", "yes", "y"])
    )


# =========================================================
# APRIORI TRAINING
# =========================================================

def run_apriori(
    onehot_csv,
    min_support=MIN_SUPPORT,
    min_confidence=MIN_CONFIDENCE,
    min_lift=MIN_LIFT,
    max_len=MAX_LEN
):

    data = pd.read_csv(onehot_csv)

    # Identify TransactionID column
    transaction_column = next(
        (
            col for col in data.columns
            if str(col).strip().lower() == "transactionid"
        ),
        None
    )

    if transaction_column is None:
        raise ValueError("TransactionID column is missing.")

    # Remove transaction identifier
    basket = data.drop(columns=[transaction_column]).copy()

    if basket.empty or len(basket.columns) == 0:
        raise ValueError("No product columns found in dataset.")

    # Convert all product columns safely into boolean values
    for column in basket.columns:
        basket[column] = convert_to_boolean(basket[column])

    if not basket.to_numpy().any():
        raise ValueError("Basket dataset contains no product occurrences.")

    print("\n" + "=" * 55)
    print("BASKET IQ - APRIORI MODEL TRAINING V2")
    print("=" * 55)

    print(f"Transactions       : {len(basket)}")
    print(f"Products           : {len(basket.columns)}")
    print(f"Minimum Support    : {min_support}")
    print(f"Minimum Confidence : {min_confidence}")
    print(f"Minimum Lift       : {min_lift}")
    print(f"Maximum Item Length: {max_len}")

    # -----------------------------------------------------
    # STEP 1: FREQUENT ITEMSET GENERATION
    # -----------------------------------------------------

    print("\n[1/3] Discovering frequent itemsets...")

    frequent_itemsets = apriori(
        basket,
        min_support=min_support,
        use_colnames=True,
        max_len=max_len,
        low_memory=True
    )

    if frequent_itemsets.empty:
        raise ValueError(
            "No frequent itemsets found. "
            "Try lowering MIN_SUPPORT."
        )

    frequent_itemsets["length"] = (
        frequent_itemsets["itemsets"].apply(len)
    )

    print(f"Frequent Itemsets Found: {len(frequent_itemsets)}")

    # -----------------------------------------------------
    # STEP 2: ASSOCIATION RULE GENERATION
    # -----------------------------------------------------

    print("\n[2/3] Generating association rules...")

    all_rules = association_rules(
        frequent_itemsets,
        metric="confidence",
        min_threshold=min_confidence
    )

    print(f"Rules before lift filter: {len(all_rules)}")

    if all_rules.empty:
        raise ValueError(
            "No association rules generated. "
            "Try lowering MIN_CONFIDENCE."
        )

    # -----------------------------------------------------
    # STEP 3: FILTERING
    # -----------------------------------------------------

    rules = all_rules[
        (all_rules["lift"] >= min_lift) &
        (all_rules["confidence"] >= min_confidence)
    ].copy()

    print(f"Rules after lift filter : {len(rules)}")

    if rules.empty:
        print(
            "\nWARNING: No rules passed the current lift threshold."
        )

    # -----------------------------------------------------
    # STEP 4: READABLE PRODUCT NAMES
    # -----------------------------------------------------

    frequent_itemsets["itemsets"] = (
        frequent_itemsets["itemsets"].apply(
            lambda items: ", ".join(sorted(map(str, items)))
        )
    )

    if not rules.empty:

        rules["antecedents"] = rules["antecedents"].apply(
            lambda items: ", ".join(sorted(map(str, items)))
        )

        rules["consequents"] = rules["consequents"].apply(
            lambda items: ", ".join(sorted(map(str, items)))
        )

        rules = rules.sort_values(
            by=["lift", "confidence", "support"],
            ascending=False
        ).reset_index(drop=True)

    # -----------------------------------------------------
    # STEP 5: FINAL OUTPUT COLUMNS
    # -----------------------------------------------------

    itemset_columns = [
        "support",
        "itemsets",
        "length"
    ]

    rule_columns = [
        "antecedents",
        "consequents",
        "antecedent support",
        "consequent support",
        "support",
        "confidence",
        "lift",
        "leverage",
        "conviction"
    ]

    frequent_itemsets = frequent_itemsets[
        itemset_columns
    ]

    if not rules.empty:
        rules = rules[
            [col for col in rule_columns if col in rules.columns]
        ]

    return frequent_itemsets, rules


# =========================================================
# MAIN
# =========================================================

def main():

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Dataset not found: {INPUT_FILE}"
        )

    itemsets, rules = run_apriori(
        INPUT_FILE,
        min_support=MIN_SUPPORT,
        min_confidence=MIN_CONFIDENCE,
        min_lift=MIN_LIFT,
        max_len=MAX_LEN
    )

    # Save model outputs
    itemsets.to_csv(
        OUTPUT_DIR / "frequent_itemsets.csv",
        index=False
    )

    rules.to_csv(
        OUTPUT_DIR / "association_rules.csv",
        index=False
    )

    # -----------------------------------------------------
    # TRAINING REPORT
    # -----------------------------------------------------

    print("\n" + "=" * 55)
    print("BASKET IQ - TRAINING COMPLETED")
    print("=" * 55)

    print(f"Frequent Itemsets : {len(itemsets)}")
    print(f"Association Rules : {len(rules)}")

    if not itemsets.empty:
        print("\nItemset Distribution:")
        print(
            itemsets.groupby("length").size().to_string()
        )

    if not rules.empty:

        print("\nTop 15 Association Rules:")

        print(
            rules[
                [
                    "antecedents",
                    "consequents",
                    "support",
                    "confidence",
                    "lift"
                ]
            ].head(15).to_string(index=False)
        )

    print("\nFiles Saved:")
    print(OUTPUT_DIR / "frequent_itemsets.csv")
    print(OUTPUT_DIR / "association_rules.csv")

    print("\n" + "=" * 55)


if __name__ == "__main__":
    main()
