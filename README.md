# Construction Materials Cost Planner

**Student name:** Mirette Adel Farag
**Course:** C60 Artificial Intelligence: Theory and Applications, Faculty of Engineering, Cairo University (Assignment 02)

## Project description

A Python application with two connected modules, joined by a menu in `main.py`:

- **Module 1: Material Quantity Calculator** (`module1_quantity.py`). A `ConcreteElement` class stores the ID, name, site, length, width, height, and waste percentage of a concrete element. Users can add, list, search for, and update elements. The module calculates the concrete volume (including waste) and the cement, sand, and aggregate needed per element and per site, and saves the results to CSV files.
- **Module 2: Purchase and Cost Analysis** (`module2_costs.py`). It reads the price and purchase files with pandas, cleans them (duplicates, missing values, unknown IDs), merges the tables, and calculates the purchase cost per site, supplier, and month. It compares the required quantities (from Module 1) with the purchased quantities, tests a price increase with NumPy, creates four Matplotlib charts, and exports reports as CSV and charts as PNG.

Formulas (training rates from the assignment):

- Net volume (m3) = length x width x height
- Volume with waste = net volume x (1 + waste / 100)
- Per 1 m3 with waste: 300 kg cement, 0.5 m3 sand, 0.8 m3 aggregate
- Cost = quantity x unit price

## Project structure

```
main.py                 menu that connects the two modules
module1_quantity.py     Module 1
module2_costs.py        Module 2
analysis_notebook.ipynb short notebook explaining the analysis and the tests
elements.csv            sample data: 8 elements, 2 sites
prices.csv              sample data: 3 materials, 2 suppliers each
purchases.csv           sample data: 40 purchase lines, 2 months
reports/                CSV reports created by the program
charts/                 PNG charts created by the program
requirements.txt        required libraries
```

## Required libraries

- Python 3.10 or newer
- pandas
- numpy
- matplotlib
- notebook (only to open the notebook)

Install them with:

```
pip install -r requirements.txt
```

## How to run

1. Put all files in one folder, with the three CSV files next to the code.
2. Open a terminal in that folder and run:

```
python main.py
```

3. Choose an option from the menu:

| Option | Action |
|---|---|
| 1 | List elements |
| 2 | Add element |
| 3 | Search element |
| 4 | Update element |
| 5 | Show quantities per element and per site |
| 6 | Save element and quantity CSV files (Module 1) |
| 7 | Purchase costs per site, supplier, and month |
| 8 | Required vs purchased quantities (shortage or surplus) |
| 9 | Price increase scenario (choose a material and a percentage) |
| 10 | Export all reports (CSV) and charts (PNG) |
| 11 | Preview the first 3 and the last element |
| 0 | Exit |

To open the notebook:

```
jupyter notebook analysis_notebook.ipynb
```

## Input validation

- Length, width, and height must be greater than zero.
- Waste percentage must be between 0 and 100.
- Duplicate element IDs are rejected, and updating an unknown ID is rejected.
- Prices and purchase quantities must be greater than zero.
- Duplicate transaction IDs are removed, and purchases that refer to an unknown element or supplier are removed.
- Rows with a missing quantity are removed (a cost cannot be calculated without a quantity).
- The price file units must match the expected units (cement in kg, sand and aggregate in m3).

## Sample data results

- 40 purchase lines become 35 after cleaning (2 duplicate transactions and 3 missing quantities removed).
- Total purchase cost: 2320.35 (Site A 712.32, Site B 1608.02).
- Required vs purchased: 12 shortages, 11 surpluses, 1 exact (24 element-material rows).
- Cement price +10%: the estimated cost of the required quantities increases by 140.43.

## Tests

The notebook (`analysis_notebook.ipynb`, section 7) runs 3 valid and 3 invalid cases and records the expected and actual results. All 6 pass.
