import config
from elsevier_client import fetch_elsevier_papers
from llm_client import translate_and_summarize
from discord_client import send_to_discord

def test_send():
    print("Fetching one paper from Elsevier for testing...")
    papers = fetch_elsevier_papers(config.ELSEVIER_API_KEY, config.SEARCH_QUERY, count=1)

    if not papers:
        print("No papers found on Elsevier.")
        return

    paper = papers[0]
    print(f"Processing: {paper['title']}")

    # Process with LLM
    print("Calling LLM for translation/summary...")
    llm_result = translate_and_summarize(paper)

    # Send to Discord
    print("Sending to Discord...")
    success = send_to_discord(config.DISCORD_WEBHOOK_URL, paper, llm_result)

    if success:
        print("Successfully sent Elsevier test paper to Discord!")
    else:
        print("Failed to send to Discord.")

if __name__ == "__main__":
    test_send()
