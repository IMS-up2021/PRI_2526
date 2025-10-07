import pandas as pd
from price_scrapper import get_amazon_price_by_isbn, _fix_scientific_str

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
    row_dict['isbn'] = _fix_scientific_str(row_dict['isbn'])
    data.append(row_dict)

for item in data:
    print(item['bookId'], _fix_scientific_str(item['isbn']))
    numStr = get_amazon_price_by_isbn(_fix_scientific_str(item['isbn']))
    if numStr:
        item['price'] = normalize_price(numStr)
    else:
        item['price'] = 0.0 

# export data to csv
df_out = pd.DataFrame(data)
df_out.to_csv("price_updated.csv", index=False)