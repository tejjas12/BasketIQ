🛒 BASKET IQ

AI-Powered Retail Recommendation & Market Basket Analysis System

Discover Patterns. Connect Products. Recommend Smarter.

""Live Demo" (https://img.shields.io/badge/Live-Demo-success?style=for-the-badge)" (https://basketiq-clxm.onrender.com)
""Python" (https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)" (https://www.python.org/)
""Flask" (https://img.shields.io/badge/Flask-Web%20Framework-black?style=for-the-badge&logo=flask)" (https://flask.palletsprojects.com/)
""Algorithm" (https://img.shields.io/badge/Algorithm-Apriori-orange?style=for-the-badge)" (https://rasbt.github.io/mlxtend/)

🌐 Live Application

Try Basket IQ: https://basketiq-clxm.onrender.com

📌 Project Overview

Basket IQ is an AI-powered retail analytics and product recommendation web application that uses Market Basket Analysis (MBA) and the Apriori Algorithm to discover relationships between products purchased together.

The system analyzes historical grocery transaction data, identifies frequent itemsets, generates association rules, and provides intelligent product recommendations based on customer-selected products.

It helps understand customer purchasing patterns and supports data-driven retail decisions.

🎯 Objectives

- Analyze customer purchasing behaviour.
- Discover frequently purchased product combinations.
- Generate meaningful association rules.
- Recommend related products using Apriori.
- Visualize retail purchasing patterns.
- Understand Support, Confidence, and Lift metrics.

✨ Key Features

1. Overview Dashboard

- Retail analytics dashboard.
- Transaction and product statistics.
- Frequent itemset insights.
- Association rule summaries.

2. AI Product Recommendations

- Select products from the available catalogue.
- Generate recommendations based on association rules.
- Rank recommendations using Lift, Confidence, and Support.

3. Market Basket Analysis

- Explore frequent itemsets.
- Analyze product associations.
- Understand purchasing relationships.
- View association rule metrics.

4. Product Insights

- Product frequency analysis.
- Popular product identification.
- Customer purchasing pattern insights.

5. Interactive Web Interface

- Flask-powered web application.
- Responsive frontend.
- Interactive analytics and visualizations.

🧠 Algorithm – Apriori

Basket IQ uses the Apriori algorithm, an unsupervised association-rule learning technique.

The algorithm identifies frequent itemsets and generates rules describing relationships between products.

Important Metrics:

Metric| Meaning
Support| Frequency of products appearing together in all transactions
Confidence| Probability of purchasing B when A is purchased
Lift| Strength of association between A and B compared with independent occurrence

Interpretation of Lift:

- Lift > 1: Positive association.
- Lift = 1: Independent occurrence.
- Lift < 1: Negative association.

Association does not necessarily imply causation.

🛠️ Technology Stack

Category| Technologies
Programming Language| Python
Backend| Flask
Data Processing| Pandas, NumPy
Machine Learning| MLxtend, Apriori
Frontend| HTML5, CSS3, JavaScript
Visualization| Plotly
Version Control| Git, GitHub
Deployment| Render

📂 Project Structure

BasketIQ/
│
├── app.py
├── requirements.txt
├── README.md
│
├── data/
│   ├── processed/
│   │   ├── frequent_itemsets.csv
│   │   ├── association_rules.csv
│   │   ├── basket_onehot.csv
│   │   ├── basket_transactions.csv
│   │   ├── customer_summary.csv
│   │   ├── product_frequency.csv
│   │   └── cleaned_transactions.csv
│   │
│   └── raw/
│
├── models/
│   ├── frequent_itemsets.csv
│   ├── association_rules.csv
│   └── basket_iq_model.pkl
│
├── reports/
│
├── src/
│   ├── apriori_engine.py
│   ├── preprocessing.py
│   ├── recommendation_engine.py
│   └── train_model.py
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── script.js
│
└── templates/
    ├── base.html
    ├── overview.html
    ├── recommendations.html
    ├── market_analysis.html
    ├── product_insights.html
    └── about.html

⚙️ Installation & Setup

Follow these steps to run Basket IQ locally.

Step 1: Clone Repository

git clone https://github.com/tejjas12/BasketIQ.git

Step 2: Navigate to Project Directory

cd BasketIQ

Step 3: Create Virtual Environment

python -m venv venv

Activate the environment:

macOS / Linux

source venv/bin/activate

Windows

venv\Scripts\activate

Step 4: Install Dependencies

pip install -r requirements.txt

Step 5: Run Application

python app.py

Step 6: Open in Browser

http://127.0.0.1:5050

📊 Dataset & Preprocessing

The project uses grocery transaction data for Market Basket Analysis.

Preprocessing includes:

1. Removing duplicate records.
2. Organizing products into customer transactions.
3. Converting transaction data into a one-hot encoded basket matrix.
4. Identifying frequent itemsets.
5. Generating association rules.

Each transaction represents a basket of products purchased together.

🚀 Deployment

Basket IQ is deployed using Render.

Live URL: https://basketiq-clxm.onrender.com

The application is connected to GitHub for source-code management and deployment updates.

🔮 Future Enhancements

- Advanced recommendation ranking.
- Customer segmentation.
- Real-time retail analytics.
- Improved interactive visualizations.
- Personalized product recommendations.
- Larger transaction dataset analysis.

👨‍💻 Project Team

Developed by:

- Tejas Digambar Patil
- Om

Department: Computer Science and Engineering – Data Science

Project Type: Academic AIML Project

📚 References

- "Apriori Algorithm – MLxtend Documentation" (https://rasbt.github.io/mlxtend/)
- "Flask Documentation" (https://flask.palletsprojects.com/)
- "Pandas Documentation" (https://pandas.pydata.org/docs/)
- "NumPy Documentation" (https://numpy.org/doc/)
- "Render Documentation" (https://render.com/docs)

---

<p align="center">
  <b>BASKET IQ</b><br>
  Discover Patterns. Connect Products. Recommend Smarter.
</p><p align="center">
  Made with ❤️ using Python, Flask & Apriori
</p>
