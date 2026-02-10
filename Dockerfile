# Use Python 3.10 + Node.js 19 (compatible with tgcalls)
FROM nikolaik/python-nodejs:python3.10-nodejs19

# Fix Debian sources and install dependencies
RUN sed -i 's|http://deb.debian.org/debian|http://archive.debian.org/debian|g' /etc/apt/sources.list && \
    sed -i '/security.debian.org/d' /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg aria2 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy app files
COPY . /app/
WORKDIR /app/

# Upgrade pip and install requirements
RUN python -m pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Start command
CMD ["bash", "start"]
