# FROM ubuntu:latest
MAINTAINER paulkim "paulracooni@gmail.com"

RUN apt-get update \
  && apt-get install -y python3-pip python3-dev default-libmysqlclient-dev build-essential \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip

RUN export WILT_ENV=production
WORKDIR /usr/wilt_django
COPY . ./
RUN pip install -r requirements.txt

WORKDIR /usr/wilt_django/wilt_api
RUN python manage.py makemigrations
RUN python manage.py migrate
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
# ENTRYPOINT ["python3"]

# WILT_ENV=production
# set WILT_ENV=production
