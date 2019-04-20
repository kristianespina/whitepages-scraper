# Whitepages Scraper
Target Website: [www.whitepages.com.au](whitepages.com.au)

## What this does
```
Given a list of 11,000 addresses and names, their phone numbers are retrieved from the locations that matched a set criteria of name and address
```

## How to use
```bash
scrapy crawl allsite -t csv -o <filename.csv>
```

## Requirements
- Python 3.6 or above
- Scrapy
- Patience! Scraping thousands might take long
