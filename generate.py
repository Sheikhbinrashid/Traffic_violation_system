# generate_data.py
"""
Generates a CSV file with synthetic red-light violation records for testing.
Fields: timestamp, city, ID, plate
Usage: python generate_data.py
"""
import pandas as pd
import random
from datetime import datetime, timedelta

# Configuration
OUTPUT_CSV = 'sample_violations_2000.csv'
NUM_ENTRIES = 2000
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime.now()
TOWNS = [
    'Harare', 'Bulawayo', 'Mutare', 'Gweru', 'Kadoma', 'Chinhoyi',
    'Bindura', 'Marondera', 'Norton', 'Masvingo', 'Chiredzi',
    'Mutoko', 'Chipinge', 'Rusape'
]


def random_date(start, end):
    """Return a random datetime between start and end."""
    delta = end - start
    seconds = random.randrange(int(delta.total_seconds()))
    return start + timedelta(seconds=seconds)


def random_plate():
    """Generate a random Zimbabwean-style license plate (e.g. 'ABC 1234')."""
    letters = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=3))
    numbers = ''.join(random.choices('0123456789', k=4))
    return f"{letters} {numbers}"


def main():
    # Build dataset
    data = {
        'timestamp': [random_date(START_DATE, END_DATE) for _ in range(NUM_ENTRIES)],
        'city': [random.choice(TOWNS) for _ in range(NUM_ENTRIES)],
        'ID': list(range(1, NUM_ENTRIES + 1)),
        'plate': [random_plate() for _ in range(NUM_ENTRIES)]
    }
    df = pd.DataFrame(data)
    df.sort_values('timestamp', inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Save to CSV
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Generated {NUM_ENTRIES} records and saved to {OUTPUT_CSV}")


if __name__ == '__main__':
    main()
