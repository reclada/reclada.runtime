FROM python3.8

WORKDIR /app

COPY . .

RUN pip install -r srv/requirements.txt
