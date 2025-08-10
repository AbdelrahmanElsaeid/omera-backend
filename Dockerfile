# استخدم Python الرسمي
FROM python:3.11-slim

# إعداد بيئة العمل
WORKDIR /app

# نسخ requirements وتثبيتها
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# نسخ باقي المشروع
COPY . .

# التأكد إن المجلد backend موجود
RUN ls -la && ls -la backend

# البورت اللي هيشتغل عليه Gunicorn
EXPOSE 8000

# أمر التشغيل الافتراضي
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "backend.wsgi:application"]
