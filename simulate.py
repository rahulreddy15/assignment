import requests
import random
import time
from datetime import datetime, timedelta
import uuid

# API endpoint
API_URL = "http://localhost:8000/events/"

# IKEA-specific data for random generation
IKEA_PRODUCT_CATEGORIES = [
    "Sofas & armchairs", "Beds & mattresses", "Storage & organization",
    "Tables & desks", "Cabinets & cupboards", "Lighting", "Textiles",
    "Decoration", "Kitchens", "Appliances", "Bathroom products"
]

COUNTRIES = ["USA", "UK", "France", "Germany", "Sweden", "Canada", "Australia"]
PROMOTION_TYPES = ["Discount", "BOGO", "Flash Sale", "Clearance", "Bundle"]

def generate_ikea_product_name():
    prefixes = ["BILLY", "MALM", "POÄNG", "KALLAX", "LACK", "HEMNES", "EXPEDIT", "IVAR", "EKTORP", "PIPPIG"]
    suffixes = ["shelf", "chair", "table", "lamp", "rug", "dresser", "sofa", "desk", "cabinet", "bookcase"]
    return f"{random.choice(prefixes)} {random.choice(suffixes)}"

def generate_product_update():
    return {
        "topic": "product_updates",
        "data": {
            "product_id": str(uuid.uuid4()),
            "name": generate_ikea_product_name(),
            "price": round(random.uniform(10, 1000), 2),
            "category": random.choice(IKEA_PRODUCT_CATEGORIES),
            "brand": "IKEA",
            "stock_quantity": random.randint(0, 1000),
            "weight": round(random.uniform(0.1, 100), 2),
            "dimensions": f"{random.randint(1, 100)}x{random.randint(1, 100)}x{random.randint(1, 100)}",
        }
    }

def generate_country_data():
    return {
        "topic": "country",
        "data": {
            "country_id": str(uuid.uuid4()),
            "name": random.choice(COUNTRIES),
            "manager": f"IKEA-Manager-{random.randint(1, 100)}",
            "product_count": random.randint(100, 10000),
            "total_sales": round(random.uniform(10000, 1000000), 2),
            "last_updated": datetime.now().isoformat()
        }
    }

def generate_product_promotion():
    return {
        "topic": "product_discounts",
        "data": {
            "product_id": str(uuid.uuid4()),
            "promotion_type": random.choice(PROMOTION_TYPES),
            "discount_percentage": round(random.uniform(5, 50), 2),
            "start_date": datetime.now().isoformat(),
            "end_date": (datetime.now() + timedelta(days=random.randint(1, 30))).isoformat(),
            "minimum_quantity": random.randint(1, 5),
            "maximum_discount": round(random.uniform(50, 500), 2) if random.choice([True, False]) else None
        }
    }

def simulate_api_calls(num_calls):
    for i in range(num_calls):
        event_type = random.choice(["product_update", "country", "product_discounts"])
        if event_type == "product_update":
            data = generate_product_update()
        elif event_type == "country":
            data = generate_country_data()
        else:
            data = generate_product_promotion()
        
        try:
            response = requests.post(API_URL, json=data)
            if response.status_code == 200:
                print(f"Call {i+1}: Event created successfully. Event ID: {response.json()['event_id']}")
            else:
                print(f"Call {i+1}: Failed to create event. Status code: {response.status_code}")
        except requests.RequestException as e:
            print(f"Call {i+1}: Error making request: {str(e)}")
        

if __name__ == "__main__":
    num_calls = 1000  # Adjust this number to simulate more or fewer calls
    simulate_api_calls(num_calls)