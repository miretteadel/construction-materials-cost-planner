# ————— Imports
import os
import numpy as np
import module1_quantity as m1
import module2_costs as m2


# ————— Folders
folder = os.path.dirname(os.path.abspath(__file__))
reports_folder = os.path.join(folder, "reports")
charts_folder = os.path.join(folder, "charts")


# ————— Menu Text
MENU = """
===== Construction Materials Cost Planner =====
MODULE 1: Material Quantities
  1. List elements
  2. Add element
  3. Search element
  4. Update element
  5. Show quantities per element and site
  6. Save Module 1 CSV files
MODULE 2: Purchases and Costs
  7. Show purchase costs (site, supplier, month)
  8. Compare required and purchased quantities
  9. Price increase scenario
 10. Export reports and charts
 11. Preview first 3 and last elements
  0. Exit
"""


# ————— Ask Number
def ask_number(text):
    try:
        return float(input(text))
    except ValueError:
        print("Rejected: please enter a number.")
        return None


# ————— Add Menu
def add_menu(elements):
    element_id = input("Element ID: ").strip()
    name = input("Name: ").strip()
    site = input("Site: ").strip()
    length = ask_number("Length (m): ")
    width = ask_number("Width (m): ")
    height = ask_number("Height (m): ")
    waste_pct = ask_number("Waste percentage (0 to 100): ")
    if None in (length, width, height, waste_pct):
        return
    if m1.add_element(elements, element_id, name, site, length, width, height, waste_pct):
        print("Element added.")


# ————— Search Menu
def search_menu(elements):
    element_id = input("Element ID to search: ").strip()
    element = m1.search_element(elements, element_id)
    if element is None:
        print("Element not found.")
    else:
        print(element)


# ————— Update Menu
def update_menu(elements):
    element_id = input("Element ID to update: ").strip()
    field = input("Field (name, site, length, width, height, waste_pct): ").strip()
    if field in ("name", "site"):
        new_value = input("New value: ").strip()
    else:
        new_value = ask_number("New value: ")
        if new_value is None:
            return
    m1.update_element(elements, element_id, field, new_value)


# ————— Save Module 1 Files
def save_module1_files(elements):
    os.makedirs(reports_folder, exist_ok=True)
    m1.save_elements(elements, os.path.join(reports_folder, "elements_saved.csv"))
    m1.save_quantities(elements, os.path.join(reports_folder, "quantities_per_element.csv"))
    m1.save_site_totals(elements, os.path.join(reports_folder, "quantities_per_site.csv"))
    print("Saved 3 files in the reports folder.")


# ————— Load Analysis
def load_analysis(elements):
    prices = m2.read_prices(os.path.join(folder, "prices.csv"))
    purchases = m2.read_purchases(os.path.join(folder, "purchases.csv"))
    if prices is None or purchases is None:
        return None
    prices = m2.clean_prices(prices)
    purchases = m2.clean_purchases(purchases, m1.existing_ids(elements), set(prices["supplier_id"]))
    data = m2.add_cost(m2.merge_data(purchases, prices, m2.elements_to_table(elements)))
    return prices, purchases, data


# ————— Show Costs
def show_costs(elements):
    analysis = load_analysis(elements)
    if analysis is None:
        return
    prices, purchases, data = analysis
    for column in ["site", "supplier_id", "month"]:
        print("Cost per", column)
        print(m2.cost_summary(data, column))
        print()
    print("Total cost:", round(data["cost"].sum(), 2))


# ————— Show Comparison
def show_comparison(elements):
    analysis = load_analysis(elements)
    if analysis is None:
        return
    prices, purchases, data = analysis
    if m2.check_units(prices):
        comparison = m2.compare_quantities(m2.required_quantities(elements), purchases)
        print(comparison)
        print()
        print(comparison["status"].value_counts())


# ————— Show Scenario
def show_scenario(elements):
    analysis = load_analysis(elements)
    if analysis is None:
        return
    prices, purchases, data = analysis
    material = input("Material (Cement, Sand, Aggregate): ").strip()
    percent = ask_number("Price increase (%): ")
    if percent is None or not m2.check_units(prices):
        return
    result = m2.price_scenario(m2.required_quantities(elements), prices, material, percent)
    if result is not None:
        print(m2.scenario_summary(result))
        total_before = np.sum(result["cost_before"].to_numpy())
        total_after = np.sum(result["cost_after"].to_numpy())
        print("Total before:", round(total_before, 2))
        print("Total after:", round(total_after, 2))
        print("Increase:", round(total_after - total_before, 2))


# ————— Export All
def export_all(elements):
    analysis = load_analysis(elements)
    if analysis is None:
        return
    prices, purchases, data = analysis
    material = input("Material for the price scenario (Cement, Sand, Aggregate): ").strip()
    percent = ask_number("Price increase (%): ")
    if percent is None or not m2.check_units(prices):
        return
    required = m2.required_quantities(elements)
    scenario = m2.price_scenario(required, prices, material, percent)
    if scenario is None:
        return
    comparison = m2.compare_quantities(required, purchases)
    m2.export_reports(data, comparison, scenario, reports_folder)
    m2.create_charts(data, comparison, charts_folder)
    print("Reports saved in the reports folder.")
    print("Charts saved in the charts folder.")


# ————— Main
def main():
    elements = m1.load_elements(os.path.join(folder, "elements.csv"))
    while True:
        print(MENU)
        choice = input("Choose an option: ").strip()
        if choice == "1":
            m1.list_elements(elements)
        elif choice == "2":
            add_menu(elements)
        elif choice == "3":
            search_menu(elements)
        elif choice == "4":
            update_menu(elements)
        elif choice == "5":
            m1.print_quantities(elements)
            print()
            m1.print_site_totals(elements)
        elif choice == "6":
            save_module1_files(elements)
        elif choice == "7":
            show_costs(elements)
        elif choice == "8":
            show_comparison(elements)
        elif choice == "9":
            show_scenario(elements)
        elif choice == "10":
            export_all(elements)
        elif choice == "11":
            m1.preview_elements(elements)
        elif choice == "0":
            print("Goodbye.")
            break
        else:
            print("Rejected: choose a number from the menu.")


# ————— Run
if __name__ == "__main__":
    main()
