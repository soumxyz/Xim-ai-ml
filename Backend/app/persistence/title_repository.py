import csv
import os
import logging

class TitleRepository:
    _titles_cache = None  # Class-level cache

    def __init__(self):
        self.logger = logging.getLogger("mesh")
        self.csv_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'sample_titles.csv')
        self.json_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'Database.json')

    async def get_all_titles(self) -> list:
        """
        Loads titles from Dataset.json (JSON Lines) or fallback to CSV.
        """
        if TitleRepository._titles_cache is not None:
            return TitleRepository._titles_cache

        titles = []
        json_abs = os.path.abspath(self.json_path)
        csv_abs = os.path.abspath(self.csv_path)
        
        # 1. Try JSON first (the full converted dataset)
        if os.path.exists(json_abs):
            try:
                import json
                import unicodedata
                import re
                with open(json_abs, 'r', encoding='utf-8') as f:
                    for line in f:
                        if not line.strip(): continue
                        row = json.loads(line)
                        title = row.get("title") or row.get("headline") or "Untitled"
                        titles.append({
                            "id": row.get("id", len(titles)),
                            "title": title,
                            "normalized_title": row.get("normalized_title", title.lower()),
                            "canonical_title": re.sub(r'[^a-z0-9]', '', unicodedata.normalize('NFKC', title).lower().strip())
                        })
                TitleRepository._titles_cache = titles
                self.logger.info(f"Loaded {len(titles)} titles from Dataset.json.")
                return titles
            except Exception as e:
                self.logger.error(f"Failed to load JSON dataset: {e}")

        # 2. Fallback to CSV
        if os.path.exists(csv_abs):
            try:
                with open(csv_abs, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        titles.append({
                            "id": int(row["id"]),
                            "title": row["title"],
                            "normalized_title": row["normalized_title"]
                        })
                TitleRepository._titles_cache = titles
                self.logger.info(f"Loaded {len(titles)} titles from CSV fallback.")
            except Exception as e:
                self.logger.error(f"Failed to load CSV fallback: {e}")
            
        return titles

    @classmethod
    def clear_cache(cls):
        cls._titles_cache = None

    @classmethod
    def add_to_cache(cls, title_dict: dict):
        if cls._titles_cache is not None:
            cls._titles_cache.append(title_dict)
