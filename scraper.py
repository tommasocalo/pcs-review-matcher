# scraper.py
import time
import json
import os
from typing import List, Dict
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from config import PCS_BASE_URL

class PCSScraper:
    def __init__(self):
        service = ChromeService(executable_path=ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)
        self.wait = WebDriverWait(self.driver, 10)
        self.go_home()
    
    def go_home(self):
        home_url = f"{PCS_BASE_URL}/login"
        self.driver.get(home_url)
    
    def login(self, username: str, password: str):
        time.sleep(2)
        username_field = self.wait.until(EC.presence_of_element_located((By.ID, "username")))
        password_field = self.wait.until(EC.presence_of_element_located((By.ID, "password")))
        username_field.clear()
        username_field.send_keys(username)
        password_field.clear()
        password_field.send_keys(password)
        submit_button = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='submit' and @value='Sign in']")))
        submit_button.click()
        time.sleep(3)
    
    def get_ac_dashboard(self, conference_name: str) -> List[Dict]:
        reviews_url = f"{PCS_BASE_URL}/reviews"
        self.driver.get(reviews_url)
        self.wait.until(EC.visibility_of_element_located((By.ID, "user_reviews")))
        time.sleep(2)
        try:
            row = self.driver.find_element(By.XPATH,
                    f"//table[@id='user_reviews']//tr[td[contains(., '{conference_name}')] and .//a[contains(@href, 'committee')]]")
            review_link = row.find_element(By.XPATH, ".//a[contains(@href, 'committee')]")
            review_link.click()
            time.sleep(2)
        except Exception as e:
            print(f"Error navigating to dashboard for conference '{conference_name}': {e}")
        return []
    
    def get_all_reviewer_info(self, output_filename: str = "reviewers.txt") -> List[Dict]:
        all_reviewers_link = self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//ul[@class='actionList']//a[contains(@href, '/committee/reviewers')]")
        ))
        all_reviewers_link.click()
        time.sleep(2)
        self.wait.until(EC.visibility_of_element_located((By.ID, "track_public_reviewers")))
        reviewer_links = []
        rows = self.driver.find_elements(By.XPATH, "//table[@id='track_public_reviewers']//tbody/tr")
        for row in rows:
            try:
                link_elem = row.find_element(By.XPATH, ".//a")
                href = link_elem.get_attribute("href")
                reviewer_links.append(href)
            except Exception as e:
                print("Error extracting reviewer link:", e)
        
        reviewer_info_list = []
        for link in reviewer_links:
            self.driver.get(link)
            time.sleep(2)
            try:
                h1_elem = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//h1")))
                name_text = h1_elem.text.strip()
                if name_text.lower().startswith("reviewer "):
                    name_text = name_text[9:].strip()
            except Exception as e:
                print(f"Error extracting reviewer name from {link}: {e}")
                name_text = "N/A"
            try:
                li_elem = self.driver.find_element(By.XPATH, "//ul[contains(@class, 'plain')]/li[1]")
                affiliation_text = li_elem.text.strip()
            except Exception as e:
                print(f"Error extracting affiliation from {link}: {e}")
                affiliation_text = "N/A"
            expert_keywords = []
            try:
                expert_uls = self.driver.find_elements(By.XPATH, "//h3[normalize-space(.)='Expert']/following-sibling::ul[1]")
                if expert_uls:
                    expert_items = expert_uls[0].find_elements(By.TAG_NAME, "li")
                    expert_keywords = [item.text.strip() for item in expert_items if item.text.strip().lower() != "none provided"]
                else:
                    expert_keywords = []
            except Exception as e:
                print(f"Error extracting expert keywords from {link}: {e}")
                expert_keywords = []
            # (We ignore competent keywords if we want expert-only mode.)
            reviewer_info_list.append({
                "name": name_text,
                "affiliation": affiliation_text,
                "expert": expert_keywords
            })
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(reviewer_info_list, f, ensure_ascii=False, indent=2)
        return reviewer_info_list
    
    def get_potential_reviewers_for_submission(self) -> List[Dict]:
        try:
            potential_link = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(., 'Show potential reviewers')]"))
            )
            potential_link.click()
            time.sleep(2)
            self.wait.until(EC.visibility_of_element_located((By.ID, "submission_affinities")))
            time.sleep(2)
        except Exception as e:
            print(f"Error clicking/waiting for potential reviewers: {e}")
            return []
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        table = soup.find("table", id="submission_affinities")
        if not table:
            print("No potential reviewers table found.")
            return []
        header_cells = table.find("thead").find_all("th")
        headers = [th.get_text(strip=True) for th in header_cells]
        reviewers = []
        tbody = table.find("tbody")
        if tbody:
            for row in tbody.find_all("tr"):
                cells = row.find_all("td")
                if len(cells) != len(headers):
                    continue
                row_data = {header: cell.get_text(strip=True) for header, cell in zip(headers, cells)}
                reviewers.append(row_data)
        else:
            print("No table body found in potential reviewers table.")
        return reviewers
    
    def get_submission_info(self, output_filename: str = "submissions.txt") -> List[Dict]:
        self.wait.until(EC.visibility_of_element_located((By.ID, "reviewer_assignments_primary")))
        time.sleep(2)
        submission_links = []
        rows = self.driver.find_elements(By.XPATH, "//table[@id='reviewer_assignments_primary']//tbody/tr")
        for row in rows:
            try:
                link_elem = row.find_element(By.XPATH, ".//td[5]//a")
                href = link_elem.get_attribute("href")
                if href:
                    submission_links.append(href)
            except Exception as e:
                print("Error extracting submission link:", e)
        submission_info_list = []
        for link in submission_links:
            self.driver.get(link)
            time.sleep(2)
            try:
                title_elem = self.wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "div.submissionTitle")))
                title_text = title_elem.text.strip()
            except Exception as e:
                print(f"Error extracting title from {link}: {e}")
                title_text = "N/A"
            try:
                abstract_elem = self.driver.find_element(By.XPATH, "//h3[normalize-space(text())='Abstract']/following-sibling::div[1]")
                abstract_text = abstract_elem.text.strip()
            except Exception as e:
                print(f"Error extracting abstract from {link}: {e}")
                abstract_text = "N/A"
            potential_reviewers = self.get_potential_reviewers_for_submission()
            submission_info_list.append({
                "title": title_text,
                "abstract": abstract_text,
                "potential_reviewers": potential_reviewers
            })
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(submission_info_list, f, ensure_ascii=False, indent=2)
        return submission_info_list

    def close(self):
        self.driver.quit()
