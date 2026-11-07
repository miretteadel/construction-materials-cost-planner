# ————— Imports
import csv


# ————— Rates
CEMENT_PER_M3 = 300
SAND_PER_M3 = 0.5
AGGREGATE_PER_M3 = 0.8

DIMENSION_FIELDS = ("length", "width", "height")
EDITABLE_FIELDS = ("name", "site", "length", "width", "height", "waste_pct")


# ————— Element Class
class ConcreteElement:
    def __init__(self, element_id, name, site, length, width, height, waste_pct):
        self.element_id = element_id
        self.name = name
        self.site = site
        self.length = length
        self.width = width
        self.height = height
        self.waste_pct = waste_pct

    def __str__(self):
        return (f"{self.element_id} | {self.name} | {self.site} | "
                f"{self.length}m x {self.width}m x {self.height}m | "
                f"waste {self.waste_pct}%")

    # ————— Element Calculations
    def net_volume(self):
        return self.length * self.width * self.height

    def volume_with_waste(self):
        return self.net_volume() * (1 + self.waste_pct / 100)

    def cement_kg(self):
        return self.volume_with_waste() * CEMENT_PER_M3

    def sand_m3(self):
        return self.volume_with_waste() * SAND_PER_M3

    def aggregate_m3(self):
        return self.volume_with_waste() * AGGREGATE_PER_M3


# ————— Validation
def check_values(length, width, height, waste_pct):
    for value in (length, width, height):
        if value <= 0:
            return False, "Dimensions must be greater than zero."
    if waste_pct < 0 or waste_pct > 100:
        return False, "Waste percentage must be between 0 and 100."
    return True, "OK"


# ————— Sets (IDs and Sites)
def existing_ids(elements):
    ids = set()
    for element in elements:
        ids.add(element.element_id)
    return ids


def unique_sites(elements):
    sites = set()
    for element in elements:
        sites.add(element.site)
    return sites


# ————— Add Element
def add_element(elements, element_id, name, site, length, width, height, waste_pct):
    if element_id in existing_ids(elements):
        print("Rejected: duplicate ID", element_id)
        return False
    ok, message = check_values(length, width, height, waste_pct)
    if not ok:
        print("Rejected:", element_id, "-", message)
        return False
    element = ConcreteElement(element_id, name, site, length, width, height, waste_pct)
    elements.append(element)
    return True


# ————— Load Elements
def load_elements(filename):
    elements = []
    with open(filename, newline="") as file:
        for row in csv.DictReader(file):
            add_element(
                elements,
                row["element_id"],
                row["element_name"],
                row["site"],
                float(row["length_m"]),
                float(row["width_m"]),
                float(row["height_m"]),
                float(row["waste_pct"]),
            )
    return elements


# ————— List Elements
def list_elements(elements):
    for element in elements:
        print(element)


# ————— Preview Elements (Indexing and Slicing)
def preview_elements(elements, count=3):
    if len(elements) == 0:
        print("No elements.")
        return
    print("First", count, "elements:")
    for element in elements[:count]:
        print(element)
    print("Last element:", elements[-1])


# ————— Search Element
def search_element(elements, element_id):
    for element in elements:
        if element.element_id == element_id:
            return element
    return None


# ————— Update Element
def update_element(elements, element_id, field, new_value):
    element = search_element(elements, element_id)
    if element is None:
        print("Rejected: unknown ID", element_id)
        return False
    if field not in EDITABLE_FIELDS:
        print("Rejected: field", field, "cannot be updated")
        return False
    if field in DIMENSION_FIELDS and new_value <= 0:
        print("Rejected: dimensions must be greater than zero.")
        return False
    if field == "waste_pct" and (new_value < 0 or new_value > 100):
        print("Rejected: waste percentage must be between 0 and 100.")
        return False
    setattr(element, field, new_value)
    print("Updated:", element)
    return True


# ————— Quantities Per Element
def print_quantities(elements):
    for element in elements:
        print(f"{element.element_id} | {element.name} | "
              f"net {element.net_volume():.2f} m3 | "
              f"with waste {element.volume_with_waste():.2f} m3 | "
              f"cement {element.cement_kg():.2f} kg | "
              f"sand {element.sand_m3():.2f} m3 | "
              f"aggregate {element.aggregate_m3():.2f} m3")


# ————— Totals Per Site
def site_totals(elements):
    totals = {}
    for element in elements:
        if element.site not in totals:
            totals[element.site] = {"volume": 0, "cement": 0, "sand": 0, "aggregate": 0}
        totals[element.site]["volume"] += element.volume_with_waste()
        totals[element.site]["cement"] += element.cement_kg()
        totals[element.site]["sand"] += element.sand_m3()
        totals[element.site]["aggregate"] += element.aggregate_m3()
    return totals


# ————— Print Site Totals
def print_site_totals(elements):
    totals = site_totals(elements)
    for site, values in totals.items():
        print(f"{site} | volume {values['volume']:.2f} m3 | "
              f"cement {values['cement']:.2f} kg | "
              f"sand {values['sand']:.2f} m3 | "
              f"aggregate {values['aggregate']:.2f} m3")


# ————— Save CSV
def save_csv(filename, header, rows):
    with open(filename, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(rows)


# ————— Save Elements
def save_elements(elements, filename):
    header = ["element_id", "element_name", "site", "length_m", "width_m", "height_m", "waste_pct"]
    rows = []
    for element in elements:
        rows.append([element.element_id, element.name, element.site,
                     element.length, element.width, element.height, element.waste_pct])
    save_csv(filename, header, rows)


# ————— Save Quantities
def save_quantities(elements, filename):
    header = ["element_id", "element_name", "site", "net_volume_m3", "volume_with_waste_m3",
              "cement_kg", "sand_m3", "aggregate_m3"]
    rows = []
    for element in elements:
        rows.append([element.element_id, element.name, element.site,
                     round(element.net_volume(), 2), round(element.volume_with_waste(), 2),
                     round(element.cement_kg(), 2), round(element.sand_m3(), 2),
                     round(element.aggregate_m3(), 2)])
    save_csv(filename, header, rows)


# ————— Save Site Totals
def save_site_totals(elements, filename):
    header = ["site", "volume_with_waste_m3", "cement_kg", "sand_m3", "aggregate_m3"]
    rows = []
    for site, values in site_totals(elements).items():
        rows.append([site, round(values["volume"], 2), round(values["cement"], 2),
                     round(values["sand"], 2), round(values["aggregate"], 2)])
    save_csv(filename, header, rows)
