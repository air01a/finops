FROM python:3.9-slim


WORKDIR /app
EXPOSE 5000:5000
COPY ./app /app/

RUN pip install --no-cache-dir -r requirements.txt
CMD ["streamlit","run","main.py","--server.port","5000"]
#CMD ["tail", "-f", "/dev/null"]
