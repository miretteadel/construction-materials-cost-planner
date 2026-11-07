# ————— Imports
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from module1_quantity import load_elements


# ————— Settings
CURRENCY = "money units"


# ————— Units
UNITS = {"Cement": "kg", "Sand": "m3", "Aggregate": "m3"}


# ————— Required Columns
PRICE_COLUMNS = ("supplier_id", "material", "unit", "unit_price")
PURCHASE_COLUMNS = ("transaction_id", "element_id", "supplier_id", "material", "date", "quantity")


# ————— Check Columns
def check_columns(table, required, name):
    for column in required:
        if column not in table.columns:
            print("Rejected:", name, "file is missing the column", column)
            return False
    return True


# ————— Read Prices
def read_prices(filename):
    prices = pd.read_csv(filename)
    if not check_columns(prices, PRICE_COLUMNS, "prices"):
        return None
    return prices


# ————— Read Purchases
def read_purchases(filename):
    purchases = pd.read_csv(filename)
    if not check_columns(purchases, PURCHASE_COLUMNS, "purchases"):
        return None
    return purchases


# ————— Read Elements
def read_elements(filename):
    elements = pd.read_csv(filename)
    return elements[["element_id", "element_name", "site"]]


# ————— Elements Table
def elements_table(elements):
    rows = []
    for element in elements:
        rows.append([element.element_id, element.name, element.site])
    return pd.DataFrame(rows, columns=["element_id", "element_name", "site"])


# ————— Elements Table
def elements_to_table(elements):
    rows = []
    for element in elements:
        rows.append([element.element_id, element.name, element.site])
    return pd.DataFrame(rows, columns=["element_id", "element_name", "site"])


# ————— Clean Prices
def clean_prices(prices):
    prices = prices.copy()
    prices["supplier_id"] = prices["supplier_id"].str.strip()
    prices["material"] = prices["material"].str.strip().str.title()
    prices = prices.drop_duplicates(subset=["supplier_id", "material"])
    prices = prices.dropna()
    prices = prices[prices["unit_price"] > 0]
    return prices.reset_index(drop=True)


# ————— Clean Purchases
def clean_purchases(purchases, element_ids, supplier_ids):
    purchases = purchases.drop_duplicates(subset="transaction_id")
    purchases = purchases.dropna(subset=["quantity"])
    purchases = purchases[purchases["quantity"] > 0]
    purchases = purchases[purchases["element_id"].isin(element_ids)]
    purchases = purchases[purchases["supplier_id"].isin(supplier_ids)].copy()
    purchases["date"] = pd.to_datetime(purchases["date"])
    purchases["month"] = purchases["date"].dt.strftime("%Y-%m")
    return purchases.reset_index(drop=True)


# ————— Merge Data
def merge_data(purchases, prices, elements):
    merged = purchases.merge(prices, on=["supplier_id", "material"], how="left")
    merged = merged.merge(elements, on="element_id", how="left")
    print("Purchases without a price:", merged["unit_price"].isna().sum())
    print("Purchases without a site:", merged["site"].isna().sum())
    return merged


# ————— Add Cost
def add_cost(merged):
    merged = merged.copy()
    merged["cost"] = merged["quantity"] * merged["unit_price"]
    return merged


# ————— Cost Summary
def cost_summary(merged, columns):
    summary = merged.groupby(columns)["cost"].sum().round(2)
    return summary.reset_index()


# ————— Required Quantities
def required_quantities(elements):
    rows = []
    for element in elements:
        amounts = {"Cement": element.cement_kg(), "Sand": element.sand_m3(), "Aggregate": element.aggregate_m3()}
        for material, amount in amounts.items():
            rows.append([element.element_id, material, UNITS[material], amount])
    return pd.DataFrame(rows, columns=["element_id", "material", "unit", "required"])


# ————— Check Units
def check_units(prices):
    wrong = prices[prices["unit"] != prices["material"].map(UNITS)]
    if len(wrong) > 0:
        print("Rejected: wrong units in the price file")
        print(wrong)
        return False
    return True


# ————— Get Status
def get_status(difference):
    if difference < 0:
        return "Shortage"
    elif difference > 0:
        return "Surplus"
    return "Exact"


# ————— Compare Quantities
def compare_quantities(required, purchases):
    purchased = purchases.groupby(["element_id", "material"], as_index=False)["quantity"].sum()
    comparison = required.merge(purchased, on=["element_id", "material"], how="left")
    comparison = comparison.rename(columns={"quantity": "purchased"}).fillna(0)
    comparison[["required", "purchased"]] = comparison[["required", "purchased"]].round(2)
    comparison["difference"] = (comparison["purchased"] - comparison["required"]).round(2)
    comparison["status"] = comparison["difference"].apply(get_status)
    return comparison


