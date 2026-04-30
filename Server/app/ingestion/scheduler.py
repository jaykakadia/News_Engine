import time
import threading
from app.ingestion.rss_ingestor import ingest_rss
from config.config import RSS_FEEDS

def run_scheduler():
    """
    Infinite loop that runs the ingestion for all configured feeds every hour.
    """
    print(f"News Scheduler started with {len(RSS_FEEDS)} feeds...")
    while True:
        for url, category in RSS_FEEDS:
            try:
                ingest_rss(url, category)
            except Exception as e:
                print(f"Error during scheduled ingestion for {url}: {e}")
        
        # Wait for 1 hour (3600 seconds)
        print("Scheduler cycle complete. Sleeping for 5 minute...")
        time.sleep(300)

def start_scheduler():
    """
    Starts the scheduler in a separate daemon thread.
    """
    thread = threading.Thread(target=run_scheduler, daemon=True)
    thread.start()
