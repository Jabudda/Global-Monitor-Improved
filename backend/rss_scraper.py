import os
import json
import feedparser
from datetime import datetime
import requests
from bs4 import BeautifulSoup

def load_sources(path):
    with open(path, 'r') as f:
        data = json.load(f)
    return [s for s in data['sources'] if s.get('enabled', True)]

def fetch_rss(url):
    return feedparser.parse(url)

def load_severity_rules(path):
    with open(path, 'r') as f:
        return json.load(f)

def score_event(event, rules):
    text = (event.get('title', '') + ' ' + event.get('summary', '')).lower()
    matched = {"severity": None, "scope": None, "matched_keywords": []}
    # Severity
    for level in ["critical", "high", "medium", "low"]:
        for kw in rules["keywords"].get(level, []):
            if kw.lower() in text:
                matched["severity"] = level
                matched["matched_keywords"].append(kw)
                break
        if matched["severity"]:
            break
    if not matched["severity"]:
        matched["severity"] = "default"
    # Geographic scope
    for scope in ["global", "national", "regional", "local"]:
        for kw in rules.get("geographic_scope", {}).get(scope, []):
            if kw.lower() in text:
                matched["scope"] = scope
                break
        if matched["scope"]:
            break
    return matched

from urllib.parse import urlparse

PUBLISHED_DATE_SELECTORS = {
    "abcnews.go.com": [
        {"tag": "meta", "attr": {"name": "datePublished"}},
        {"tag": "meta", "attr": {"property": "article:published_time"}},
    ],
    "bbc.com": [
        {"tag": "meta", "attr": {"property": "article:published_time"}},
        {"tag": "time", "attr": {"data-testid": "timestamp"}},
    ],
    "foxnews.com": [
        {"tag": "meta", "attr": {"itemprop": "datePublished"}},
        {"tag": "meta", "attr": {"property": "article:published_time"}},
        {"tag": "time", "attr": {"datetime": True}},
    ],
    "theguardian.com": [
        {"tag": "meta", "attr": {"property": "article:published_time"}},
        {"tag": "time", "attr": {"itemprop": "datePublished"}},
    ],
    "aljazeera.com": [
        {"tag": "meta", "attr": {"property": "article:published_time"}},
        {"tag": "span", "attr": {"class": "date-simple"}},
    ],
    "france24.com": [
        {"tag": "meta", "attr": {"property": "article:published_time"}},
        {"tag": "span", "attr": {"class": "m-date"}},
    ],
    "dw.com": [
        {"tag": "meta", "attr": {"property": "article:published_time"}},
        {"tag": "span", "attr": {"class": "date"}},
    ],
    "cnn.com": [
        {"tag": "meta", "attr": {"name": "pubdate"}},
        {"tag": "meta", "attr": {"property": "og:pubdate"}},
        {"tag": "meta", "attr": {"itemprop": "datePublished"}},
        {"tag": "p", "attr": {"class": "update-time"}},
    ],
}

def fetch_story_published(url):
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code != 200:
            return None
        soup = BeautifulSoup(resp.text, 'html.parser')
        domain = urlparse(url).netloc
        # Remove subdomains for matching
        domain_parts = domain.split('.')
        if len(domain_parts) > 2:
            domain = '.'.join(domain_parts[-3:]) if domain_parts[-2] in ("co", "com", "org", "net") else '.'.join(domain_parts[-2:])
        selectors = PUBLISHED_DATE_SELECTORS.get(domain, [])
        # Try site-specific selectors
        for sel in selectors:
            tag = sel["tag"]
            attr = sel.get("attr", {})
            if tag == "meta":
                meta = soup.find("meta", attrs=attr)
                if meta and meta.get("content"):
                    return meta["content"]
            elif tag == "time":
                time_tag = soup.find("time", attrs={k: v for k, v in attr.items() if v is not True})
                if time_tag and ("datetime" in time_tag.attrs):
                    return time_tag["datetime"]
            else:
                el = soup.find(tag, attrs=attr)
                if el and el.text:
                    return el.text.strip()
        # Fallback: try common meta tags
        for prop in [
            {"name": "article:published_time"},
            {"name": "pubdate"},
            {"name": "datePublished"},
            {"name": "publish-date"},
            {"name": "date"},
            {"property": "article:published_time"},
            {"property": "og:published_time"},
            {"itemprop": "datePublished"}
        ]:
            meta = soup.find('meta', attrs=prop)
            if meta and meta.get('content'):
                return meta['content']
        # Fallback: look for time tag
        time_tag = soup.find('time')
        if time_tag and time_tag.get('datetime'):
            return time_tag['datetime']
        return None
    except Exception:
        return None

def main():
    sources_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'sources.json')
    events_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'events.json')
    rules_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'severity_rules.json')
    sources = load_sources(sources_path)
    rules = load_severity_rules(rules_path)
    all_events = []
    for source in sources:
        feed = fetch_rss(source['url'])
        for entry in feed.entries:
            event = {
                'source': source['name'],
                'title': entry.get('title', ''),
                'link': entry.get('link', ''),
                'published': entry.get('published', ''),
                'summary': entry.get('summary', ''),
                'fetched_at': datetime.utcnow().isoformat() + 'Z'
            }
            # Fetch actual story published date from HTML
            story_published = fetch_story_published(event['link'])
            if story_published:
                event['story_published'] = story_published
            # Apply severity rules
            scored = score_event(event, rules)
            event['severity'] = scored['severity']
            event['scope'] = scored['scope']
            event['matched_keywords'] = scored['matched_keywords']
            all_events.append(event)
    # Save events to events.json
    with open(events_path, 'w') as f:
        json.dump({'events': all_events, 'last_updated': datetime.utcnow().isoformat() + 'Z'}, f, indent=2)
    # Saved {len(all_events)} events to {events_path} (removed print for clean logs)

if __name__ == "__main__":
    main()
