import math
from collections import defaultdict, Counter

class InvertedTokenIndex:
    def __init__(self):
        self.index = defaultdict(list)
        self.doc_freq = Counter()
        self.titles_map = {}
        self.doc_lengths = {}
        self.total_docs = 0

    def build_index(self, titles: list):
        self.index.clear()
        self.doc_freq.clear()
        self.titles_map.clear()
        self.doc_lengths.clear()
        self.total_docs = len(titles)
        
        for title_obj in titles:
            title_id = title_obj.get('id')
            normalized_title = title_obj.get('normalized_title', '')
            self.titles_map[title_id] = title_obj
            
            tokens = set(normalized_title.split())
            self.doc_lengths[title_id] = len(tokens)
            
            for token in tokens:
                self.index[token].append(title_id)
                self.doc_freq[token] += 1

    async def filter_by_tokens(self, query_tokens: list) -> list:
        candidate_scores = defaultdict(float)
        # Process unique tokens to prevent double-counting frequency
        for token in set(query_tokens):
            if token in self.index:
                # IDF weighting: rare tokens confer higher score
                df = self.doc_freq[token]
                # log(1 + N/df) gives higher score to rare tokens
                idf = math.log1p(self.total_docs / max(1, df))
                for cid in self.index[token]:
                    candidate_scores[cid] += idf
        
        def get_score(cid):
            raw_score = candidate_scores[cid]
            # Length penalty: divides the raw TF-IDF score by the number of tokens in the document.
            # This mathematically guarantees that an exact match rises above compound matches (e.g. 'Bharat' > 'Nav Bharat')
            return raw_score / max(1, self.doc_lengths.get(cid, 1))

        # Sort by match score (descending), then by ID string (ascending) for deterministic stability
        sorted_cids = sorted(candidate_scores.keys(), key=lambda cid: (-get_score(cid), str(cid)))
        
        return [self.titles_map[cid] for cid in sorted_cids if cid in self.titles_map]
