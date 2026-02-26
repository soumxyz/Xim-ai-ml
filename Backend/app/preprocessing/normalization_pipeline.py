import re
import nltk
from nltk.corpus import stopwords

# Ensure stopwords are downloaded
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class NormalizationPipeline:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        # Add common business/media terms to stopwords if needed
        self.stop_words.update(['the', 'and', 'a', 'an', 'of', 'for'])

    def normalize(self, text: str) -> str:
        if not text:
            return ""
        
        # Lowercase
        text = text.lower()
        
        # Remove special characters and punctuation, replacing them with a space
        # This prevents Unicode squish-bypass (e.g. 'Hindustan\u202DTimes' -> 'Hindustantimes')
        text = re.sub(r'[^a-z0-9\s]', ' ', text)
        
        # Tokenize and remove stopwords
        tokens = text.split()
        tokens = [t for t in tokens if t not in self.stop_words]
        
        # Join and normalize whitespace
        return " ".join(tokens)
