from pathlib import Path
import csv, random

OUT = Path(__file__).parent / "properties.csv"
random.seed(42)

cities = {
    "London":   {"base": 1600, "per_bed": 550, "noise": 300},
    "Manchester":{"base": 900, "per_bed": 350, "noise": 220},
    "Birmingham":{"base": 1000,"per_bed": 320, "noise": 210},
    "Newcastle":{"base": 800, "per_bed": 280, "noise": 200},
}
types = ["Studio","Apartment","Flat","House","Terrace","Semi-Detached","Detached"]
titles = {
    "London": [
        "Flat near Canary Wharf","Zone 2 Apartment","Southwest Terrace","North London Flat",
        "Riverside Apartment","Suburban House","East End Studio"
    ],
    "Manchester": [
        "City Centre Apartment","MediaCityUK Flat","Didsbury House","Castlefield Studio",
        "Salford Quays Apartment","Northern Quarter Flat"
    ],
    "Birmingham": [
        "Edgbaston House","City Core Apartment","Harborne Terrace","Jewellery Quarter Flat",
        "Bournville House","Sutton Coldfield Semi-Detached"
    ],
    "Newcastle": [
        "Quayside Studio","Jesmond Flat","Heaton House","City Centre Apartment",
        "Sandyford Terrace","Ouseburn Flat"
    ],
}

def gen_listing(i, city):
    p = cities[city]
    bedrooms = random.choices([0,1,2,3,4], weights=[10,25,35,22,8])[0]
    area = max(20, int(random.gauss(35 + bedrooms*20, 8)))
    typ = random.choice(types)
    title = f"{bedrooms if bedrooms>0 else 'Studio'} Bed {random.choice(titles[city]) if bedrooms>0 else random.choice(titles[city])}"
    price = int(p["base"] + p["per_bed"]*bedrooms + random.gauss(0, p["noise"]))
    price = max(450, price)
    return {
        "id": i,
        "title": title,
        "city": city,
        "bedrooms": bedrooms,
        "price": price,
        "area_m2": area,
        "type": typ
    }

def main(n=200):
    rows = []
    i = 1
    # balanced per city
    per_city = n // len(cities)
    for city in cities.keys():
        for _ in range(per_city):
            rows.append(gen_listing(i, city)); i += 1
    # write
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id","title","city","bedrooms","price","area_m2","type"])
        w.writeheader()
        for r in rows: w.writerow(r)
    print(f"Wrote {len(rows)} rows to {OUT}")

if __name__ == "__main__":
    main(200)
# backend/generate_data.py
from pathlib import Path
import csv, random

OUT = Path(__file__).parent / "properties.csv"
random.seed(42)

cities = {
    "London":    {"base": 1700, "per_bed": 600, "noise": 320},
    "Manchester":{"base": 1000, "per_bed": 360, "noise": 220},
    "Birmingham":{"base": 1050, "per_bed": 340, "noise": 210},
    "Newcastle": {"base":  850, "per_bed": 300, "noise": 190},
    "Leeds":     {"base":  980, "per_bed": 330, "noise": 200},
    "Liverpool": {"base":  900, "per_bed": 310, "noise": 190},
    "Bristol":   {"base": 1300, "per_bed": 420, "noise": 240},
    "Edinburgh": {"base": 1400, "per_bed": 430, "noise": 250},
    "Glasgow":   {"base": 1100, "per_bed": 360, "noise": 210},
}
types = ["Studio","Apartment","Flat","House","Terrace","Semi-Detached","Detached"]

def gen_listing(i, city):
    p = cities[city]
    bedrooms = random.choices([0,1,2,3,4], weights=[10,25,35,22,8])[0]
    area = max(20, int(random.gauss(35 + bedrooms*20, 8)))
    typ = random.choice(types)
    # Title that reads well in cards
    title = f"{'Studio' if bedrooms==0 else str(bedrooms)+' Bed'} {typ} in {city}"
    price = int(p["base"] + p["per_bed"]*bedrooms + random.gauss(0, p["noise"]))
    return {
        "id": i, "title": title, "city": city,
        "bedrooms": bedrooms, "price": max(450, price),
        "area_m2": area, "type": typ
    }

def main(n=360):  # ~40 each x 9 cities
    rows = []; i = 1
    per_city = n // len(cities)
    for city in cities:
        for _ in range(per_city):
            rows.append(gen_listing(i, city)); i += 1
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["id","title","city","bedrooms","price","area_m2","type"])
        w.writeheader(); w.writerows(rows)
    print(f"Wrote {len(rows)} rows to {OUT}")

if __name__ == "__main__":
    main()
