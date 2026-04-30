import os
import sys
from dotenv import load_dotenv

# Add the Server directory to sys.path so we can import modules correctly
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

load_dotenv()

from app.ingestion.rss_ingestor import ingest_rss
from config.config import RSS_FEEDS

def run_once():
    """
    Runs the ingestion for all configured feeds once and then exits.
    Useful for triggering via system cron jobs.
    """
    print(f"Cron job started: Ingesting {len(RSS_FEEDS)} feeds...")
    for url, category in RSS_FEEDS:
        try:
            ingest_rss(url, category)
        except Exception as e:
            print(f"Error during ingestion for {url}: {e}")
    print("Cron cycle complete.")

if __name__ == "__main__":
    run_once()
