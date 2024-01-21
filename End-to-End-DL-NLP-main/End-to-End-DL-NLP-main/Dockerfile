FROM python:3.10.13

COPY requirements.txt .

RUN pip install -r requirements.txt

RUN python -c "import nltk;nltk.download('punkt')"

COPY . .

EXPOSE 8080

CMD ["python3", "app.py"]


