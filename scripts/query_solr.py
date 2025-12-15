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
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(query_data))
        response.raise_for_status() # Check for HTTP errors
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def convert_solr_to_ui(solr_json):
    """Convert Solr response -> Streamlit UI expected format."""
    # Check if Solr returned an error
    if "error" in solr_json:
        return {"results": [], "error": solr_json["error"]}

    docs = solr_json.get("response", {}).get("docs", [])
    converted = []

    for d in docs:
        # Extract Title (Handle list vs string)
        title_raw = d.get("title", ["No Title"])
        title = title_raw[0] if isinstance(title_raw, list) and len(title_raw) > 0 else str(title_raw)

        # Extract Content (Handle list vs string) - MAPPING TO 'content' FIELD
        content_raw = d.get("content", [""]) 
        content = content_raw[0] if isinstance(content_raw, list) and len(content_raw) > 0 else str(content_raw)

        converted.append({
            "title": title,
            "content": content
        })

    return {"results": converted}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--queries", help="Directory with query files")
    parser.add_argument("--q", help="Direct text query")
    parser.add_argument("--uri", required=True)
    parser.add_argument("--collection", required=True)
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--output")

    args = parser.parse_args()

    # --- Direct text query mode (Used by UI) ---
    if args.q:
        # Construct Solr JSON Request
        # We use 'params' wrapper to act like standard URL parameters
        q = {
            "params": {
                "q": args.q,
                "rows": args.limit,
                "defType": "edismax", # Optional: better query parser
                "qf": "title content" # Query these fields
            }
        }

        url = f"{args.uri}/{args.collection}/select"
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(url, headers=headers, data=json.dumps(q))
            
            # If 404 or 400, print error cleanly
            if response.status_code != 200:
                print(json.dumps({
                    "results": [], 
                    "error": f"Solr returned {response.status_code}: {response.text[:200]}"
                }))
                return

            solr_json = response.json()
            result = convert_solr_to_ui(solr_json)
            print(json.dumps(result))

        except Exception as e:
            # Catch connection crashes
            print(json.dumps({"results": [], "error": str(e)}))

        return

    # --- File mode (Legacy) ---
    if args.queries:
        for file_name in os.listdir(args.queries):
            if not file_name.endswith(".json"): continue
            file_path = os.path.join(args.queries, file_name)
            solr_json = run_query(file_path, args.uri, args.collection)
            result = convert_solr_to_ui(solr_json)
            if args.output:
                with open(os.path.join(args.output, file_name.replace(".json", "_results.json")), "w") as out:
                    out.write(json.dumps(result))
            else:
                print(json.dumps(result))

if __name__ == "__main__":
    main()