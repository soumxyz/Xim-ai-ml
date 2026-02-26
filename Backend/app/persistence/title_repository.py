class TitleRepository:
    def __init__(self):
        # Placeholder for actual DB connection
        pass

    async def get_all_titles(self) -> list:
        # Returns a mock set of titles for testing the startup flow
        # In production, this would fetch from Layer 6 Persistence
        return [
            {
                "id": 1, 
                "title": "The Daily News", 
                "normalized_title": "daily news",
                "embedding": [0.1] * 384 # Mock embedding
            },
            {
                "id": 2, 
                "title": "Indian Express", 
                "normalized_title": "indian express",
                "embedding": [0.2] * 384
            }
        ]
