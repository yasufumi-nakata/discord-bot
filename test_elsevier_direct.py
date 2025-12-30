import config
from elsevier_client import fetch_elsevier_papers
from discord_client import send_to_discord

def test_direct():
    print("Fetching one paper from Elsevier (DIRECT TEST, NO LLM)...")
    papers = fetch_elsevier_papers(config.ELSEVIER_API_KEY, config.SEARCH_QUERY, count=1)

    if not papers:
        print("No papers found on Elsevier.")
        return

    paper = papers[0]
    print(f"Processing: {paper['title']}")

    # Mock LLM result for instant test
    llm_result = "【テスト通知】\nこれはエルゼビアAPIの動作確認用テストです。LLMをバイパスして送信しています。"

    print("Sending to Discord...")
    success = send_to_discord(config.DISCORD_WEBHOOK_URL, paper, llm_result)

    if success:
        print("Successfully sent Elsevier direct test to Discord!")
    else:
        print("Failed to send to Discord.")

if __name__ == "__main__":
    test_direct()
