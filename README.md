# Telecom Asset and Inventory Analytics Dashboard

A SQL and Python-based analytics system for tracking, valuing, and managing
telecom infrastructure assets across multiple data center sites - built to
support inventory management, lifecycle planning, and audit compliance.

## What it does

- Tracks 3,000+ telecom asset records across 12 data center sites
- Monitors asset lifecycle stages from New through End of Support
- Calculates total inventory value and tracks warranty status
- Identifies assets overdue for audit and flags replacement priorities
- Analyzes utilization, manufacturer distribution, and purchase trends over time

## Tech Stack

- Python - core language
- SQL (SQLite) - inventory analysis and reporting queries
- Pandas / NumPy - data processing and feature engineering
- Streamlit - interactive web dashboard
- Plotly - dynamic visualizations
- Faker - synthetic data generation

## Key Metrics Tracked

| Metric | Description |
|--------|--------------|
| Total Inventory Value | Sum of unit cost across all tracked assets |
| Lifecycle Distribution | Breakdown of assets by stage (New, Active, Aging, End of Life, End of Support) |
| Warranty Status | Percentage of assets currently under active warranty |
| Audit Compliance | Percentage of assets overdue for physical audit (180+ days) |
| Replacement Priority | Site and asset type combinations with highest end-of-life replacement value |

## How to Run

### 1. Clone the repo
```bash
git clone https://github.com/gkamatam-25/telecom-asset-inventory.git
cd telecom-asset-inventory
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Generate the dataset
```bash
python3 generate_data.py
```

### 4. Run the SQL analysis
```bash
python3 analyze_assets.py
```

### 5. Launch the dashboard
```bash
streamlit run app.py
```

## Project Structure

```
telecom-asset-inventory/
├── data/
│   ├── telecom_assets.csv
│   └── summary_*.csv          (analysis outputs)
├── generate_data.py            (synthetic data generator)
├── analyze_assets.py           (SQL-based analysis)
├── app.py                      (Streamlit dashboard)
├── requirements.txt
└── README.md
```

## Key Features

- Four-tab interactive dashboard - Overview, Lifecycle and Warranty, Sites and Manufacturers, Replacement Planning
- SQL-driven analysis - 10+ SQLite queries covering status, lifecycle, site value, and audit compliance
- Real-time filtering - by site, asset type, status, and lifecycle stage
- End-of-life tracking - identifies highest-value replacement priorities by site and asset type
- Audit compliance monitoring - flags assets not physically verified in over 180 days

## Sample Insights

- Total inventory value across all tracked assets: approximately $35.1 million
- Storage Arrays represent the highest total inventory value of any asset type
- Roughly 51 percent of assets are overdue for audit, varying significantly by site
- Nearly 29 percent of the fleet falls into End of Life or End of Support lifecycle stages, representing future replacement risk

## Author

Gowthami Kamatam - MS Data Science, Illinois Institute of Technology
