import pandas as pd

REQUIRED_COLUMNS = ["Member_number", "Date", "itemDescription"]

def preprocess_groceries(input_path: str):
    """Clean Groceries_dataset.csv and create transaction basket data."""
    df = pd.read_csv(input_path)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df = df[REQUIRED_COLUMNS].copy()
    df["Member_number"] = pd.to_numeric(df["Member_number"], errors="coerce")
    df["Date"] = pd.to_datetime(df["Date"], format="%d-%m-%Y", errors="coerce")
    df["itemDescription"] = df["itemDescription"].astype("string").str.strip().str.lower()

    df = df.dropna(subset=REQUIRED_COLUMNS)
    df = df[(df["Member_number"] > 0) & (df["itemDescription"] != "")]
    df["Member_number"] = df["Member_number"].astype("int64")
    df["Date"] = df["Date"].dt.strftime("%Y-%m-%d")
    df = df.drop_duplicates(["Member_number", "Date", "itemDescription"])

    df["TransactionID"] = df["Member_number"].astype(str) + "_" + df["Date"]
    transaction_items = df[["TransactionID", "itemDescription"]].drop_duplicates()
    basket = (transaction_items.groupby("TransactionID")["itemDescription"]
              .apply(lambda x: " | ".join(sorted(set(x))))
              .reset_index(name="Items"))
    item_sets = transaction_items.groupby("TransactionID")["itemDescription"].apply(set)
    products = sorted(transaction_items["itemDescription"].unique())
    onehot = pd.DataFrame(False, index=item_sets.index, columns=products)
    for transaction_id, items in item_sets.items():
        onehot.loc[transaction_id, list(items)] = True
    onehot.index.name = "TransactionID"
    return df, transaction_items, basket, onehot.reset_index()
