import streamlit as st
import pandas as pd
import json
import subprocess
import os

st.set_page_config(page_title="Search UI", layout="wide")


st.title("Search System Interface")


#  SIDEBAR OPTIONS
st.sidebar.header("⚙️ Opções")

show_snippets = st.sidebar.checkbox("Gerar snippets", True)
show_clusters = st.sidebar.checkbox("Mostrar clusters", True)

max_results = st.sidebar.slider("Maximum number of results:", 1, 100, 10)


query = st.text_input("Write your query:", "")

search_button = st.button("Search")



def run_query(query_text, max_results=10):
    script_path = os.path.join("scripts", "query_solr.py")

    try:
        output = subprocess.check_output(
            [
                "python3", script_path,
                "--q", query_text,
                "--limit", str(max_results),
                "--uri", "http://localhost:8983/solr",
                "--collection", "courses"           
            ],
            universal_newlines=True
        )
        return json.loads(output)

    except Exception as e:
        st.error(f"Error running search script: {e}")
        return None


def generate_snippet(text, query):
    text_lower = text.lower()
    query_lower = query.lower()
    pos = text_lower.find(query_lower)

    if pos == -1:
        return text[:200] + "..."

    start = max(0, pos - 50)
    end = min(len(text), pos + 50)
    snippet = text[start:end].replace(query, f"**{query}**")
    return snippet + "..."


def cluster_results(results):
    clusters = {}
    for res in results:
        key = res["title"][0].upper()
        clusters.setdefault(key, []).append(res)
    return clusters


#  SEARCH ACTION
if search_button and query.strip() != "":
    with st.spinner("Searching..."):
        data = run_query(query, max_results=max_results)

    if data is None:
        st.stop()

    results = data.get("results", [])

    st.subheader(f"Results ({len(results)})")

    if show_clusters:
        clusters = cluster_results(results)

        for cluster_name, items in clusters.items():
            with st.expander(f"Cluster {cluster_name} ({len(items)})"):
                for r in items:
                    st.markdown(f"### {r.get('title','Sem título')}")

                    if show_snippets:
                        snippet = generate_snippet(r.get("content",""), query)
                        st.markdown(snippet)

                    st.markdown("---")

    else:
        for r in results:
            st.markdown(f"### {r.get('title','Sem título')}")

            if show_snippets:
                snippet = generate_snippet(r.get("content",""), query)
                st.markdown(snippet)

            st.markdown("---")

else:
    st.info("Write a query above and click 'Search'.")

