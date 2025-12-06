from flask import Flask, render_template, request
import pysolr

# Initialize the Flask app
app = Flask(__name__)

# Connect to Solr (assuming Solr is running locally on port 8983 and the core is named 'mycore')
solr = pysolr.Solr('http://localhost:8983/solr/mycore', always_commit=True)

def search_solr(query):
    """
    Executes a search query against Solr and returns the results.
    """
    try:
        # Perform the query on Solr
        results = solr.search(query)
        return results
    except Exception as e:
        print(f"Error executing query: {e}")
        return []

@app.route('/', methods=['GET', 'POST'])
def home():
    """
    Handles the main page where users input their queries and view results.
    """
    results = []
    query = ''
    
    if request.method == 'POST':
        # Get the query entered by the user
        query = request.form['query']
        
        # Perform the Solr search
        results = search_solr(query)
    
    return render_template('index.html', query=query, results=results)

@app.route('/book/<book_id>')
def book_details(book_id):
    try:
        results = solr.search(f"id:{book_id}")

        docs = list(results)
        print(f"Solr query results: {docs}")

        if docs:
            book = docs[0]  # first document
            return render_template('book_details.html', book=book)
        else:
            return "Book not found", 404
    except Exception as e:
        print(f"Error: {e}")
        return f"Error fetching book details: {e}", 500





if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
