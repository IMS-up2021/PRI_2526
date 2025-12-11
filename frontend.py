from flask import Flask, render_template, request, redirect, url_for
import pysolr
from typing import List
from feedback import combine_term_vectors, build_expanded_edismax_query

# Initialize the Flask app
app = Flask(__name__)

# Connect to Solr (adjust URL/core if different)
SOLR_URL = 'http://localhost:8983/solr/mycore'
solr = pysolr.Solr(SOLR_URL, always_commit=True)

# default qf used for edismax expansion queries (keep in sync with your config)
DEFAULT_QF = "title^3 description^2 genres^2 author^1"

def search_solr_raw(q: str, rows: int = 30, qf: str = DEFAULT_QF):
    params = {
        "defType": "edismax",
        "qf": qf,
        "rows": rows,
        "wt": "json"
    }
    # pysolr: search(q, **params)
    return solr.search(q, **params)

@app.route('/', methods=['GET', 'POST'])
def home():
    """
    Main search page. POST triggers a search.
    """
    results = []
    query = ''
    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        if query:
            res = search_solr_raw(query, rows=30)
            results = list(res)  # pysolr returns Results object, turn into list for template
    return render_template('index.html', query=query, results=results)

@app.route('/refine', methods=['POST'])
def refine():
    """
    Re-rank using explicit relevance feedback (Rocchio-like).
    Expects form fields:
      - query: original query text
      - selected_ids: list of selected bookId values
    """
    query = request.form.get('query', '').strip()
    selected_ids = request.form.getlist('selected_ids')
    if not query or not selected_ids:
        return redirect(url_for('home'))

    # fetch title+description for selected docs
    # build safe OR query on bookId or id
    id_clauses = []
    for sid in selected_ids:
        sid_escaped = sid.replace('"', '\\"')
        id_clauses.append(f'bookId:"{sid_escaped}"')  # prefer bookId field
    fetch_q = " OR ".join(id_clauses)
    docs_res = solr.search(fetch_q, rows=len(selected_ids), fl="title,description,bookId", wt="json")
    docs = list(docs_res)

    relevant_texts: List[str] = []
    for d in docs:
        title = d.get('title', "")
        if isinstance(title, list):
            title = " ".join(title)
        descr = d.get('description', "")
        if isinstance(descr, list):
            descr = " ".join(descr)
        relevant_texts.append(f"{title} {descr}")

    # build Rocchio expansion
    expanded_terms = combine_term_vectors(query, relevant_texts, top_k=20)
    expanded_query = build_expanded_edismax_query(query, expanded_terms, term_boost_scale=1.0)

    # run expanded query
    res = search_solr_raw(expanded_query, rows=100)
    results = list(res)
    # render same template with expanded results and show original query
    return render_template('index.html', query=query, results=results, expanded=True)

@app.route('/book/<book_id>')
def book_details(book_id):
    try:
        res = solr.search(f'bookId:"{book_id}"', rows=1)
        docs = list(res)
        if docs:
            book = docs[0]
            return render_template('book_details.html', book=book)
        else:
            return "Book not found", 404
    except Exception as e:
        return f"Error fetching book details: {e}", 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)