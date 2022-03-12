FROM python:3.9
RUN apt update && apt -y install gettext-base
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV CONFIGPATH ./config/config.yaml
CMD ["sh", "-c", "/start.sh"]
