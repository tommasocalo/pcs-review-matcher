# Review Matcher

This project scrapes PCS website for reviewer and submission information, embeds the text using the SPECTER2 model, and computes matching scores (Euclidean distances) between each paper and each reviewer. The goal is to automatically match reviewers with papers by comparing the semantic similarity between paper content (title and abstract) and reviewer profiles (expert keywords).

The SPECTER2 model is a transformer-based language model fine-tuned for scientific paper retrieval. It generates embeddings that capture the meaning of scientific texts, enabling effective similarity comparisons via Euclidean distance.

This project produces three primary output files:

- **reviewer_distance_matrix.csv**: A CSV file where each row corresponds to a reviewer, including reviewer name, email, and one column per paper (e.g., "Paper 1", "Paper 2", etc.) with the computed distance scores.
- **paper_id_to_title.json**: A JSON file mapping paper IDs to paper titles.
- **submissions.txt**: A JSON file containing scraped submission data (titles, abstracts, potential reviewer details, and authors).

## Project Structure

```
my_review_matcher/
├── .env
├── README.md
├── requirements.txt
├── config.py
├── main.py
├── embedder.py
├── matcher.py
└── scraper.py
```

- **.env**: Contains configuration variables.
- **requirements.txt**: Lists all Python dependencies.
- **config.py**: Loads environment variables from the `.env` file.
- **scraper.py**: Contains the `PCSScraper` class for logging in and scraping reviewer and submission data.
- **embedder.py**: Contains the `SPECTEREmbedder` class that loads the SPECTER2 model and computes embeddings.
- **matcher.py**: Contains the `ReviewMatcher` class that computes embeddings for papers and reviewers and calculates distances (using only expert keywords if configured).
- **main.py**: The main script that ties everything together. It scrapes (or loads) the data, computes reviewer–paper matching scores, and saves the results.

## Setup

1. **Install Dependencies**

   Install all required dependencies by running:
   ```bash
   pip install -r requirements.txt
   ```

2. **Create and Configure the .env File**

   In the project root, create a file named `.env` and populate it with your configuration. For example:
   ```dotenv
   # .env file

   # PCS website configuration
   PCS_BASE_URL=https://new.precisionconference.com
   USERNAME=alice_smith
   PASSWORD=SecretPassword123

   # Conference name to filter by (e.g. CHI 2025)
   CONFERENCE_NAME=CHI 2025

   # If you want to update submissions even if the file exists, set to "true"
   UPDATE_SUBMISSIONS=true

   # If you want to consider only expert keywords (ignore competent keywords), set to "true"
   EXPERT_ONLY=true
   ```

3. **Run the Script**

   Execute the main script with:
   ```bash
   python main.py
   ```

## How It Works

### Scraping

- **Login and Dashboard Navigation:**  
  The `PCSScraper` logs in using credentials from the `.env` file and navigates to the specified conference dashboard (e.g. "CHI 2025").

- **Reviewer and Submission Data:**  
  Reviewer data (including name, affiliation, and expert keywords) are scraped and saved as `reviewers.txt` (in JSON format).  
  Submission data (including paper titles, abstracts, potential reviewer details, and authors) are scraped and saved as `submissions.txt` (in JSON format).  
  If these files already exist and the `UPDATE_SUBMISSIONS` flag is not set, the script loads the data from disk instead of re-scraping.

### Embedding and Matching

- **Embedding:**  
  The `SPECTEREmbedder` computes text embeddings for papers (using the title and abstract) and for reviewers (using their name concatenated with their expert keywords).  
  The SPECTER2 model, a transformer fine-tuned for scientific paper retrieval, is used to generate embeddings that capture the semantic content of the texts.

- **Matching:**  
  The `ReviewMatcher` calculates the Euclidean distance between each paper embedding and each reviewer embedding.  
  A lower distance indicates a higher similarity between a paper and a reviewer.  
  A distance matrix is built where each row corresponds to a reviewer and each column corresponds to a paper.

### Output Files

- **reviewer_distance_matrix.csv:**  
  Contains one row per reviewer with columns for reviewer name, email, and one column per paper (e.g., "Paper 1", "Paper 2", etc.) with the corresponding distance scores.

- **paper_id_to_title.json:**  
  A JSON mapping from paper IDs (e.g., 1, 2, 3, …) to their titles.

- **submissions.txt:**  
  Contains the scraped submission data.

## Data Discovery

After running the script, you can perform further analysis on the output files. For example, in Python:

```python
import pandas as pd
df = pd.read_csv("reviewer_distance_matrix.csv")
print(df.head())
```

And view the paper mapping:

```python
import json
with open("paper_id_to_title.json", "r") as f:
    paper_mapping = json.load(f)
print(paper_mapping)
```

## Command-Line Flags and Options

This project uses environment variables (set in `.env`) to control its behavior:

- **UPDATE_SUBMISSIONS:**  
  If set to `true`, the script re-scrapes submission data even if `submissions.txt` exists; otherwise, it loads the existing file.

- **EXPERT_ONLY:**  
  If set to `true`, only expert keywords are used when computing reviewer embeddings (ignoring competent keywords).

## Goal

The primary goal of this project is to automatically match reviewers with papers by comparing the semantic similarity between paper content (title and abstract) and reviewer profiles (name and expert keywords). The similarity is calculated using Euclidean distance between embeddings generated by the SPECTER2 model. This information can be used to map reviewer availability to their content similarity with submitted papers.

## Fictitious Example Data

**Reviewers (reviewers.txt):**

```json
[
  {
    "name": "Jane Doe",
    "affiliation": "Department of Computer Science, Fictional University, jane.doe@fictional.edu",
    "expert": [
      "Human-Computer Interaction",
      "User Experience Design",
      "Lab Study"
    ]
  }
]
```

**Submissions (submissions.txt snippet):**

```json
[
  {
    "title": "AI in Healthcare: Innovations and Challenges",
    "abstract": "This study explores the application of artificial intelligence in healthcare settings, highlighting innovative solutions and discussing challenges in implementation. The research provides insights into future directions...",
    "potential_reviewers": [
      {
        "Score": "0.08",
        "Bid": "2",
        "Name": "John Doe",
        "Position": "clinician",
        "Years afterPhD": "5",
        "Pubs in lastsix years": "4",
        "Committee?": "cmte",
        "VolunteeredReviews": "1",
        "AssignedReviews": "8",
        "PrimaryReviews": "7",
        "SecondaryReviews": "1",
        "Action": "assign"
      },
      {
        "Score": "0.09",
        "Bid": "1",
        "Name": "Emily Davis",
        "Position": "researcher",
        "Years afterPhD": "3",
        "Pubs in lastsix years": "5",
        "Committee?": "cmte",
        "VolunteeredReviews": "0",
        "AssignedReviews": "10",
        "PrimaryReviews": "10",
        "SecondaryReviews": "0",
        "Action": "assign"
      }
    ]
  }
]

```

## License

This project is provided as a fictitious example.

---

Feel free to modify and extend the project as needed. Enjoy!
"""
```
