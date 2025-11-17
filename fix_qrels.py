with open('./config/qrels.txt', 'r') as infile, open('./config/qrels_clean.txt', 'w') as outfile:
    for line in infile:
        if line.startswith('#'):
            continue
        parts = line.split()
        if len(parts) >= 4:
            query_id = parts[0].zfill(4)  # Add leading zeros: 1 -> 0001
            outfile.write(f"{query_id} {parts[1]} {parts[2]} {parts[3]}\n")