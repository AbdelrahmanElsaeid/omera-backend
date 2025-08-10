# استخدم Python الرسمي
FROM python:3.11-slim

# إعداد بيئة العمل
WORKDIR /app

# نسخ requirements وتثبيتها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي المشروع
COPY . .

# التأكد إن المجلد config موجود
RUN ls -la && ls -la config

# البورت اللي هيشتغل عليه Gunicorn
EXPOSE 8000

# أمر التشغيل الافتراضي
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "backend.wsgi:application"]
