import pandas as pd

# Load CSV safely
df = pd.read_csv("final.csv", dtype=str)

# Clean known junk values
BAD_VALUES = ["Published", "published", "", "null", "None"]

for col in ["publishDate", "firstPublishDate"]:
    if col in df.columns:
        df[col] = df[col].replace(BAD_VALUES, pd.NA)

        # Convert with coercion (invalid -> NaT)
        df[col] = pd.to_datetime(
            df[col],
            format="%m/%d/%y",
            errors="coerce"
        )

        # Log bad rows
        bad_rows = df[df[col].isna()]
        if not bad_rows.empty:
            print(f"⚠️ Invalid values detected in {col}:")
            print(bad_rows[[col]].head())

        # Convert to Solr ISO format
        df[col] = df[col].dt.strftime("%Y-%m-%dT00:00:00Z")

# Save cleaned file
df.to_csv("final_fixed.csv", index=False)

print("✅ final_fixed.csv generated successfully")
