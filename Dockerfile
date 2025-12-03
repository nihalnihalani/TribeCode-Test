FROM python:3.9-slim

WORKDIR /app

# Install system dependencies if needed (e.g. for playwright)
# RUN apt-get update && apt-get install -y ...

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install chromium
RUN playwright install-deps

COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "src.web.app:app", "--host", "0.0.0.0", "--port", "8000"]

