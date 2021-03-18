FROM python:3

ADD . /www
WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["uwsgi", "uwsgi.ini"]