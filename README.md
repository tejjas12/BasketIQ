# ShopMind AI - Dataset Pack

This archive contains the cleaned and processed Kaggle Groceries dataset, ready for Apriori-based market basket analysis.

## Dataset summary
- Original rows: 38,765
- Clean purchase rows: 38,006
- Unique customers: 3,898
- Unique products: 167
- Derived baskets: 14,963

## Important transaction assumption
The source dataset does not provide an invoice number. We define a basket as one unique `Member_number + Date` combination. This can combine same-day purchases by the same customer. Mention this limitation in your report and viva.

## Most useful files
- `data/processed/basket_onehot.csv`: Boolean transaction-product matrix; use this as Apriori input.
- `data/processed/transaction_items.csv`: One row per transaction-product pair.
- `data/processed/basket_transactions.csv`: Human-readable basket list.
- `data/processed/cleaned_transactions.csv`: Cleaned row-level records.
- `data/processed/product_frequency.csv`: Product transaction counts and shares.
- `data/processed/customer_summary.csv`: Customer-level summary.
- `reports/preprocessing_report.txt`: Cleaning methodology and summary.

## Run Apriori
Install:
```bash
pip install pandas mlxtend
```

From the project root, copy `src/apriori_engine.py` into your ShopMind project or run it from this archive's root:
```bash
python src/apriori_engine.py
```

The script uses minimum support 0.01, confidence 0.20 and lift 1.0 as initial experimental thresholds. Tune these based on results and runtime.

## Notes
- Product names are normalized to lowercase.
- Exact duplicate customer-date-product rows are removed.
- The one-hot matrix is a basket representation, not a customer profile.
- This dataset is suitable for association mining; it does not contain product prices or explicit invoice IDs.
