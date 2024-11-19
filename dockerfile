FROM python:3.9

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN python manage.py collectstatic --no-input

EXPOSE 8000

CMD ["gunicorn", "--workers=3", "myproject.wsgi:application"]
