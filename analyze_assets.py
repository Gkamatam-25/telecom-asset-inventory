"""
Telecom Asset and Inventory Analytics - SQL-style Analysis and Reporting
Author: Gowthami Kamatam
"""

import pandas as pd
import numpy as np
import sqlite3
import warnings
warnings.filterwarnings("ignore")

# 1. Load data
print("Loading telecom asset inventory data...")
df = pd.read_csv("data/telecom_assets.csv", parse_dates=["purchase_date", "warranty_expiry", "last_audit_date"])
print(f"Loaded {len(df)} asset records\n")

# 2. Load into SQLite for SQL-based analysis
conn = sqlite3.connect(":memory:")
df.to_sql("assets", conn, index=False, if_exists="replace")

print("="*70)
print("TELECOM ASSET AND INVENTORY ANALYSIS REPORT")
print("="*70)

# 3. Overall inventory KPIs
query_overview = """
SELECT
    COUNT(*) as total_assets,
    ROUND(SUM(unit_cost), 2) as total_inventory_value,
    ROUND(AVG(unit_cost), 2) as avg_asset_cost,
    SUM(CASE WHEN warranty_active = 1 THEN 1 ELSE 0 END) as assets_under_warranty,
    SUM(needs_audit) as assets_needing_audit
FROM assets
"""
overview = pd.read_sql(query_overview, conn)
print("\n--- OVERALL INVENTORY KPIs ---")
print(overview.to_string(index=False))

# 4. Assets by status
query_status = """
SELECT
    status,
    COUNT(*) as asset_count,
    ROUND(SUM(unit_cost), 2) as total_value
FROM assets
GROUP BY status
ORDER BY asset_count DESC
"""
by_status = pd.read_sql(query_status, conn)
print("\n--- ASSETS BY STATUS ---")
print(by_status.to_string(index=False))

# 5. Assets by lifecycle stage
query_lifecycle = """
SELECT
    lifecycle_stage,
    COUNT(*) as asset_count,
    ROUND(SUM(unit_cost), 2) as total_value,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM assets), 1) as pct_of_total
FROM assets
GROUP BY lifecycle_stage
ORDER BY
    CASE lifecycle_stage
        WHEN 'New' THEN 1
        WHEN 'Active' THEN 2
        WHEN 'Aging' THEN 3
        WHEN 'End of Life - Plan Replace' THEN 4
        WHEN 'End of Support' THEN 5
    END
"""
by_lifecycle = pd.read_sql(query_lifecycle, conn)
print("\n--- ASSETS BY LIFECYCLE STAGE ---")
print(by_lifecycle.to_string(index=False))

# 6. Inventory value by site
query_sites = """
SELECT
    site,
    COUNT(*) as asset_count,
    ROUND(SUM(unit_cost), 2) as total_value,
    SUM(needs_audit) as assets_needing_audit
FROM assets
GROUP BY site
ORDER BY total_value DESC
LIMIT 6
"""
by_site = pd.read_sql(query_sites, conn)
print("\n--- TOP 6 SITES BY INVENTORY VALUE ---")
print(by_site.to_string(index=False))

# 7. Asset type breakdown
query_types = """
SELECT
    asset_type,
    COUNT(*) as asset_count,
    ROUND(AVG(unit_cost), 2) as avg_cost,
    ROUND(SUM(unit_cost), 2) as total_value
FROM assets
GROUP BY asset_type
ORDER BY total_value DESC
"""
by_type = pd.read_sql(query_types, conn)
print("\n--- ASSET TYPE BREAKDOWN ---")
print(by_type.to_string(index=False))

# 8. Manufacturer breakdown
query_manufacturer = """
SELECT
    manufacturer,
    COUNT(*) as asset_count,
    ROUND(SUM(unit_cost), 2) as total_value
FROM assets
GROUP BY manufacturer
ORDER BY asset_count DESC
"""
by_manufacturer = pd.read_sql(query_manufacturer, conn)
print("\n--- MANUFACTURER BREAKDOWN ---")
print(by_manufacturer.to_string(index=False))

# 9. Warranty status
query_warranty = """
SELECT
    warranty_active,
    COUNT(*) as asset_count,
    ROUND(SUM(unit_cost), 2) as total_value
FROM assets
GROUP BY warranty_active
"""
by_warranty = pd.read_sql(query_warranty, conn)
print("\n--- WARRANTY STATUS ---")
print(by_warranty.to_string(index=False))

# 10. Assets needing replacement soon (End of Life or End of Support)
query_eol = """
SELECT
    site,
    asset_type,
    COUNT(*) as asset_count,
    ROUND(SUM(unit_cost), 2) as replacement_value
FROM assets
WHERE lifecycle_stage IN ('End of Life - Plan Replace', 'End of Support')
GROUP BY site, asset_type
ORDER BY replacement_value DESC
LIMIT 10
"""
eol_assets = pd.read_sql(query_eol, conn)
print("\n--- TOP 10 SITE/TYPE COMBINATIONS NEEDING REPLACEMENT ---")
print(eol_assets.to_string(index=False))

# 11. Average utilization by asset type (active assets only)
query_utilization = """
SELECT
    asset_type,
    ROUND(AVG(utilization_pct), 1) as avg_utilization_pct,
    COUNT(*) as active_count
FROM assets
WHERE status = 'Active'
GROUP BY asset_type
ORDER BY avg_utilization_pct DESC
"""
by_utilization = pd.read_sql(query_utilization, conn)
print("\n--- AVERAGE UTILIZATION BY ASSET TYPE (Active Only) ---")
print(by_utilization.to_string(index=False))

# 12. Purchase year trend
query_yearly = """
SELECT
    purchase_year,
    COUNT(*) as assets_purchased,
    ROUND(SUM(unit_cost), 2) as total_spend
FROM assets
GROUP BY purchase_year
ORDER BY purchase_year
"""
by_year = pd.read_sql(query_yearly, conn)
print("\n--- PURCHASES BY YEAR ---")
print(by_year.to_string(index=False))

# 13. Audit compliance by site
query_audit = """
SELECT
    site,
    COUNT(*) as total_assets,
    SUM(needs_audit) as overdue_audits,
    ROUND(SUM(needs_audit) * 100.0 / COUNT(*), 1) as pct_overdue
FROM assets
GROUP BY site
ORDER BY pct_overdue DESC
"""
by_audit = pd.read_sql(query_audit, conn)
print("\n--- AUDIT COMPLIANCE BY SITE ---")
print(by_audit.to_string(index=False))

# 14. Save summary tables for dashboard use
print("\nSaving analysis outputs for dashboard...")
overview.to_csv("data/summary_overview.csv", index=False)
by_status.to_csv("data/summary_by_status.csv", index=False)
by_lifecycle.to_csv("data/summary_by_lifecycle.csv", index=False)
by_site.to_csv("data/summary_by_site.csv", index=False)
by_type.to_csv("data/summary_by_type.csv", index=False)
by_manufacturer.to_csv("data/summary_by_manufacturer.csv", index=False)
by_warranty.to_csv("data/summary_by_warranty.csv", index=False)
eol_assets.to_csv("data/summary_eol_assets.csv", index=False)
by_utilization.to_csv("data/summary_by_utilization.csv", index=False)
by_year.to_csv("data/summary_by_year.csv", index=False)
by_audit.to_csv("data/summary_by_audit.csv", index=False)

conn.close()
print("\nAnalysis complete. Summary files saved to data/")
