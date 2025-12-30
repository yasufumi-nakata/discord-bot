import feedparser
import urllib.parse
from datetime import datetime, timedelta

def fetch_arxiv_papers(query, max_results=5, since_date=None):
    """
    Fetch recent papers from arXiv.
    """
    base_url = 'http://export.arxiv.org/api/query?'
    # Sort by submitted date, descending
    search_query = f'all:{query}'
    url = f'{base_url}search_query={urllib.parse.quote(search_query)}&sortBy=submittedDate&sortOrder=descending&max_results={max_results}'

    feed = feedparser.parse(url)
    papers = []

    for entry in feed.entries:
        # entry.published is in format 'YYYY-MM-DDTHH:MM:SSZ'
        pub_date = datetime.strptime(entry.published, '%Y-%m-%dT%H:%M:%SZ')

        if since_date and pub_date <= since_date:
            continue

        # Extract DOI if available (often in arxiv:doi field)
        doi = entry.get('arxiv_doi', '')

        # Extract authors
        authors = [a.name for a in entry.get('authors', [])]
        authors_str = ", ".join(authors)

        papers.append({
            'id': entry.id,
            'title': entry.title,
            'summary': entry.summary,
            'url': entry.link,
            'doi': doi,
            'authors': authors_str,
            'published': entry.published,
            'pub_date_obj': pub_date,
            'source': 'arXiv'
        })

    return papers

if __name__ == "__main__":
    import config
    print("Fetching papers from arXiv...")
    papers = fetch_arxiv_papers(config.SEARCH_QUERY)
    for p in papers:
        print(f"Title: {p['title']}\nURL: {p['url']}\n")
