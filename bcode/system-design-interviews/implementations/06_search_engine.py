"""
Search Engine — Core Implementation
=====================================
Demonstrates: Inverted index, TF-IDF scoring, boolean queries,
autocomplete with trie, simple PageRank.

In a real system:
- Inverted index stored in Lucene/Elasticsearch (segment-based, immutable)
- TF-IDF replaced by BM25 (better term saturation handling)
- Distributed: index sharded by document ID or term
- Autocomplete: prefix trie in Redis, or completion suggester in ES
- PageRank: computed offline via MapReduce, stored as document boost
"""

import math
import re
from collections import defaultdict, Counter
from dataclasses import dataclass, field


# ─── Tokenization ────────────────────────────────────────────────────────────

STOP_WORDS = {"the", "a", "an", "is", "are", "was", "were", "in", "on", "at",
              "to", "for", "of", "and", "or", "it", "this", "that", "with"}


def tokenize(text: str) -> list[str]:
    """Lowercase, split on non-alpha, remove stop words."""
    words = re.findall(r'[a-z0-9]+', text.lower())
    return [w for w in words if w not in STOP_WORDS and len(w) > 1]


# ─── Inverted Index ──────────────────────────────────────────────────────────

@dataclass
class Posting:
    doc_id: int
    term_frequency: int
    positions: list[int] = field(default_factory=list)


class InvertedIndex:
    """
    Maps term → list of (doc_id, frequency, positions).
    Core data structure of every search engine.
    """

    def __init__(self):
        self.index: dict[str, list[Posting]] = defaultdict(list)
        self.documents: dict[int, str] = {}  # doc_id → raw text
        self.doc_lengths: dict[int, int] = {}  # doc_id → token count
        self.num_docs = 0

    def add_document(self, doc_id: int, text: str):
        """Index a document."""
        self.documents[doc_id] = text
        tokens = tokenize(text)
        self.doc_lengths[doc_id] = len(tokens)
        self.num_docs += 1

        # Count term frequencies and positions
        term_positions: dict[str, list[int]] = defaultdict(list)
        for pos, token in enumerate(tokens):
            term_positions[token].append(pos)

        for term, positions in term_positions.items():
            self.index[term].append(Posting(
                doc_id=doc_id,
                term_frequency=len(positions),
                positions=positions,
            ))

    def search(self, term: str) -> list[Posting]:
        """Look up a single term."""
        return self.index.get(term.lower(), [])

    def document_frequency(self, term: str) -> int:
        """How many documents contain this term."""
        return len(self.index.get(term.lower(), []))


# ─── TF-IDF Scoring ──────────────────────────────────────────────────────────

class TFIDFScorer:
    """
    TF-IDF: Term Frequency × Inverse Document Frequency.
    High score = term is frequent in this doc but rare across all docs.
    """

    def __init__(self, index: InvertedIndex):
        self.index = index

    def tf(self, term_freq: int, doc_length: int) -> float:
        """Normalized term frequency."""
        return term_freq / doc_length if doc_length > 0 else 0

    def idf(self, term: str) -> float:
        """Inverse document frequency — rare terms score higher."""
        df = self.index.document_frequency(term)
        if df == 0:
            return 0
        return math.log(self.index.num_docs / df)

    def score(self, query: str) -> list[tuple[int, float]]:
        """Score all documents for a query. Returns sorted (doc_id, score)."""
        tokens = tokenize(query)
        scores: dict[int, float] = defaultdict(float)

        for term in tokens:
            idf_val = self.idf(term)
            for posting in self.index.search(term):
                tf_val = self.tf(posting.term_frequency, self.index.doc_lengths[posting.doc_id])
                scores[posting.doc_id] += tf_val * idf_val

        return sorted(scores.items(), key=lambda x: x[1], reverse=True)


# ─── Boolean Queries ──────────────────────────────────────────────────────────

def boolean_and(index: InvertedIndex, terms: list[str]) -> set[int]:
    """AND query: documents must contain ALL terms."""
    if not terms:
        return set()
    result = {p.doc_id for p in index.search(terms[0])}
    for term in terms[1:]:
        result &= {p.doc_id for p in index.search(term)}
    return result


def boolean_or(index: InvertedIndex, terms: list[str]) -> set[int]:
    """OR query: documents containing ANY term."""
    result: set[int] = set()
    for term in terms:
        result |= {p.doc_id for p in index.search(term)}
    return result


# ─── Autocomplete Trie ────────────────────────────────────────────────────────

class TrieNode:
    def __init__(self):
        self.children: dict[str, "TrieNode"] = {}
        self.is_word: bool = False
        self.frequency: int = 0  # Search frequency for ranking


