import os
import json
import time
from datetime import datetime, timedelta
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

def run_service(test_mode=False):
    print(f"--- Brain Wave Paper Service (Yesterday's Filter) ---")

    while True:
        sent_ids = load_sent_papers()
        current_run_time = datetime.now()
        yesterday = current_run_time - timedelta(days=1)
        yesterday_date = yesterday.date()

        all_papers = []

        print(f"[{current_run_time.strftime('%Y-%m-%d %H:%M:%S')}] Target date: {yesterday_date}")


        # Elsevier
        print("Elsevier fetching...")
        elsevier_results = llm_service.fetch_elsevier(config.ELSEVIER_API_KEY, config.SEARCH_QUERY, count=25)
        elsevier_yesterday = [p for p in elsevier_results if p['pub_date_obj'].date() == yesterday_date]

        if test_mode and not elsevier_yesterday and elsevier_results:
            print("Test Mode: No papers for yesterday on Elsevier, using the latest 3 for demonstration.")
            all_papers.extend(elsevier_results[:3])
        else:
            all_papers.extend(elsevier_yesterday)

        new_count = 0
        for paper in all_papers:
            if paper['id'] in sent_ids and not test_mode:
                continue

            print(f"Processing: {paper['title']} ({paper['source']})")
            summary_result = llm_service.get_detailed_summary(paper)

            if llm_service.send_to_discord(paper, summary_result):
                sent_ids.add(paper['id'])
                new_count += 1
                time.sleep(2)

        if new_count == 0 and not test_mode:
            print("No new papers found for yesterday.")
            # llm_service.send_simple_message_to_discord(f"{yesterday_date}の更新はないです")

        save_sent_papers(sent_ids)

        if test_mode:
            print("Test run complete.")
            break

        print(f"Sleeping for {config.FETCH_INTERVAL_SECONDS}s...")
        time.sleep(config.FETCH_INTERVAL_SECONDS)

if __name__ == "__main__":
    import sys
    is_test = "--test" in sys.argv
    run_service(test_mode=is_test)
