#!/usr/bin/env python3
import os
import json
import argparse
import requests

def run_query(query_file, base_uri, collection):
    with open(query_file, "r") as f:
        query_data = json.load(f)

    url = f"{base_uri}/{collection}/select"
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, headers=headers, data=json.dumps(query_data))

    if response.status_code != 200:
        print(f"Error {response.status_code} on {query_file}: {response.text}")
        return None

    return response.json()

def main():
    parser = argparse.ArgumentParser(description="Query Solr using predefined JSON files OR a text query.")
    parser.add_argument("--queries", help="Path to directory containing query JSON files")
    parser.add_argument("--q", help="Plain text Solr query")
    parser.add_argument("--uri", required=True)
    parser.add_argument("--collection", required=True)
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--output")

    args = parser.parse_args()

    # --- Direct text query ---
    if args.q:
        q = {
            "query": args.q,
            "limit": args.limit
        }
        url = f"{args.uri}/{args.collection}/select"
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, headers=headers, data=json.dumps(q))

        if args.output:
            with open(args.output, "w") as out:
                out.write(response.text)
        else:
            print(response.text)
        return

    # --- JSON file mode (your original logic) ---
    if not args.queries:
        print("Either --q or --queries must be provided.")
        return

    ...


if __name__ == "__main__":
    main()