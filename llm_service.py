import os
import requests
import feedparser
import urllib.parse
import re
import json
import time
from datetime import datetime
from openai import OpenAI
import config

# Initialize OpenAI client for LM Studio
llm_client = OpenAI(base_url=config.LM_STUDIO_BASE_URL, api_key="not-needed")

def fetch_arxiv(query, since_date=None, max_results=5):
    """Fetch and parse papers from arXiv."""
    base_url = 'http://export.arxiv.org/api/query?'
    search_query = f'all:{query}'
    url = f'{base_url}search_query={urllib.parse.quote(search_query)}&sortBy=submittedDate&sortOrder=descending&max_results={max_results}'

    feed = feedparser.parse(url)
    papers = []

    for entry in feed.entries:
        pub_date = datetime.strptime(entry.published, '%Y-%m-%dT%H:%M:%SZ')
        if since_date and pub_date <= since_date:
            continue

        doi = entry.get('arxiv_doi', '')
        authors = [a.name for a in entry.get('authors', [])]

        papers.append({
            'source': 'arXiv',
            'id': entry.id,
            'title': entry.title,
            'summary': entry.summary,
            'url': entry.link,
            'doi': doi,
            'authors': ", ".join(authors),
            'published': entry.published,
            'pub_date_obj': pub_date
        })
    return papers

def get_elsevier_abstract(api_key, eid):
    """Retrieve full abstract from Elsevier's Abstract Retrieval API if search view isn't enough."""
    url = f"https://api.elsevier.com/content/abstract/eid/{eid}"
    headers = {
        "X-ELS-APIKey": api_key,
        "Accept": "application/json"
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            coredata = data.get('abstracts-retrieval-response', {}).get('coredata', {})
            return coredata.get('dc:description')
    except Exception as e:
        print(f"Error fetching abstract for {eid}: {e}")
    return None

def fetch_elsevier(api_key, query, since_date=None, count=5):
    """Fetch and parse papers from Elsevier Scopus."""
    url = "https://api.elsevier.com/content/search/scopus"
    headers = {
        "X-ELS-APIKey": api_key,
        "Accept": "application/json"
    }
    params = {
        "query": f"TITLE-ABS-KEY({query})",
        "count": count,
        "sort": "-pubdate",
        "view": "STANDARD" # Fallback to STANDARD as COMPLETE failed earlier
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print(f"Elsevier API Error: {response.status_code}")
            return []

        data = response.json()
        entries = data.get('search-results', {}).get('entry', [])
        papers = []

        for entry in entries:
            pub_date_str = entry.get('prism:coverDate', '')
            try:
                pub_date = datetime.strptime(pub_date_str, '%Y-%m-%d')
            except:
                pub_date = datetime.min

            if since_date and pub_date <= since_date:
                continue

            eid = entry.get('eid')
            title = entry.get('dc:title', 'No Title')

            # Try to get abstract. If STANDARD view, it might be missing.
            summary = entry.get('dc:description')
            if not summary and eid:
                print(f"Abstract missing for {title}, trying individual retrieval...")
                summary = get_elsevier_abstract(api_key, eid)

            summary = summary or "No abstract available."

            # Extract links
            links = entry.get('link', [])
            paper_url = next((l.get('@href') for l in links if l.get('@ref') == 'scopus'), "")

            papers.append({
                'source': 'Elsevier',
                'id': entry.get('dc:identifier', eid),
                'title': title,
                'summary': summary,
                'url': paper_url,
                'doi': entry.get('prism:doi', ''),
                'authors': entry.get('dc:creator', 'Unknown Authors'),
                'published': pub_date_str,
                'pub_date_obj': pub_date
            })
        return papers
    except Exception as e:
        print(f"Error fetching Elsevier: {e}")
        return []

def get_detailed_summary(paper):
    """Generate detailed 5-point summary and APA citation using local LLM."""
    system_prompt = "あなたは優秀な研究助手です。論文の内容を日本語で分かりやすく、指定されたフォーマットで正確に要約・翻訳してください。"

    user_prompt = f"""以下の論文のタイトルと要約を日本語に翻訳し、指定されたフォーマットで要点をまとめてください。
また、APA形式の引用（英語のまま）も作成してください。

【メタデータ】
タイトル: {paper['title']}
著者: {paper['authors']}
公開日: {paper['published']}
DOI: {paper['doi']}
URL: {paper['url']}
要約 (Abstract): {paper['summary']}

出力形式:
【日本語タイトル】
**（ここに日本語のタイトルを太字で記入）**

【詳細要約】
``・どんなもの?``
（回答）
``・先行研究と比べてどこがすごい?``
（回答）
``・技術や手法のキモはどこ?``
（回答）
``・どうやって有効だと検証した?``
（回答）
``・議論はある?``
（回答）

【APA引用】
（ここにAPA形式の引用文。DOIやURLも含めること。この項目のみ英語のままで出力してください）
"""

    try:
        response = llm_client.chat.completions.create(
            model=config.LM_STUDIO_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )
        content = response.choices[0].message.content

        # Clean <think> tags
        content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
        return content
    except Exception as e:
        return f"LLM処理エラー: {e}"

def get_detailed_summary_with_custom_prompt(paper, system_prompt, user_prompt):
    """Helper for interactive bot to use specific sample-style prompts."""
    try:
        response = llm_client.chat.completions.create(
            model=config.LM_STUDIO_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )
        content = response.choices[0].message.content
        # Clean <think> tags
        content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
        return content
    except Exception as e:
        return f"LLM処理エラー: {e}"

def send_to_discord(paper, result):
    """Send embed notification to Discord."""
    embed = {
        "title": paper['title'],
        "url": paper['url'],
        "description": result,
        "color": 3447003, # Blue
        "footer": {
            "text": f"Source: {paper['source']} | DOI: {paper.get('doi', 'N/A')}"
        }
    }

    payload = {
        "content": f"**New Paper from {paper['source']}!**\nDirect Link: {paper['url']}",
        "embeds": [embed]
    }

    try:
        response = requests.post(config.DISCORD_WEBHOOK_URL, json=payload)
        return response.status_code in [200, 204]
    except Exception as e:
        print(f"Discord sending error: {e}")
        return False

def send_simple_message_to_discord(message):
    """Send a plain text message to Discord."""
    payload = {"content": message}
    try:
        response = requests.post(config.DISCORD_WEBHOOK_URL, json=payload)
        return response.status_code in [200, 204]
    except Exception as e:
        print(f"Discord simple message sending error: {e}")
        return False
