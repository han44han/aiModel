# استخدام نسخة بايثون جاهزة للذكاء الاصطناعي
FROM python:3.10-slim

# تثبيت متطلبات النظام (المهمة لـ OpenCV و Detectron2)
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx libglib2.0-0 git g++ build-essential \
    && rm -rf /var/lib/apt/lists/*

# تحديد مكان العمل داخل السيرفر
WORKDIR /app

# نسخ الملفات
COPY . .

# تثبيت المكتبات
RUN pip install --no-cache-dir -r requirements.txt

# تشغيل التطبيق
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]