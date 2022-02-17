FROM python:3.9
ADD socket_server.py server.py
RUN pip install websockets
RUN pip install psycopg2
EXPOSE 8080
CMD ["python", "-u", "server.py"]