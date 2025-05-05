import time
            link = c.select_one('h3.title a')
            name = link.get_text(strip=True)
            detail = urljoin(base, link['href'])
            email, phone = fetch_email_phone(detail)
            contacts.append({'name': name, 'company': name, 'email': email, 'phone': phone, 'notes': detail})
        time.sleep(1)
    return contacts

# 4) Audition calls (NYCastings)

def scrape_auditions():
    calls = []
    base = 'https://www.nycastings.com'
    for page in range(1, 6):
        url = f'{base}/jobs/listings?page={page}'
        resp = requests.get(url); resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'html.parser')
        for card in soup.select('div.job-listing'):
            title = card.select_one('h2.title').get_text(strip=True)
            link = urljoin(base, card.select_one('a')['href'])
            date = card.select_one('span.date').get_text(strip=True)
            calls.append({'title': title, 'link': link, 'date': date})
        time.sleep(1)
    return calls

# 5) New productions (Variety RSS)

def scrape_new_productions():
    feed = feedparser.parse('https://variety.com/feed/')
    prods = []
    for entry in feed.entries:
        if 'greenlight' in entry.title.lower() or 'first look' in entry.title.lower():
            prods.append({'title': entry.title, 'link': entry.link, 'published': entry.published})
    return prods

# 6) Script opportunities (Inktip)

def scrape_script_opps():
    url = 'https://www.inktip.com/submit.html'
    resp = requests.get(url); resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    opps = []
    for li in soup.select('div.submission-criteria ul li'):
        opps.append({'text': li.get_text(strip=True)})
    return opps

# Write JSON helper

def write_json(path, desc, data, key='contacts'):
    obj = {'meta': {'description': desc, 'count': len(data)}, key: data}
    with open(path, 'w') as f:
        json.dump(obj, f, indent=2)

# Main runner

def main():
    agents = scrape_agents()
    write_json('data/screenwriters.json', "Screenwriter agents", agents)
    film = scrape_film()
    write_json('data/film.json', "Film companies", film)
    tv = scrape_tv()
    write_json('data/tv-series.json', "TV companies", tv)
    write_json('data/screenwriter-film.json', "Agents + Film", agents + film)
    write_json('data/screenwriter-tv.json', "Agents + TV", agents + tv)
    auditions = scrape_auditions()
    write_json('data/auditions.json', "Audition calls", auditions, key='calls')
    productions = scrape_new_productions()
    write_json('data/new-productions.json', "New productions", productions, key='projects')
    opps = scrape_script_opps()
    write_json('data/script-opportunities.json', "Script opportunities", opps, key='opportunities')

if __name__ == '__main__':
    main()