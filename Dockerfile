FROM python:3.6.10-buster
COPY . /app
WORKDIR /app
RUN curl -sL https://deb.nodesource.com/setup_14.x | bash - && \
    apt update && \
    apt -y install git nodejs && \
    pip3 install -r requirements.txt && \
    cd /app/engage_ui/static/ && \
    npm install
EXPOSE 5000
ENTRYPOINT [ "python3", "run.py" ]
CMD []
