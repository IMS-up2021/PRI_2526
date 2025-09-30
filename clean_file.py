import pandas as pd

input_file = "books_1.Best_Books_Ever.csv"
output_file = "ficheiro_limpo.csv"
df = pd.read_csv(input_file, dtype=str, low_memory=False)

# only lines without letters in isbn
mask_valid_isbn = df["isbn"].str.fullmatch(r"\d+")

# ISBN valid for values different from 9999999999999
df = df[mask_valid_isbn & (df["isbn"] != "9999999999999")]

# Deleted blank values in firstPublishDate
df = df.dropna(subset=["firstPublishDate"])

df.to_csv(output_file, index=False)

# just to check how many lines were updated
print("Linhas atualizadas:", len(df))