# ————— Price Scenario
def price_scenario(required, prices, material, percent):
    material = material.strip().title()
    lowest = prices.groupby("material")["unit_price"].min()
    if material not in lowest.index:
        print("Rejected: unknown material", material)
        return None
    if percent <= 0:
        print("Rejected: the increase must be greater than zero.")
        return None

    quantities = required["required"].to_numpy()
    prices_before = required["material"].map(lowest).to_numpy()
    prices_after = np.where(required["material"].to_numpy() == material,
                            prices_before * (1 + percent / 100),
                            prices_before)

    result = required[["element_id", "material"]].copy()
    result["quantity"] = quantities
    result["price_before"] = prices_before
    result["price_after"] = prices_after
    result["cost_before"] = quantities * prices_before
    result["cost_after"] = quantities * prices_after
    return result


# ————— Scenario Summary
def scenario_summary(result):
    summary = result.groupby("material")[["cost_before", "cost_after"]].sum()
    summary["extra_cost"] = summary["cost_after"] - summary["cost_before"]
    return summary.round(2)


# ————— Save Chart
def save_chart(filename):
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()


# ————— Line Chart
def line_chart(data, filename):
    ordered = data.sort_values("date")
    cumulative = ordered["cost"].cumsum()
    plt.figure(figsize=(8, 5))
    plt.plot(ordered["date"], cumulative, marker="o")
    plt.title("Cumulative Purchase Cost Over Time")
    plt.xlabel("Purchase date")
    plt.ylabel(f"Cumulative cost ({CURRENCY})")
    plt.xticks(rotation=45)
    save_chart(filename)


# ————— Bar Chart
def bar_chart(data, filename):
    totals = data.groupby("element_id")["cost"].sum()
    plt.figure(figsize=(8, 5))
    plt.bar(totals.index, totals.values)
    plt.title("Purchase Cost per Element")
    plt.xlabel("Element ID")
    plt.ylabel(f"Total cost ({CURRENCY})")
    save_chart(filename)


# ————— Scatter Chart
def scatter_chart(comparison, filename):
    cement = comparison[comparison["material"] == "Cement"]
    top = max(cement["required"].max(), cement["purchased"].max())
    plt.figure(figsize=(6, 6))
    plt.scatter(cement["required"], cement["purchased"])
    plt.plot([0, top], [0, top], linestyle="--", label="Purchased = Required")
    plt.title("Cement: Required vs Purchased per Element")
    plt.xlabel("Required cement (kg)")
    plt.ylabel("Purchased cement (kg)")
    plt.legend()
    save_chart(filename)


# ————— Histogram
def histogram_chart(data, filename):
    plt.figure(figsize=(8, 5))
    plt.hist(data["cost"], bins=8)
    plt.title("Distribution of Purchase Cost per Transaction")
    plt.xlabel(f"Transaction cost ({CURRENCY})")
    plt.ylabel("Number of transactions")
    save_chart(filename)


# ————— Create Charts
def create_charts(data, comparison, folder):
    os.makedirs(folder, exist_ok=True)
    line_chart(data, os.path.join(folder, "Line_Chart_for_Cost.png"))
    bar_chart(data, os.path.join(folder, "Bar_Chart_per_Element.png"))
    scatter_chart(comparison, os.path.join(folder, "Scatter_Cement_Required_vs_Purchased.png"))
    histogram_chart(data, os.path.join(folder, "Histogram_Cost.png"))


# ————— Export Reports
def export_reports(data, comparison, scenario, folder):
    os.makedirs(folder, exist_ok=True)
    data.to_csv(os.path.join(folder, "purchases_with_cost.csv"), index=False)
    cost_summary(data, "site").to_csv(os.path.join(folder, "cost_per_site.csv"), index=False)
    cost_summary(data, "supplier_id").to_csv(os.path.join(folder, "cost_per_supplier.csv"), index=False)
    cost_summary(data, "month").to_csv(os.path.join(folder, "cost_per_month.csv"), index=False)
    cost_summary(data, ["site", "supplier_id", "month"]).to_csv(os.path.join(folder, "cost_per_site_supplier_month.csv"), index=False)
    comparison.to_csv(os.path.join(folder, "required_vs_purchased.csv"), index=False)
    scenario_summary(scenario).reset_index().to_csv(os.path.join(folder, "price_scenario.csv"), index=False)


# ————— Test
if __name__ == "__main__":
    folder = os.path.dirname(os.path.abspath(__file__))
    elements = load_elements(os.path.join(folder, "elements.csv"))
    prices = clean_prices(read_prices(os.path.join(folder, "prices.csv")))
    purchases = read_purchases(os.path.join(folder, "purchases.csv"))
    purchases = clean_purchases(purchases, {e.element_id for e in elements}, set(prices["supplier_id"]))

    element_table = read_elements(os.path.join(folder, "elements.csv"))
    data = add_cost(merge_data(purchases, prices, element_table))
    required = required_quantities(elements)

    if check_units(prices):
        comparison = compare_quantities(required, purchases)
        scenario = price_scenario(required, prices, "Cement", 10)
        export_reports(data, comparison, scenario, os.path.join(folder, "reports"))
        create_charts(data, comparison, os.path.join(folder, "charts"))
        print("Reports saved in the reports folder.")
        print("Charts saved in the charts folder.")
