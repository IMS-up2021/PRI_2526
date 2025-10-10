import pandas as pd
from isbn_checker import is_isbn_valid

input_file = "books_1.Best_Books_Ever.csv"
output_file = "ficheiro_limpo.csv"
df = pd.read_csv(input_file, dtype=str, low_memory=False)

# only lines without letters in isbn
mask_valid_isbn = df["isbn"].str.fullmatch(r"\d+")

# ISBN valid for values different from 9999999999999
mask_not_fake_isbn = df["isbn"] != "9999999999999"

# ISBN must be valid according to is_isbn_valid
mask_isbn_checker = df["isbn"].apply(is_isbn_valid)

# Combine all conditions
df = df[mask_valid_isbn & mask_not_fake_isbn & mask_isbn_checker]

# Deleted blank values in firstPublishDate
df = df.dropna(subset=["firstPublishDate"])

# Deleted edition column
df = df.drop(columns=["edition"])

df.to_csv(output_file, index=False)

# just to check how many lines were updated
print("Linhas atualizadas:", len(df))