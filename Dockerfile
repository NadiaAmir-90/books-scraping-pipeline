FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1 OUTPUT_DIR=/app/output
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY scrapyd.conf /etc/scrapyd/scrapyd.conf
COPY books_scraper/ /app/books_scraper/
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh && mkdir -p /app/output

EXPOSE 6800
ENTRYPOINT ["/app/docker-entrypoint.sh"]
