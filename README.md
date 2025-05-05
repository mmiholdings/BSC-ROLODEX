# BSC ROLODEX

This repository contains the Rolodex of contacts for Both Sides of the Camera Studios.

## Data files
- `data/screenwriters.json`: Screenwriter’s database (over 400 agents)
- `data/film.json`: Film database (665 producers & production companies)
- `data/tv-series.json`: TV Series database (455 producers & production companies)
- `data/screenwriter-film.json`: Screenwriter & Film database (1050+ agents & producers)
- `data/screenwriter-tv.json`: Screenwriter & TV database (850+ agents & producers)

## Usage
1. Push this repo to GitHub under username `mmiholdings` with the name `BSC-ROLODEX`.
2. In Netlify, click **New site from Git**, connect your GitHub account, and select `BSC-ROLODEX`.
3. No build command is required; the site will deploy as a static site.

## Fill in contacts
Each JSON file follows this schema:
```json
{
  "meta": {
    "description": "...",
    "count": 0
  },
  "contacts": [
    {
      "name": "Full Name",
      "company": "Company Name",
      "email": "email@example.com",
      "phone": "+1-XXX-XXX-XXXX",
      "notes": ""
    }
  ]
}
```