import os
import json
import feedparser
from datetime import datetime

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

def main():
    sources_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'sources.json')
    events_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'events.json')
    rules_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'severity_rules.json')
    sources = load_sources(sources_path)
    rules = load_severity_rules(rules_path)
    all_events = []
    for source in sources:
        print(f"Fetching: {source['name']} ({source['url']})")
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
            # Apply severity rules
            scored = score_event(event, rules)
            event['severity'] = scored['severity']
            event['scope'] = scored['scope']
            event['matched_keywords'] = scored['matched_keywords']
            all_events.append(event)
    # Save events to events.json
    with open(events_path, 'w') as f:
        json.dump({'events': all_events, 'last_updated': datetime.utcnow().isoformat() + 'Z'}, f, indent=2)
    print(f"Saved {len(all_events)} events to {events_path}")

if __name__ == "__main__":
    main()
