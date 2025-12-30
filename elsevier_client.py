import requests
from datetime import datetime

def fetch_elsevier_papers(api_key, query, count=5, since_date=None):
    """
    Fetch recent papers from Elsevier Scopus Search API.
    """
    url = "https://api.elsevier.com/content/search/scopus"
    headers = {
        "X-ELS-APIKey": api_key,
        "Accept": "application/json"
    }

    # Scopus query (e.g., TITLE-ABS-KEY(query))
    scopus_query = f"TITLE-ABS-KEY({query})"

    params = {
        "query": scopus_query,
        "count": count,
        "sort": "-pubdate",
        "view": "STANDARD"
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        print(f"Error Elsevier API: {response.status_code} - {response.text}")
        return []

    data = response.json()
    entries = data.get('search-results', {}).get('entry', [])

    papers = []
    for entry in entries:
        paper_id = entry.get('dc:identifier', '')
        title = entry.get('dc:title', 'No Title')
        summary = entry.get('dc:description', 'No Abstract Available')
        doi = entry.get('prism:doi', '')
        authors_str = entry.get('dc:creator', 'Unknown Authors')

        # Scopus pub date is often just YYYY-MM-DD
        pub_date_str = entry.get('prism:coverDate', '')
        try:
            pub_date = datetime.strptime(pub_date_str, '%Y-%m-%d')
        except:
            pub_date = datetime.min

        if since_date and pub_date <= since_date:
            continue

        # Extract link
        links = entry.get('link', [])
        paper_url = ""
        for link in links:
            if link.get('@ref') == 'scopus':
                paper_url = link.get('@href')
                break

        papers.append({
            'id': paper_id,
            'title': title,
            'summary': summary,
            'url': paper_url,
            'doi': doi,
            'authors': authors_str,
            'published': pub_date_str,
            'pub_date_obj': pub_date,
            'source': 'Elsevier'
        })

    return papers

if __name__ == "__main__":
    import config
    print("Fetching papers from Elsevier...")
    papers = fetch_elsevier_papers(config.ELSEVIER_API_KEY, config.SEARCH_QUERY)
    for p in papers:
        print(f"Title: {p['title']}\nURL: {p['url']}\n")
