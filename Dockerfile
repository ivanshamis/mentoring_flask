FROM python:3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /opt/project
RUN mkdir -p uploads
COPY requirements.txt /opt/project
RUN pip install -r requirements.txt
COPY . /opt/project
EXPOSE 8001
