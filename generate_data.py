"""
Telecom Asset & Inventory Analytics — Synthetic Data Generator
Author: Gowthami Kamatam
"""

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

np.random.seed(42)
random.seed(42)

# Configuration
N_ASSETS = 3000

SITES = [
    "Chicago-DC1", "Chicago-DC2", "Dallas-DC1", "Phoenix-DC1",
    "Atlanta-DC1", "Seattle-DC1", "NewYork-DC1", "NewYork-DC2",
    "Denver-DC1", "Miami-DC1", "Boston-DC1", "Austin-DC1"
]

ASSET_TYPES = [
    "Router", "Switch", "Server", "Firewall", "Load Balancer",
    "UPS Unit", "PDU", "Storage Array", "Optical Transceiver", "Patch Panel"
]

MANUFACTURERS = [
    "Cisco", "Juniper", "Arista", "Dell", "HPE", "Nokia",
    "Ciena", "Fortinet", "Palo Alto Networks"
]

STATUS_OPTIONS = ["Active", "Active", "Active", "Active", "In Maintenance", "Decommissioned", "In Storage"]
STATUS_WEIGHTS = [0.55, 0.1, 0.1, 0.1, 0.05, 0.05, 0.05]

VENDORS = [
    "TechServe Logistics", "GlobalNet Supply", "DataCenter Direct",
    "NetGear Solutions", "Infra Partners Inc", "CoreEquip Distribution"
]

LIFECYCLE_STAGES = ["New", "Active", "Aging", "End of Life - Plan Replace", "End of Support"]

# Generate asset records
print("Generating synthetic telecom asset inventory data...")

records = []
purchase_start = datetime(2018, 1, 1)

for i in range(N_ASSETS):
    asset_id = f"AST-{20000 + i}"
    asset_type = random.choice(ASSET_TYPES)
    manufacturer = random.choice(MANUFACTURERS)
    site = random.choice(SITES)
    status = np.random.choice(STATUS_OPTIONS, p=STATUS_WEIGHTS)
    vendor = random.choice(VENDORS)

    # Purchase date over last 7 years
    days_offset = random.randint(0, 2555)
    purchase_date = purchase_start + timedelta(days=days_offset)

    # Asset age determines lifecycle stage
    age_years = (datetime(2026, 1, 1) - purchase_date).days / 365.25

    if age_years < 1:
        lifecycle = "New"
    elif age_years < 4:
        lifecycle = "Active"
    elif age_years < 6:
        lifecycle = "Aging"
    elif age_years < 7:
        lifecycle = "End of Life - Plan Replace"
    else:
        lifecycle = "End of Support"

    # Warranty - typically 3-5 years from purchase
    warranty_years = random.choice([3, 3, 5, 5, 5])
    warranty_expiry = purchase_date + timedelta(days=warranty_years * 365)
    warranty_active = warranty_expiry > datetime(2026, 1, 1)

    # Cost varies by asset type
    cost_ranges = {
        "Router": (3000, 25000), "Switch": (1500, 15000), "Server": (5000, 35000),
        "Firewall": (4000, 20000), "Load Balancer": (8000, 30000),
        "UPS Unit": (2000, 12000), "PDU": (500, 3000), "Storage Array": (10000, 60000),
        "Optical Transceiver": (200, 2000), "Patch Panel": (100, 800)
    }
    cost_range = cost_ranges[asset_type]
    unit_cost = round(random.uniform(*cost_range), 2)

    # Rack position
    rack_number = f"R{random.randint(1, 40):02d}"
    rack_unit = f"U{random.randint(1, 42)}"

    # Last audit date
    last_audit_days_ago = random.randint(1, 365)
    last_audit_date = datetime(2026, 1, 1) - timedelta(days=last_audit_days_ago)

    # Utilization (for active assets)
    if status == "Active":
        utilization_pct = round(random.uniform(15, 95), 1)
    else:
        utilization_pct = 0.0

    records.append({
        "asset_id": asset_id,
        "asset_type": asset_type,
        "manufacturer": manufacturer,
        "site": site,
        "rack_number": rack_number,
        "rack_unit": rack_unit,
        "status": status,
        "lifecycle_stage": lifecycle,
        "vendor": vendor,
        "purchase_date": purchase_date,
        "unit_cost": unit_cost,
        "warranty_expiry": warranty_expiry,
        "warranty_active": warranty_active,
        "age_years": round(age_years, 1),
        "utilization_pct": utilization_pct,
        "last_audit_date": last_audit_date
    })

df = pd.DataFrame(records)
df = df.sort_values("purchase_date").reset_index(drop=True)

# Derived fields
df["purchase_year"] = df["purchase_date"].dt.year
df["days_since_audit"] = (datetime(2026, 1, 1) - df["last_audit_date"]).dt.days
df["needs_audit"] = df["days_since_audit"] > 180

df.to_csv("data/telecom_assets.csv", index=False)

print(f"Generated {len(df)} asset records")
print(f"\nStatus distribution:")
print(df["status"].value_counts())
print(f"\nLifecycle stage distribution:")
print(df["lifecycle_stage"].value_counts())
print(f"\nTotal inventory value: ${df['unit_cost'].sum():,.2f}")
print(f"\nAssets needing audit (>180 days): {df['needs_audit'].sum()}")
print(f"\nSample data:")
print(df.head(3))
print(f"\nSaved to data/telecom_assets.csv")
