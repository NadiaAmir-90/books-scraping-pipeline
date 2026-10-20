
## 1. Project Overview

The spider starts at the homepage, discovers all book categories from the page itself (no hardcoded category names or URLs), randomly selects 5–10 of them, walks through every page of each selected category, collects all book links, and randomly selects exactly 5 books per category. For each selected book it extracts the required fields, which then flow through a cleaning pipeline and are written to JSON, CSV, XML, and a SQLite database.

## 2. Features

- Dynamic category discovery (nothing hardcoded)
- Random selection of 5–10 categories per run
- Pagination handling, so sampling is done from **all** books in a category
- Exactly 5 random books per category (all books if a category has fewer than 5)
- Configurable start URL (environment variable, settings, or spider argument)
- Item pipelines for cleaning, normalization, numeric conversion, and storage
- Scrapy Feed Exports configured in `settings.py` (JSON, CSV, XML)
- SQLite storage through an Item Pipeline and a repository class
- Docker image with Scrapyd configured and the project auto-deployed
- OOP, SOLID, and DRY structure with docstrings and logging throughout

Extracted fields:

| Field | Description |
|---|---|
| `title` | Book title |
| `price` | Book price (numeric, currency symbol removed) |
| `availability` | `True` if "In stock", otherwise `False` |
| `product_url` | Product details page URL |
| `image_url` | Book image URL |
| `category` | Book category |

## 3. Tech Stack

- Python 3.11+ (3.12 locally)
- Scrapy
- Scrapyd and scrapyd-client
- SQLite (Python standard library `sqlite3`)
- python-dotenv
- Docker
- uv (optional, for local virtual environments without admin rights)

## 4. Installation Guide

### Prerequisites

- Python 3.10 or newer
- Git
- Docker 

### Steps

```bash
git clone https://github.com/NadiaAmir-90/books-scraping-pipeline
cd books-scraping-pipeline
```

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.local/bin/env
uv venv venv
source venv/bin/activate
uv pip install -r requirements.txt
```

### Verify the installation:

```bash
scrapy version
```


## 5. Running the Spider

```bash
cd books_scraper
scrapy crawl bookstore
```

### With a custom start URL:

```bash
scrapy crawl bookstore -a start_url=https://books.toscrape.com/index.html
```

### Verify that the database matches the exported file:

```bash
python - <<'EOF'
import sqlite3, json
db = sqlite3.connect("output/books.db")
print("DB rows:  ", db.execute("SELECT COUNT(*) FROM books").fetchone()[0])
print("JSON rows:", len(json.load(open("output/books.json"))))
EOF
```

## 6. Docker Setup Guide

### Run all Docker commands from the **repository root**.

```bash
cd ~/books-scraping-pipeline
docker rm -f books-scrapyd 2>/dev/null
docker run -d -p 6800:6800 \
  -v $(pwd)/books_scraper/output:/app/output \
  --name books-scrapyd books-scrapyd
docker logs -f books-scrapyd
```

### Useful commands:

```bash
docker ps                          # container status
docker logs books-scrapyd          # Scrapyd and deploy logs
docker stop books-scrapyd          # stop
docker rm -f books-scrapyd         # remove
```

## 7. Scrapyd Deployment Guide

### Inside Docker

#### The project is deployed automatically at container start. Confirm it:

```bash
curl http://localhost:6800/listprojects.json
curl "http://localhost:6800/listspiders.json?project=books_scraper"
```

#### Run the spider through the Scrapyd API:

```bash
curl http://localhost:6800/schedule.json -d project=books_scraper -d spider=bookstore
```

#### Override the start URL for one job :

```bash
curl http://localhost:6800/schedule.json \
  -d project=books_scraper -d spider=bookstore \
  -d start_url=https://books.toscrape.com/index.html
```

#### Check job status:

```bash
curl "http://localhost:6800/listjobs.json?project=books_scraper"
```


#### Cancel a job:

```bash
curl "http://localhost:6800/listjobs.json?project=books_scraper"
curl http://localhost:6800/cancel.json -d project=books_scraper -d job=<jobid>
```

### Without Docker (local Scrapyd)

```bash
# terminal 1
scrapyd

# terminal 2
cd books_scraper
scrapyd-deploy
curl http://localhost:6800/schedule.json -d project=books_scraper -d spider=bookstore
```

### `books_scraper/scrapy.cfg` contains the deploy target:

```ini
[settings]
default = books_scraper.settings

[deploy]
url = http://localhost:6800/
project = books_scraper
```

### Scrapyd configuration (`scrapyd.conf`)

```ini
[scrapyd]
eggs_dir     = /var/lib/scrapyd/eggs
logs_dir     = /var/lib/scrapyd/logs
items_dir    =
dbs_dir      = /var/lib/scrapyd/dbs
jobs_to_keep = 5
max_proc     = 1
bind_address = 0.0.0.0
http_port    = 6800
```

- `bind_address = 0.0.0.0` lets the host reach Scrapyd inside the container.
- `items_dir` is empty so Scrapyd does not add a second feed on top of the `FEEDS` setting.

## 8. Output Format Description

| File | Format | Notes |
|---|---|---|
| `books.json` | JSON array | Indented, UTF-8 |
| `books.csv` | CSV | Header row, fixed column order |
| `books.xml` | XML | One item element per book |

### Example JSON record:

```json
{
    "title": "A Light in the Attic",
    "price": 51.77,
    "availability": true,
    "product_url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
    "image_url": "https://books.toscrape.com/media/cache/2c/da/2cdad67c44b002e7ead0cc35693c0e8b.jpg",
    "category": "Poetry"
}
```

## 9. Database Configuration

- Engine: SQLite
- File: `<OUTPUT_DIR>/books.db` (set through the `SQLITE_PATH` setting)
- Table: `books`

| Column | Type | Notes |
|---|---|---|
| `product_url` | TEXT | Primary key |
| `title` | TEXT | |
| `price` | REAL | Numeric price |
| `availability` | INTEGER | `1` = in stock, `0` = otherwise |
| `image_url` | TEXT | |
| `category` | TEXT | |


### Inspect the data:

```bash
python -c "import sqlite3; print(sqlite3.connect('books_scraper/output/books.db').execute('SELECT * FROM books LIMIT 5').fetchall())"
```

## 10. Folder Structure

```
books-scraping-pipeline/
├── Dockerfile
├── docker-entrypoint.sh
├── requirements.txt
├── scrapyd.conf
├── README.md
├── .gitignore
├── .dockerignore
├── .env.example
└── books_scraper/
    ├── scrapy.cfg
    ├── output/                      # generated: books.json/csv/xml, books.db (git-ignored)
    └── books_scraper/
        ├── __init__.py
        ├── items.py                 # BookItem schema
        ├── middlewares.py
        ├── pipelines.py             # cleaning + SQLite pipelines
        ├── settings.py              # config, feed exports, pipeline order
        ├── services/
        │   ├── __init__.py
        │   ├── extractors.py        # CategoryExtractor, BookExtractor
        │   └── selectors.py         # RandomSelector
        ├── storage/
        │   ├── __init__.py
        │   └── sqlite_repository.py # SQLiteBookRepository
        └── spiders/
            ├── __init__.py
            └── bookstore_spider.py
```

