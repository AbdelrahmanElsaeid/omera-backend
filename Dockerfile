# 1️⃣ Start from Python image
FROM python:3.11-slim-bullseye

# 2️⃣ Environment settings
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/root/.local/bin:$PATH"

# 3️⃣ Install dependencies
RUN apt-get update && apt-get -y install gcc libpq-dev && apt-get clean

# 4️⃣ Create and set work directory
WORKDIR /app

# 5️⃣ Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# 6️⃣ Copy project files
COPY . /app/

# 7️⃣ Run gunicorn as default
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "config.wsgi:application"]
