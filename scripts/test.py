def main():
    parser = argparse.ArgumentParser(description="Query Solr using predefined JSON query files.")
    parser.add_argument("--queries", required=True, help="Path to directory containing query JSON files")
    parser.add_argument("--uri", required=True, help="Base Solr URI, e.g. http://localhost:8983/solr")
    parser.add_argument("--collection", required=True, help="Solr core/collection name, e.g. mycore")
    parser.add_argument("--output", help="Optional output file to save all query results")

    args = parser.parse_args()
    all_results = {}

    query_files = sorted(
        [os.path.join(args.queries, f) for f in os.listdir(args.queries) if f.endswith(".json")]
    )

    if not query_files:
        print("No JSON query files found in", args.queries)
        return

    for qfile in query_files:
        results = run_query(qfile, args.uri, args.collection)
        if results:
            all_results[os.path.basename(qfile)] = results

    if args.output:
        with open(args.output, "w") as out:
            json.dump(all_results, out, indent=2)
    else:
        print(json.dumps(all_results, indent=2))

if __name__ == "__main__":
    main()