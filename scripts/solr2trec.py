#!/usr/bin/env python3
import sys
import json

def solr_to_trec(solr_data, run_id="mysys"):
    trec_lines = []

    for query_name, data in solr_data.items():
        topic_id = query_name.split(".")[0]
        if "response" not in data:
            continue

        docs = data["response"].get("docs", [])
        for rank, doc in enumerate(docs, start=1):
            doc_id = doc.get("bookId") or doc.get("id") or f"doc{rank}"
            score = doc.get("score", 0)
            trec_lines.append(f"{topic_id} Q0 {doc_id} {rank} {score} {run_id}")

    return trec_lines


def main():
    input_data = sys.stdin.read()
    if not input_data.strip():
        print("No input data received. Pipe Solr JSON results into this script.")
        sys.exit(1)

    solr_data = json.loads(input_data)
    trec_lines = solr_to_trec(solr_data)
    print("\n".join(trec_lines))


if __name__ == "__main__":
    main()