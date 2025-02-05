# matcher.py
import os
import json
import numpy as np
from sklearn.metrics.pairwise import euclidean_distances
from embedder import SPECTEREmbedder

class ReviewMatcher:
    def __init__(self):
        self.embedder = SPECTEREmbedder()
        
    def process_paper(self, paper: dict) -> dict:
        paper_text = f"{paper['title']}{self.embedder.tokenizer.sep_token}{paper.get('abstract', '')}"
        paper_embedding = self.embedder.embed([paper_text])[0]
        reviewer_embeddings = self._get_reviewer_embeddings()
        distances = euclidean_distances([paper_embedding], reviewer_embeddings)
        return {
            "paper": paper,
            "distances": distances[0],
            "reviewer_embeddings": reviewer_embeddings
        }
    
    def _get_reviewer_embeddings(self) -> np.ndarray:
        reviewers = self._load_reviewers()
        texts = [f"{r['name']}{self.embedder.tokenizer.sep_token}{', '.join(r.get('expert', []))}"
                 for r in reviewers]
        return self.embedder.embed(texts)
    
    def _load_reviewers(self) -> list:
        if os.path.exists("reviewers.txt"):
            with open("reviewers.txt", "r", encoding="utf-8") as f:
                reviewers = json.load(f)
            return reviewers
        else:
            raise FileNotFoundError("reviewers.txt not found. Run the scraper first.")
