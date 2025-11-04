import pandas as pd
import os

CSV_FILE = "final.csv"
OUTPUT_DIR = "config"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "qrels.txt")

os.makedirs(OUTPUT_DIR, exist_ok=True)

df = pd.read_csv(CSV_FILE)


topics = {
    1: ("Fantasy", df["genres"].str.contains("Fantasy", case=False, na=False)),
    2: ("Rating >= 4.5", df["rating"] >= 4.5),
    3: ("Author: J.K. Rowling", df["author"].str.contains("J.K. Rowling", case=False, na=False)),
}

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write("# topic_id  Q0  doc_id  relevance\n")
    for topic_id, (desc, mask) in topics.items():
        relevant_docs = df[mask]
        f.write(f"# Topic {topic_id}: {desc}\n")
        for doc_id in relevant_docs["bookId"]:
            f.write(f"{topic_id} Q0 {doc_id} 1\n")

