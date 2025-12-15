import re
from collections import Counter, defaultdict
from typing import List, Optional, Tuple

# small stopword list — extend if needed
STOPWORDS = {
    "the","a","an","and","or","of","in","on","for","to","with","by","from","at","is","are","was","were","it",
    "that","this","as","be","has","have","i","you","he","she","they","we"
}

TOKEN_RE = re.compile(r"[a-z0-9']{2,}", re.I)

def tokenize(text: str) -> List[str]:
    if not text:
        return []
    tokens = TOKEN_RE.findall(text.lower())
    tokens = [t for t in tokens if t not in STOPWORDS]
    return tokens

def doc_to_term_counts(texts: List[str]) -> Counter:
    c = Counter()
    for t in texts:
        c.update(tokenize(t))
    return c

def combine_term_vectors(
    orig_query: str,
    relevant_texts: List[str],
    non_relevant_texts: Optional[List[str]] = None,
    alpha: float = 1.0,
    beta: float = 0.75,
    gamma: float = 0.15,
    top_k: int = 15
) -> List[Tuple[str, float]]:
    """
    Simple Rocchio-like combination.
    Returns list of (term, score) sorted descending.
    """
    q_terms = tokenize(orig_query)
    q_counter = Counter(q_terms)

    rel_counter = doc_to_term_counts(relevant_texts)
    if relevant_texts:
        for t in rel_counter:
            rel_counter[t] /= max(1, len(relevant_texts))

    nonrel_counter = Counter()
    if non_relevant_texts:
        nonrel_counter = doc_to_term_counts(non_relevant_texts)
        for t in nonrel_counter:
            nonrel_counter[t] /= max(1, len(non_relevant_texts))

    scores = defaultdict(float)
    for t, v in q_counter.items():
        scores[t] += alpha * v
    for t, v in rel_counter.items():
        scores[t] += beta * v
    for t, v in nonrel_counter.items():
        scores[t] -= gamma * v

    # filter and sort
    filtered = [(t, s) for t, s in scores.items() if t not in STOPWORDS and len(t) > 1 and s > 0]
    filtered.sort(key=lambda x: x[1], reverse=True)
    return filtered[:top_k]

def build_expanded_edismax_query(orig_query: str, expanded_terms: List[Tuple[str, float]], term_boost_scale: float = 1.0) -> str:
    """
    Build edismax q string that keeps original query and appends boosted expansion terms.
    Example output: (original query) term1^2.34 term2^1.12
    """
    parts = []
    # keep original query (parenthesized to preserve phrases)
    parts.append(f'({orig_query})')

    if expanded_terms:
        max_score = expanded_terms[0][1] or 1.0
        for term, score in expanded_terms:
            boost = 1.0 + (score / max_score) * term_boost_scale * 3.0
            # minimal escaping: wrap tokens with quotes if they contain spaces (rare here)
            safe_term = term.replace('"', '')
            parts.append(f'{safe_term}^{boost:.3f}')

    return " ".join(parts)