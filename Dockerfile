FROM python:3.9
ADD socket_server.py server.py
RUN pip install websockets
EXPOSE 8080
CMD ["python", "-u", "server.py"]