# youtube extractor container build
FROM python:3.8-alpine
COPY requirements.txt /app/
WORKDIR /app/
COPY . .
RUN pip install -r requirements.txt
CMD python app.py