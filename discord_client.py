import requests
import json

def send_to_discord(webhook_url, paper_info, llm_result):
    """
    Send formatted paper info and LLM summary to Discord webhook.
    """
    embed = {
        "title": paper_info['title'],
        "url": paper_info['url'],
        "description": llm_result,
        "color": 3447003,  # Blue
        "footer": {
            "text": f"Source: {paper_info['source']} | DOI: {paper_info.get('doi', 'N/A')}"
        }
    }

    # Add explicit URL field if someone wants to copy-paste easily
    payload = {
        "content": f"**Source URL:** {paper_info['url']}",
        "embeds": [embed]
    }

    response = requests.post(webhook_url, json=payload)

    if response.status_code not in [200, 204]:
        print(f"Error Discord Webhook: {response.status_code} - {response.text}")
        return False
    return True

if __name__ == "__main__":
    import config
    test_paper = {
        'title': 'Test Paper Title',
        'url': 'https://arxiv.org/abs/1234.5678',
        'source': 'arXiv',
        'published': '2025-12-30'
    }
    test_llm = "【日本タイトル】\nテスト論文タイトル\n\n【要約】\n- 要点1\n- 要点2"
    print("Testing Discord notification...")
    send_to_discord(config.DISCORD_WEBHOOK_URL, test_paper, test_llm)
