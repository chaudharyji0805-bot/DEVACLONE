# Base image with Python 3.10 + Node.js (matches Heroku target)
FROM nikolaik/python-nodejs:python3.10-nodejs19

# Fix Debian mirrors (works with old Debian)
RUN sed -i 's|http://deb.debian.org/debian|http://archive.debian.org/debian|g' /etc/apt/sources.list && \
    sed -i '/security.debian.org/d' /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg aria2 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy project into container
WORKDIR /app
COPY . /app

# Upgrade pip
RUN python -m pip install --no-cache-dir --upgrade pip

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Entrypoint
CMD ["bash", "start"]
