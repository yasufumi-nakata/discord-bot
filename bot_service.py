import os
import json
import time
from datetime import datetime
import config
import llm_service

def load_sent_papers():
    if os.path.exists(config.SENT_PAPERS_LOG):
        with open(config.SENT_PAPERS_LOG, 'r') as f:
            try:
                return set(json.load(f))
            except:
                pass
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

def run_service():
    print(f"--- Brain Wave Paper Service Started (Interval: {config.FETCH_INTERVAL_SECONDS}s) ---")

    while True:
        sent_ids = load_sent_papers()
        last_check = get_last_check_time()
        current_run_time = datetime.now()

        all_papers = []

        print(f"[{current_run_time.strftime('%Y-%m-%d %H:%M:%S')}] Checking papers since {last_check or 'the beginning'}...")

        # Fetch from arXiv
        print("arXiv fetching...")
        arxiv_papers = llm_service.fetch_arxiv(config.SEARCH_QUERY, since_date=last_check)
        all_papers.extend(arxiv_papers)

        # Fetch from Elsevier
        print("Elsevier fetching...")
        elsevier_papers = llm_service.fetch_elsevier(config.ELSEVIER_API_KEY, config.SEARCH_QUERY, since_date=last_check)
        all_papers.extend(elsevier_papers)

        new_count = 0
        for paper in all_papers:
            if paper['id'] in sent_ids:
                continue

            print(f"New paper found: {paper['title']} ({paper['source']})")

            # Detailed summary
            summary_result = llm_service.get_detailed_summary(paper)

            # Send to Discord
            if llm_service.send_to_discord(paper, summary_result):
                sent_ids.add(paper['id'])
                new_count += 1
                time.sleep(2) # Prevent rate limiting

        if new_count == 0:
            print("No new papers found. Sending 'No updates' notification...")
            llm_service.send_simple_message_to_discord("更新ないです")

        save_sent_papers(sent_ids)
        save_last_check_time(current_run_time)
        print(f"Iteration complete. Notified: {new_count}. Sleeping...")

        time.sleep(config.FETCH_INTERVAL_SECONDS)

if __name__ == "__main__":
    run_service()
