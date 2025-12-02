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

def convert_solr_to_ui(solr_json):
    """Convert Solr response -> Streamlit UI expected format."""
    docs = solr_json.get("response", {}).get("docs", [])

    converted = []
    for d in docs:
        converted.append({
            "title": d.get("title", ["No Title"])[0],
            "content": d.get("content", [""])[0]
        })

    return {"results": converted}

def main():
    parser = argparse.ArgumentParser(description="Query Solr using predefined JSON files OR a text query.")

    parser.add_argument("--queries", help="Path to directory containing query JSON files")
    parser.add_argument("--q", help="Plain text Solr query")
    parser.add_argument("--uri", required=True)
    parser.add_argument("--collection", required=True)
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--output")

    args = parser.parse_args()

    # --- Direct text query mode ---
    if args.q:
        q = {
            "query": args.q,
            "limit": args.limit
        }

        url = f"{args.uri}/{args.collection}/select"
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, headers=headers, data=json.dumps(q))

        solr_json = response.json()
        result = convert_solr_to_ui(solr_json)

        if args.output:
            with open(args.output, "w") as out:
                out.write(json.dumps(result))
        else:
            print(json.dumps(result))

        return

    # --- JSON file mode (not used in your UI) ---
    if not args.queries:
        print("Either --q or --queries must be provided.")
        return

    # Loop through query files if needed
    for file_name in os.listdir(args.queries):
        if not file_name.endswith(".json"):
            continue

        file_path = os.path.join(args.queries, file_name)
        solr_json = run_query(file_path, args.uri, args.collection)
        result = convert_solr_to_ui(solr_json)

        if args.output:
            out_path = os.path.join(args.output, file_name.replace(".json", "_results.json"))
            with open(out_path, "w") as out:
                out.write(json.dumps(result))
        else:
            print(json.dumps(result))


if __name__ == "__main__":
    main()
