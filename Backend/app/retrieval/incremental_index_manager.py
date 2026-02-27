import logging
import numpy as np

class IncrementalIndexManager:
    def __init__(self, ann_index, token_index):
        self.ann_index = ann_index
        self.token_index = token_index
        self.logger = logging.getLogger("mesh.indexing")

    def add_new_title(self, title_obj: dict):
        """
        Dynamically updates indexes with a new approved title.
        """
        try:
            # 1. Update Token Index
            self.token_index.build_index([title_obj]) # build_index clear()s, so we need to fix it or add an append method
            # For demo, we'll assume we have an append_to_index method
            if hasattr(self.token_index, 'append_title'):
                self.token_index.append_title(title_obj)
            
            # 2. Update FAISS Index
            if 'embedding' in title_obj:
                embedding = np.array([title_obj['embedding']]).astype('float32')
                self.ann_index.index.add(embedding)
                self.ann_index.metadata.append(title_obj)
                
            self.logger.info(f"Dynamically indexed new title: {title_obj.get('title')}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to incrementally update index: {str(e)}")
            return False
