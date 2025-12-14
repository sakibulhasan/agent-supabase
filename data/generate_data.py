import random
import uuid
from datetime import datetime, timedelta
import calendar
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Initialize Supabase client
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')

if not SUPABASE_URL or not SUPABASE_ANON_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY must be set in .env file")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# -----------------------------
# CONFIG
# -----------------------------
START_YEAR = 2021
END_YEAR = 2025
END_MONTH = 11  # November
MIN_TX_PER_MONTH = 30

# Growth multipliers per year
YEAR_GROWTH = {
    2021: 1.00,
    2022: 1.12,
    2023: 1.27,
    2024: 1.45,
    2025: 1.67,
}

# Income items and categories
car_sales = [
    ("Mercedes S-Class", "Vehicle Sales"),
    ("BMW 7 Series", "Vehicle Sales"),
    ("Audi A8", "Vehicle Sales"),
    ("Lexus LS", "Vehicle Sales"),
    ("Genesis G90", "Vehicle Sales"),
    ("Porsche 911", "Vehicle Sales"),
    ("Chevrolet Corvette", "Vehicle Sales"),
    ("Nissan GT-R", "Vehicle Sales"),
    ("Aston Martin Vantage", "Vehicle Sales"),
    ("Ferrari Roma", "Vehicle Sales"),
    ("Tesla Model S", "Vehicle Sales"),
    ("Tesla Model X", "Vehicle Sales"),
    ("Porsche Taycan", "Vehicle Sales"),
    ("Mercedes EQS", "Vehicle Sales"),
    ("BMW i7", "Vehicle Sales")
]

service_items = [
    ("Oil Change & Filter Replacement", "Service Revenue"),
    ("Brake System Repair", "Service Revenue"),
    ("Engine Diagnostic & Tune-up", "Service Revenue"),
    ("Transmission Service", "Service Revenue"),
    ("Air Conditioning Repair", "Service Revenue"),
    ("Wheel Alignment & Balancing", "Service Revenue"),
    ("Battery Replacement", "Service Revenue"),
    ("Tire Rotation & Replacement", "Service Revenue"),
    ("Suspension Repair", "Service Revenue"),
    ("Detailing & Car Wash", "Service Revenue"),
    ("Paint & Body Work", "Service Revenue"),
    ("Electrical System Repair", "Service Revenue"),
    ("Premium Warranty Service", "Service Revenue"),
    ("Annual Vehicle Inspection", "Service Revenue")
]

parts_items = [
    ("Brake Pads & Rotors", "Parts Sales"),
    ("Engine Oil & Filters", "Parts Sales"),
    ("Spark Plugs & Ignition Coils", "Parts Sales"),
    ("Air Filters", "Parts Sales"),
    ("Wiper Blades", "Parts Sales"),
    ("Battery", "Parts Sales"),
    ("Alternator", "Parts Sales"),
    ("Starter Motor", "Parts Sales"),
    ("Radiator & Coolant", "Parts Sales"),
    ("Transmission Fluid", "Parts Sales"),
    ("Timing Belt", "Parts Sales"),
    ("Tires (Set of 4)", "Parts Sales"),
    ("Headlight Bulbs", "Parts Sales"),
    ("Cabin Air Filter", "Parts Sales"),
    ("Fuel Pump", "Parts Sales"),
    ("Oxygen Sensor", "Parts Sales")
]

service_providers = [
    "Premium Auto Care",
    "Elite Warranty Services",
    "Luxury Detailing Co.",
    None
]

vendors = [
    "AutoParts Co.",
    "Luxury Advertising",
    "Car Care Service",
    "Premium Transport Logistics",
    "DealerSoft Systems",
    "Elite Automotive Supplies"
]

customers = [
    "John Smith", "Alice Johnson", "David Lee", "Sophia Martinez",
    "Michael Brown", "Emma Wilson", "Daniel Thompson", "Olivia Taylor",
    "James Anderson", "Isabella Harris"
]

payment_methods = ["Credit Card", "Bank Transfer", "Financing"]

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------

def random_date_in_month(year, month):
    days = calendar.monthrange(year, month)[1]
    day = random.randint(1, days)
    return datetime(year, month, day).date()

