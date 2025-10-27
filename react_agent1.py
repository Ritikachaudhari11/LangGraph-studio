import os
import sqlite3
from datetime import datetime
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage

# Selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


# -------------------- API Key --------------------
groq_api_key = os.environ.get("GROQ_API_KEY")
if not groq_api_key:
    raise ValueError("GROQ_API_KEY environment variable not set.")


# -------------------- Tool 1: Get certification points --------------------
@tool("get_certification_points")
def get_certification_points(cert_name: str) -> dict:
    """
    Look up the certification's credit points from SQLite (certifications_data.db → certifications_table)
    """
    try:
        conn = sqlite3.connect("certifications_data.db")
        cursor = conn.cursor()
        cursor.execute("SELECT cert_name, points FROM certifications_table")
        records = cursor.fetchall()
        conn.close()

        cert_name_lower = cert_name.lower()

        # Try to find a best match
        for db_cert, points in records:
            if any(keyword in cert_name_lower for keyword in db_cert.lower().split()):
                return {"category": db_cert, "points": points}

        # Default to lowest points if no match found
        if records:
            db_cert, points = records[-1]
            return {"category": db_cert, "points": points}

        return {"error": "No certifications found in database"}

    except Exception as e:
        return {"error": f"Database error: {str(e)}"}


# -------------------- Tool 2: Parse Credly Badge --------------------
@tool("parse_credly_badge")
def parse_credly_badge(url: str) -> dict:
    """
    Extracts badge details (name, issuer, holder, dates) from Credly badge URL using Selenium (headless)
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=options)

    badge_details = {}
    try:
        driver.get(url)
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.cr-badges-full-badge__head-group"))
        )

        # Badge name
        try:
            badge_details["badge_name"] = driver.find_element(
                By.CSS_SELECTOR, "div.cr-badges-full-badge__head-group"
            ).text
        except NoSuchElementException:
            badge_details["badge_name"] = "N/A"

        # Issued by
        try:
            issuer_element = driver.find_element(By.CSS_SELECTOR, "a.cr-badge-organization-name")
            badge_details["issued_by"] = issuer_element.text
        except NoSuchElementException:
            badge_details["issued_by"] = "Unknown"

        # Certificate holder
        try:
            badge_details["certificate_holder"] = driver.find_element(
                By.CSS_SELECTOR, "p.badge-banner-issued-to-text__name-and-celebrator-list"
            ).text
        except NoSuchElementException:
            badge_details["certificate_holder"] = "N/A"

        # Dates (issued + expiry)
        try:
            details = driver.find_element(By.CSS_SELECTOR, "p.cr-badge-banner-issued-at-text").text
            badge_details["dates"] = details
        except NoSuchElementException:
            badge_details["dates"] = "N/A"

        # Check if expired
        text_all = driver.page_source.lower()
        if "expired" in text_all or "expire" in text_all:
            badge_details["is_expired"] = True
        else:
            badge_details["is_expired"] = False

        return badge_details

    except TimeoutException:
        return {"error": "Page load timeout"}
    except Exception as e:
        return {"error": f"Error parsing badge: {str(e)}"}
    finally:
        driver.quit()


# -------------------- Tools List --------------------
tools = [parse_credly_badge, get_certification_points]


# -------------------- LLM Setup --------------------
llm = ChatGroq(groq_api_key=groq_api_key, model="openai/gpt-oss-20b")


# -------------------- Agent Graph --------------------
graph = create_react_agent(llm, tools)


# -------------------- Example Run --------------------
if __name__ == "__main__":
    # Example Credly badge
    test_url = "https://www.credly.com/badges/90ee2ee9-f6cf-4d9b-8a52-f631d8644d58/public_url"
    query = f"How many credit points can I get for this badge? {test_url}"

    response = graph.invoke({"messages": [HumanMessage(content=query)]})
    print("\n--- Final Agent Response ---\n")
    print(response)