class AutocompleteTrie:
    """
    Prefix trie for search suggestions.
    Production: Redis sorted sets or Elasticsearch completion suggester.
    """

    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str, frequency: int = 1):
        node = self.root
        for char in word.lower():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_word = True
        node.frequency += frequency

    def suggest(self, prefix: str, limit: int = 5) -> list[tuple[str, int]]:
        """Find all words with given prefix, sorted by frequency."""
        node = self.root
        for char in prefix.lower():
            if char not in node.children:
                return []
            node = node.children[char]

        # DFS to find all words under this prefix
        results: list[tuple[str, int]] = []
        self._dfs(node, prefix, results)
        return sorted(results, key=lambda x: x[1], reverse=True)[:limit]

    def _dfs(self, node: TrieNode, current: str, results: list):
        if node.is_word:
            results.append((current, node.frequency))
        for char, child in node.children.items():
            self._dfs(child, current + char, results)


# ─── PageRank ─────────────────────────────────────────────────────────────────

def pagerank(graph: dict[str, list[str]], damping: float = 0.85, iterations: int = 20) -> dict[str, float]:
    """
    Simplified PageRank on a small link graph.
    PR(A) = (1-d)/N + d * Σ(PR(T)/C(T)) for all T linking to A

    Production: Computed via MapReduce on the entire web graph.
    """
    nodes = set(graph.keys())
    for targets in graph.values():
        nodes.update(targets)
    nodes = list(nodes)
    n = len(nodes)

    # Initialize uniform
    ranks = {node: 1.0 / n for node in nodes}

    for _ in range(iterations):
        new_ranks = {}
        for node in nodes:
            rank_sum = 0.0
            for source, targets in graph.items():
                if node in targets:
                    rank_sum += ranks[source] / len(targets)
            new_ranks[node] = (1 - damping) / n + damping * rank_sum
        ranks = new_ranks

    return ranks


# ─── Demo ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== Search Engine Demo ===\n")

    # Build index
    index = InvertedIndex()
    docs = [
        (1, "Python is a great programming language for data science"),
        (2, "Java and Python are popular languages for backend development"),
        (3, "Machine learning with Python uses libraries like scikit-learn"),
        (4, "JavaScript is the language of the web browser"),
        (5, "Distributed systems require careful design and testing"),
        (6, "Python web frameworks include Django and Flask"),
    ]
    for doc_id, text in docs:
        index.add_document(doc_id, text)

    print("--- Inverted Index ---")
    print(f"  Indexed {index.num_docs} documents")
    print(f"  Vocabulary size: {len(index.index)} terms")
    print(f"  'python' appears in {index.document_frequency('python')} docs")

    # TF-IDF search
    print("\n--- TF-IDF Search ---")
    scorer = TFIDFScorer(index)
    for query in ["python programming", "web development", "distributed systems"]:
        results = scorer.score(query)
        print(f"  Query: '{query}'")
        for doc_id, score in results[:3]:
            print(f"    Doc {doc_id} (score {score:.3f}): {index.documents[doc_id][:50]}...")
        print()

    # Boolean queries
    print("--- Boolean Queries ---")
    and_result = boolean_and(index, ["python", "web"])
    or_result = boolean_or(index, ["python", "web"])
    print(f"  'python' AND 'web': docs {and_result}")
    print(f"  'python' OR 'web':  docs {or_result}")

    # Autocomplete
    print("\n--- Autocomplete Trie ---")
    trie = AutocompleteTrie()
    search_terms = [("python", 100), ("python tutorial", 80), ("python list", 60),
                    ("pytorch", 45), ("pandas", 70), ("programming", 30)]
    for term, freq in search_terms:
        trie.insert(term, freq)

    for prefix in ["py", "pan", "pro"]:
        suggestions = trie.suggest(prefix, limit=3)
        print(f"  '{prefix}' → {[(s, f) for s, f in suggestions]}")

    # PageRank
    print("\n--- PageRank ---")
    web_graph = {
        "google.com": ["python.org", "github.com"],
        "python.org": ["github.com", "docs.python.org"],
        "github.com": ["python.org"],
        "docs.python.org": ["python.org"],
        "blog.example.com": ["python.org", "github.com"],
    }
    ranks = pagerank(web_graph)
    sorted_ranks = sorted(ranks.items(), key=lambda x: x[1], reverse=True)
    print(f"  Link graph: {len(web_graph)} pages")
    for page, rank in sorted_ranks:
        bar = "█" * int(rank * 100)
        print(f"    {page:<20} {rank:.4f} {bar}")
