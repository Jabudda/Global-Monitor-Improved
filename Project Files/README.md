# Crisis Management Web Scraper

A web scraper that monitors current events from multiple news sources, ranks them by severity, and displays them on a GitHub Pages website.

## Features

- 🔍 **Multi-Source Scraping**: Fetches news from RSS feeds and APIs
- 📊 **Severity Ranking**: Automatically ranks events by crisis level
- 🌐 **Live Website**: Displays results on GitHub Pages
- ⚡ **Automated Updates**: GitHub Actions runs scraper automatically
- 📱 **Responsive Design**: Mobile-friendly interface

## Severity Criteria

Events are ranked based on:
1. **Keywords**: disaster, crisis, emergency, fatal, casualties
2. **Geographic Scope**: local, regional, national, global
3. **Impact Level**: affected population, economic impact
4. **Urgency**: breaking news vs. ongoing situations

## Setup

### Prerequisites
- Python 3.9 or higher
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/crisis-management-scraper.git
cd crisis-management-scraper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure news sources in `config/sources.json`

4. Run the scraper:
```bash
python scraper/main.py
```

### Live Prices Local Proxy (testing)
For local testing without CORS issues, start the lightweight proxy server:

```bash
python3 scraper/proxy_server.py 8001
```

The frontend auto-detects `localhost` and routes Yahoo Finance requests through `http://localhost:8001/proxy?url=...`.

When not on localhost, it falls back to public proxies (Jina/AllOrigins). We can later switch these calls to a free, documented market API for production.

### Run static site and proxy together
Use the helper script to launch both servers (serves repo root so `/data/events.json` is available):

```bash
bash scripts/run_local.sh
```

Ports are configurable via environment variables:

```bash
PROXY_PORT=8002 STATIC_PORT=8010 bash scripts/run_local.sh

Open the site at `http://localhost:STATIC_PORT/docs/` (e.g., `http://localhost:8010/docs/`).

Alternatively, just open the root and it will redirect:

```
http://localhost:8010/
```
```

## GitHub Pages Deployment

1. Enable GitHub Pages in repository settings
2. Set source to the `docs/` folder
3. GitHub Actions will automatically update the site

## Configuration

Edit `config/sources.json` to add or remove news sources:

```json
{
  "sources": [
    {
      "name": "Example News",
      "type": "rss",
      "url": "https://example.com/rss",
      "enabled": true
    }
  ]
}
```

Edit `config/severity_rules.json` to customize ranking criteria.

## Project Structure

```
.
├── scraper/              # Python scraping modules
│   ├── main.py          # Main scraper script
│   ├── fetcher.py       # News fetching logic
│   └── ranker.py        # Severity ranking algorithm
├── docs/                # GitHub Pages website
│   ├── index.html       # Main webpage
│   ├── styles.css       # Styling
│   └── app.js           # Frontend logic
├── config/              # Configuration files
│   ├── sources.json     # News sources
│   └── severity_rules.json  # Ranking criteria
├── data/                # Generated data files
│   └── events.json      # Latest events data
└── .github/workflows/   # GitHub Actions
    └── scrape.yml       # Automated scraping workflow

```

## License

MIT License

## Contributing

Pull requests are welcome! Please ensure code follows PEP 8 standards.