def generate_income_transaction(year, month):
    # Randomly choose between car sales (60%), services (25%), or parts (15%)
    income_type = random.choices(
        ['car_sale', 'service', 'parts'],
        weights=[60, 25, 15],
        k=1
    )[0]
    
    if income_type == 'car_sale':
        item, category = random.choice(car_sales)
        base_price = random.randint(40000, 250000)
        unit_price = int(base_price * YEAR_GROWTH[year])
        quantity = random.choice([1, 1, 1, 2])  # mostly 1, sometimes 2
        
        # Discount or markup
        if random.random() < 0.2:
            list_price = unit_price + random.randint(2000, 8000)
        elif random.random() < 0.4:
            list_price = unit_price - random.randint(1000, 5000)
        else:
            list_price = None
            
    elif income_type == 'service':
        item, category = random.choice(service_items)
        base_price = random.randint(100, 5000)
        unit_price = int(base_price * YEAR_GROWTH[year])
        quantity = 1
        list_price = None
        
    else:  # parts
        item, category = random.choice(parts_items)
        base_price = random.randint(50, 3000)
        unit_price = int(base_price * YEAR_GROWTH[year])
        quantity = random.choice([1, 1, 2, 3, 4])
        list_price = None

    total_price = unit_price * quantity

    return {
        "id": str(uuid.uuid4()),
        "date": str(random_date_in_month(year, month)),
        "item": item,
        "category": category,
        "quantity": quantity,
        "unit_price": unit_price,
        "list_price": list_price,
        "total_price": total_price,
        "customer": random.choice(customers),
        "service_provider": random.choice(service_providers),
        "payment_method": random.choice(payment_methods),
        "notes": None
    }

def generate_expense_transaction(year, month):
    item = random.choice([
        "Inventory Purchase", "Maintenance Service", "Vendor Payment",
        "Advertising Campaign", "Transport Fee", "Software Subscription"
    ])

    category = item
    unit_price = int(random.randint(500, 10000) * YEAR_GROWTH[year])
    quantity = random.choice([1, 1, 2, 3, 5, 10])
    list_price = unit_price
    total_price = unit_price * quantity

    return {
        "id": str(uuid.uuid4()),
        "date": str(random_date_in_month(year, month)),
        "item": item,
        "category": category,
        "quantity": quantity,
        "unit_price": unit_price,
        "list_price": list_price,
        "total_price": total_price,
        "vendor": random.choice(vendors),
        "payment_method": random.choice(payment_methods),
        "notes": None
    }

# -----------------------------
# MAIN GENERATION LOOP
# -----------------------------
income_batch = []
expense_batch = []
total_income = 0
total_expense = 0

print("Starting data generation and insertion...")

for year in range(START_YEAR, END_YEAR + 1):
    for month in range(1, 13):
        if year == END_YEAR and month > END_MONTH:
            break

        tx_count = random.randint(MIN_TX_PER_MONTH, MIN_TX_PER_MONTH + 20)

        print(f"Generating data for {year}-{month:02d}... ({tx_count} transactions each)")

        # Income transactions
        for _ in range(tx_count):
            income_batch.append(generate_income_transaction(year, month))
            
            # Insert in batches of 100
            if len(income_batch) >= 100:
                try:
                    supabase.table('transactions_income').insert(income_batch).execute()
                    total_income += len(income_batch)
                    print(f"  ✓ Inserted {len(income_batch)} income transactions (Total: {total_income})")
                    income_batch = []
                except Exception as e:
                    print(f"  ✗ Error inserting income transactions: {e}")
                    income_batch = []

        # Expense transactions
        for _ in range(tx_count):
            expense_batch.append(generate_expense_transaction(year, month))
            
            # Insert in batches of 100
            if len(expense_batch) >= 100:
                try:
                    supabase.table('transactions_expense').insert(expense_batch).execute()
                    total_expense += len(expense_batch)
                    print(f"  ✓ Inserted {len(expense_batch)} expense transactions (Total: {total_expense})")
                    expense_batch = []
                except Exception as e:
                    print(f"  ✗ Error inserting expense transactions: {e}")
                    expense_batch = []

# Insert remaining records
if income_batch:
    try:
        supabase.table('transactions_income').insert(income_batch).execute()
        total_income += len(income_batch)
        print(f"  ✓ Inserted {len(income_batch)} income transactions (Total: {total_income})")
    except Exception as e:
        print(f"  ✗ Error inserting final income transactions: {e}")

if expense_batch:
    try:
        supabase.table('transactions_expense').insert(expense_batch).execute()
        total_expense += len(expense_batch)
        print(f"  ✓ Inserted {len(expense_batch)} expense transactions (Total: {total_expense})")
    except Exception as e:
        print(f"  ✗ Error inserting final expense transactions: {e}")

# -----------------------------
# OUTPUT
# -----------------------------
print("\n" + "="*60)
print("DATA GENERATION COMPLETE!")
print("="*60)
print(f"Total Income Transactions: {total_income}")
print(f"Total Expense Transactions: {total_expense}")
print(f"Grand Total: {total_income + total_expense}")
print("="*60)
