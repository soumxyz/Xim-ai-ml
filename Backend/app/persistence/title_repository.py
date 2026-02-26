import csv
import os
import logging

class TitleRepository:
    _titles_cache = None  # Class-level cache

    def __init__(self):
        self.logger = logging.getLogger("metrixa")
        self.csv_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'sample_titles.csv')

    async def get_all_titles(self) -> list:
        """
        Loads titles from CSV dataset.
        Uses class-level cache to avoid re-reading on every call.
        """
        if TitleRepository._titles_cache is not None:
            return TitleRepository._titles_cache

        titles = []
        abs_path = os.path.abspath(self.csv_path)
        
        if not os.path.exists(abs_path):
            self.logger.warning(f"Dataset not found at {abs_path}. Returning empty list.")
            return []
        
        try:
            with open(abs_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    titles.append({
                        "id": int(row["id"]),
                        "title": row["title"],
                        "normalized_title": row["normalized_title"]
                    })
            
            TitleRepository._titles_cache = titles
            self.logger.info(f"Loaded {len(titles)} titles from CSV.")
        except Exception as e:
            self.logger.error(f"Failed to load CSV: {e}")
            
        return titles

    @classmethod
    def clear_cache(cls):
        cls._titles_cache = None

    @classmethod
    def add_to_cache(cls, title_dict: dict):
        if cls._titles_cache is not None:
            cls._titles_cache.append(title_dict)
