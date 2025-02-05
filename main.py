# main.py
import os
import json
import numpy as np
import pandas as pd
from tqdm import tqdm
from config import USERNAME, PASSWORD, CONFERENCE_NAME, UPDATE_SUBMISSIONS, EXPERT_ONLY
from scraper import PCSScraper
from matcher import ReviewMatcher

def main():
    # Instantiate scraper and log in.
    scraper = PCSScraper()
    scraper.login(USERNAME, PASSWORD)
    
    # Navigate to conference dashboard.
    scraper.get_ac_dashboard(CONFERENCE_NAME)
    
    # Load or scrape reviewers.
    if os.path.exists("reviewers.txt"):
        with open("reviewers.txt", "r", encoding="utf-8") as f:
            reviewers = json.load(f)
        print(f"Loaded {len(reviewers)} reviewers from file.")
    else:
        reviewers = scraper.get_all_reviewer_info("reviewers.txt")
        print(f"Scraped {len(reviewers)} reviewers.")
    
    # Return to dashboard.
    scraper.get_ac_dashboard(CONFERENCE_NAME)
    
    # Check if submissions need to be updated.
    if os.path.exists("submissions.txt") and not UPDATE_SUBMISSIONS:
        with open("submissions.txt", "r", encoding="utf-8") as f:
            submissions = json.load(f)
        print(f"Loaded {len(submissions)} submissions from file.")
    else:
        submissions = scraper.get_submission_info("submissions.txt")
        print(f"Scraped {len(submissions)} submissions.")
    
    # Instantiate matcher.
    matcher = ReviewMatcher()
    reviewers_data = matcher._load_reviewers()
    n_reviewers = len(reviewers_data)
    n_papers = len(submissions)
    distance_matrix = np.zeros((n_reviewers, n_papers))
    paper_id_to_title = {}
    
    for i, paper in enumerate(tqdm(submissions, desc="Processing papers")):
        result = matcher.process_paper(paper)
        distances = result["distances"]
        for j in range(n_reviewers):
            distance_matrix[j, i] = distances[j]
        paper_id_to_title[i + 1] = paper.get("title", "N/A")
    
    rows = []
    for j, reviewer in enumerate(reviewers_data):
        row = {
            "name": reviewer.get("name", "N/A"),
            "mail": reviewer.get("mail", "N/A")
        }
        for i in range(n_papers):
            row[f"Paper {i + 1}"] = distance_matrix[j, i]
        rows.append(row)
    
    df = pd.DataFrame(rows)
    df.to_csv("reviewer_distance_matrix.csv", index=False)
    print("Saved reviewer distance matrix to 'reviewer_distance_matrix.csv'.")
    
    with open("paper_id_to_title.json", "w", encoding="utf-8") as f:
        json.dump(paper_id_to_title, f, ensure_ascii=False, indent=2)
    print("Saved paper ID-to-title mapping to 'paper_id_to_title.json'.")
    
    scraper.close()

if __name__ == "__main__":
    main()
