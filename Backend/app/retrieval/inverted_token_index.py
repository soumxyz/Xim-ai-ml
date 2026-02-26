from collections import defaultdict, Counter

class InvertedTokenIndex:
    def __init__(self):
        self.index = defaultdict(list)
        self.titles_map = {}

    def build_index(self, titles: list):
        self.index.clear()
        for title_obj in titles:
            title_id = title_obj.get('id')
            normalized_title = title_obj.get('normalized_title', '')
            self.titles_map[title_id] = title_obj
            
            tokens = set(normalized_title.split())
            for token in tokens:
                self.index[token].append(title_id)

    async def filter_by_tokens(self, query_tokens: list) -> list:
        candidate_counts = Counter()
        for token in query_tokens:
            if token in self.index:
                for cid in self.index[token]:
                    candidate_counts[cid] += 1
        
        # Sort by match count (descending), then by ID string (ascending) for deterministic stability
        sorted_cids = sorted(candidate_counts.keys(), key=lambda cid: (-candidate_counts[cid], str(cid)))
        
        return [self.titles_map[cid] for cid in sorted_cids if cid in self.titles_map]
