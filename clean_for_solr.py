import pandas as pd
import re

df = pd.read_csv("price_updated.csv")
df["price"] = (
    df["price"].astype(str)
    .str.replace(".", "", regex=False)  
    .str.replace(",", ".", regex=False)  
)

df["pages"] = df["pages"].astype(str).apply(lambda x: re.findall(r'\d+', x)[0] if re.findall(r'\d+', x) else None)

df.to_csv("final.csv", index=False)
