# LangGraph-studio
# Goal - 
The main goal of this agent is to:

Extract certification information (like name, issuer, issue date, and expiration date) from a Credly badge URL using Selenium automation.

Check and calculate credit points for each certification by querying an internal SQLite database (certifications_data.db).

Reason intelligently about validity and point eligibility — for example, identifying expired certificates and explaining point allocations clearly.

Respond conversationally to user queries such as:

How many credit points can I get for this certification?
Has my badge expired?

# User Interaction -
How Users Interact with the Agent

## System Componenet - 
# 1. LangGraph Agent

The agent is built using the ReAct (Reason + Act) framework from LangGraph.
It connects an LLM (ChatGroq) with functional tools like:

parse_credly_badge(url) → Extracts certification details from the web.

get_certification_points(cert_name) → Fetches points for the corresponding certificate from the SQLite database.

This allows the agent to decide when to call a tool, interpret the output, and generate a natural-language response.

# 2. ChatGroq LLM 
The ChatGroq model serves as the reasoning brain of the agent.
It interprets user questions, determines intent, calls appropriate tools, and generates conversational responses like:

“Sorry, your certification has expired, so you won’t get any credit points. Otherwise, you would have earned 5 credit points for your HashiCorp Terraform cert.”

# 3 . 3. SQLite Database

A lightweight database (certifications_data.db) is used to store mapping between certification categories and their point values.

cert_name	                     points
Any Professional or Specialty	 10
Any Associate or Hashicorp	    5
Anything Else	                 2.5

This ensures efficient and persistent lookup of credit points.

# 4. 4. Selenium Web Scraper

The Selenium module automates a headless browser to open Credly badge URLs and extract:

Certification name

Issuing organization

Certificate holder’s name

Issue and expiry dates

These details are then passed to the LLM for reasoning and presentation.

## Diagram(Text Representation )

                          ┌──────────────────────────┐
                          │        User Input        │
                          │ (Credly URL or question) │
                          └────────────┬─────────────┘
                                       │
                                       ▼
                    ┌────────────────────────────────────┐
                    │     LangGraph ReAct Agent          │
                    │  (Reasoning + Tool Coordination)   │
                    └────────────┬───────────────────────┘
                                 │
              ┌──────────────────┴──────────────────┐
              │                                     │
              ▼                                     ▼
 ┌──────────────────────────┐          ┌──────────────────────────┐
 │ parse_credly_badge Tool  │          │ get_certification_points │
 │ (Selenium Web Scraper)   │          │ (SQLite Database Query)  │
 │ - Fetches:               │          │ - Fetches points from    │
 │   • Badge name           │          │   certifications_table   │
 │   • Issuer               │          │ - Matches cert name →    │
 │   • Issue & expiry dates │          │   credit points          │
 └────────────┬─────────────┘          └────────────┬─────────────┘
              │                                     │
              └──────────────────┬──────────────────┘
                                 ▼
                    ┌────────────────────────────────────┐
                    │         ChatGroq LLM               │
                    │ (Understands + Generates Response) │
                    └──────────────────┬─────────────────┘
                                       │
                                       ▼
                          ┌──────────────────────────┐
                          │  Conversational Output    │
                          │ e.g., “Your cert expired │
                          │ so you won’t get points.”│
                          └──────────────────────────┘
## Prerequisites

LangGraph → ReAct-style reasoning agent framework

ChatGroq → LLM backend for reasoning and conversation

Selenium → Automated web scraping for badge details

SQLite → Lightweight local database for credit points

Python 3.11 → Core implementation language

### installation and Sequence of Commands 
python -m venv env
env\Scripts\activate
set GROQ_API_KEY=your api key
set LANGSMITH_API_KEY=your api key
pip install langgraph
pip install --upgrade "langgraph-cli[inmem]"
python react_agent.py
langgraph dev

