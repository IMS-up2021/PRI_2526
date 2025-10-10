import pandas as pd
from price_scrapper import get_price_by_isbn_from_directtextbook

def normalize_price(price_str: str) -> float:
    if not price_str:
        return 0.0

    price_str = price_str.replace(',', '.').replace('€', '').replace('$', '').strip()

    try:
        return float(price_str)
    except ValueError:
        return 0.0

data = []
df = pd.read_csv("ficheiro_limpo.csv", dtype=str)

for _, row in df.iterrows():
    row_dict = row.to_dict()
    row_dict['isbn'] = row_dict['isbn']
    data.append(row_dict)

for item in data:
    print("Processing item with ISBN:", item['isbn'])
    print("Current price:", item['price'])
    price_str = str(item['price']).strip().lower()
    if price_str not in ['', '0', '0.0', 'nan', 'none']:
        continue  # Skip if price already exists and is not zero/empty/nan
    print("Fetching price...")
    print("Fetching price...")
    retries = 3
    print("Fetching price...")
    numStr = None
    # Clean ISBN: cast to str and remove trailing '.0' if present
    clean_isbn = str(item['isbn']).replace('.0', '')
    for attempt in range(retries):
        print(f"Fetching price for ISBN: {clean_isbn} (Attempt {attempt+1})")
        numStr = get_price_by_isbn_from_directtextbook(clean_isbn)
        print(f"Attempt {attempt+1}: Price found:", numStr)
        if numStr is not None:
            break
        print("Price not found, retrying...")
    if numStr:
        item['price'] = normalize_price(numStr)
    else:
        # drop item if no price found after retries
        print(f"No price found for ISBN {clean_isbn} after {retries} attempts. Dropping item.")
        item['price'] = 0.0


for item in data:
    if item['price'] == 0.0:
        data.remove(item)

# export data to csv
df_out = pd.DataFrame(data)
df_out.to_csv("price_updated.csv", index=False)