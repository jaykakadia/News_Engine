# News_Engine
Core Vision
A real-time, personalized news intelligence platform that:
    Aggregates news from multiple free sources
    Filters and maps content to user-defined interests
    Triggers alerts (email/notifications) on high-relevance events
    Enables conversational interaction with news (AI chat layer)
    Provides analytics for both users and news agencies

# Cron Job for Ingestion
To start running the news ingestion in the background every hour, use this command in your terminal:
```bash
echo "0 * * * * cd \"/Users/jay/softrefine/Python/ News Engine/Server\" && \"/Users/jay/softrefine/Python/ News Engine/Server/venv/bin/python\" ingest_now.py >> cron_log.log 2>&1" | crontab -
```

### How to turn it off
If you want to stop the background ingestion, simply open your terminal and type:
```bash
crontab -r
```
This will remove the schedule. If you want to use the background scheduler again, just run the setup command above!
