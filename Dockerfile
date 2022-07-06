FROM python:3.9

WORKDIR /app

ADD app.py .

EXPOSE 5000

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

CMD ["python", "app.py"]