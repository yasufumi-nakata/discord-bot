from openai import OpenAI
import config

client = OpenAI(base_url=config.LM_STUDIO_BASE_URL, api_key="not-needed")

import re

def translate_and_summarize(paper_info):
    """
    Translate title and summary to Japanese, and generate APA citation.
    """
    title = paper_info['title']
    summary = paper_info['summary']
    authors = paper_info.get('authors', 'Unknown')
    pub_date = paper_info.get('published', '')
    doi = paper_info.get('doi', '')
    url = paper_info['url']

    prompt = f"""以下の論文のタイトルと要約を日本語に翻訳し、重要なポイントを簡潔にまとめてください。
また、提供されたメタデータを使用してAPA形式の引用を作成してください。

【メタデータ】
タイトル: {title}
著者: {authors}
公開日: {pub_date}
DOI: {doi}
URL: {url}
要約: {summary}

出力形式:
【日本タイトル】
（ここに日本語のタイトル）

【要約】
（ここに3点ほどの箇条書きで要点）

【APA引用】
（ここにAPA形式の引用。DOIやURLも含めること）
"""

    try:
        response = client.chat.completions.create(
            model=config.LM_STUDIO_MODEL,
            messages=[
                {"role": "system", "content": "あなたは優秀な研究助手です。論文の内容を日本語で分かりやすく、かつ正確に翻訳・要約してください。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        content = response.choices[0].message.content

        # Remove <think>...</think> blocks if present
        content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()

        return content
    except Exception as e:
        return f"LLM処理中にエラーが発生しました: {str(e)}"

if __name__ == "__main__":
    test_paper = {
        'title': "A Brain-Computer Interface for everyone",
        'summary': "This paper describes a new BCI system that uses EEG to control robots.",
        'authors': "John Doe, Jane Smith",
        'published': "2025-12-30",
        'doi': "10.1234/test.doi",
        'url': "https://arxiv.org/abs/1234.5678"
    }
    print("Testing LLM translation...")
    result = translate_and_summarize(test_paper)
    print(result)
