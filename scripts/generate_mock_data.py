import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set random seed for reproducibility
np.random.seed(42)

# Define categories with typical expenses
categories = [
    'Housing',
    'Groceries',
    'Restaurants',
    'Transportation',
    'Entertainment',
    'Shopping',
    'Healthcare',
    'Utilities',
    'Travel',
    'Education',
    'Fitness',
    'Insurance',
    'Nomina'
]

# Define typical amounts for each category
category_amounts = {
    'Housing': (800, 1200),      # Rent/Mortgage
    'Groceries': (200, 400),     # Weekly groceries
    'Restaurants': (20, 100),    # Dining out
    'Transportation': (50, 150),  # Gas, public transport
    'Entertainment': (20, 80),    # Movies, events
    'Shopping': (50, 200),       # Clothes, electronics
    'Healthcare': (30, 200),     # Medical expenses
    'Utilities': (100, 200),     # Electric, water, internet
    'Travel': (200, 1000),       # Vacations
    'Education': (50, 300),      # Books, courses
    'Fitness': (30, 80),         # Gym, equipment
    'Insurance': (50, 150),      # Various insurance
    'Nomina': (1000, 1000)       # Nomina
}

# Define transaction types
transaction_types = ['Ingress', 'Expense']

# Generate data for the last 3 years
end_date = datetime.now()
start_date = end_date - timedelta(days=3*365)
dates = pd.date_range(start=start_date, end=end_date, freq='D')

# Create empty lists to store data
records = []

# Generate transactions
for date in dates:
    # Random number of transactions per day (1-5)
    num_transactions = random.randint(1, 5)
    
    for _ in range(num_transactions):
        category = random.choice(categories)
        min_amount, max_amount = category_amounts[category]
        amount = round(random.uniform(min_amount, max_amount), 2)
        
        # Generate random time for the day
        hour = random.randint(8, 22)
        minute = random.randint(0, 59)
        datetime_with_time = date.replace(hour=hour, minute=minute)
        
        # For Ingress type, use positive amounts; for Expense type, use negative amounts
        transaction_type = random.choice(transaction_types)
        if category == 'Nomina':
            transaction_type = 'Ingress'
        
        records.append({
            'Date & time': datetime_with_time,
            'Purpose': f'{category} {"income" if transaction_type == "Ingress" else "expense"}',
            'Type': transaction_type,
            'Category': category,
            'Month': date.month,
            'Year': date.year,
            'Amount': amount
        })

# Create DataFrame
df = pd.DataFrame(records)

# Sort by date
df = df.sort_values('Date & time')

# Save to Excel
output_file = 'data/expenses_mock.xlsx'
df.to_excel(output_file, index=False)

print(f"Mock data generated and saved to {output_file}") 
