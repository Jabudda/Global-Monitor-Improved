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

def fetch_story_published(url):
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            # Try common meta tags for published date
            for prop in [
                {'name': 'article:published_time'},
                {'name': 'pubdate'},
                {'name': 'datePublished'},
                {'name': 'publish-date'},
                {'name': 'date'},
                {'property': 'article:published_time'},
                {'property': 'og:published_time'},
                {'itemprop': 'datePublished'}
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
