import os
import json
import time
import config
from arxiv_client import fetch_arxiv_papers
from elsevier_client import fetch_elsevier_papers
from llm_client import translate_and_summarize
from discord_client import send_to_discord

from datetime import datetime

def load_sent_papers():
    if os.path.exists(config.SENT_PAPERS_LOG):
        with open(config.SENT_PAPERS_LOG, 'r') as f:
            return set(json.load(f))
    return set()

def save_sent_papers(sent_ids):
    with open(config.SENT_PAPERS_LOG, 'w') as f:
        json.dump(list(sent_ids), f)

def get_last_check_time():
    if os.path.exists(config.LAST_CHECK_FILE):
        with open(config.LAST_CHECK_FILE, 'r') as f:
            try:
                ts = f.read().strip()
                return datetime.fromisoformat(ts)
            except:
                pass
    return None

def save_last_check_time(dt):
    with open(config.LAST_CHECK_FILE, 'w') as f:
        f.write(dt.isoformat())

def main():
    print(f"Starting Brain Wave Paper Bot (Interval: {config.FETCH_INTERVAL_SECONDS}s)...")

    while True:
        sent_ids = load_sent_papers()
        last_check = get_last_check_time()
        current_run_time = datetime.now()

        all_papers = []

        # 1. Fetch papers
        print(f"[{current_run_time.strftime('%Y-%m-%d %H:%M:%S')}] Checking for new papers since {last_check}...")

        print("Fetching from arXiv...")
        try:
            arxiv_papers = fetch_arxiv_papers(config.SEARCH_QUERY, since_date=last_check)
            all_papers.extend(arxiv_papers)
        except Exception as e:
            print(f"Error fetching arXiv: {e}")

        print("Fetching from Elsevier...")
        try:
            elsevier_papers = fetch_elsevier_papers(config.ELSEVIER_API_KEY, config.SEARCH_QUERY, since_date=last_check)
            all_papers.extend(elsevier_papers)
        except Exception as e:
            print(f"Error fetching Elsevier: {e}")

        new_count = 0
        for paper in all_papers:
            if paper['id'] in sent_ids:
                continue

            print(f"Processing new paper: {paper['title']}")

            # 2. LLM Processing
            llm_result = translate_and_summarize(paper)

            # 3. Discord Notification
            success = send_to_discord(config.DISCORD_WEBHOOK_URL, paper, llm_result)

            if success:
                sent_ids.add(paper['id'])
                new_count += 1
                # Avoid hitting limits or overwhelming the user/API
                time.sleep(2)

        # 4. Save progress
        save_sent_papers(sent_ids)
        save_last_check_time(current_run_time)
        print(f"Check complete. Notified {new_count} new papers. Sleeping for {config.FETCH_INTERVAL_SECONDS}s...")

        time.sleep(config.FETCH_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
