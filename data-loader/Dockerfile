FROM python:3.9.17-alpine3.18

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt

CMD ["python", "load_ams.py", "&&", "python", "load_pep.py", "&&", "python", "load_sl.py"]