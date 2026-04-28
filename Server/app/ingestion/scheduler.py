import time
import threading
from app.ingestion.rss_ingestor import ingest_rss

def run_scheduler():
    """
    Infinite loop that runs the ingestion every hour.
    """
    print("News Scheduler started...")
    while True:
        try:
            ingest_rss()
        except Exception as e:
            print(f"Error during scheduled ingestion: {e}")
        
        # Wait for 1 hour (3600 seconds)
        print("Scheduler sleeping for 1 hour...")
        time.sleep(3600)

def start_scheduler():
    """
    Starts the scheduler in a separate daemon thread.
    """
    thread = threading.Thread(target=run_scheduler, daemon=True)
    thread.start()
