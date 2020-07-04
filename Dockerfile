FROM ubuntu:latest
MAINTAINER paulkim "paulracooni@gmail.com"

RUN apt-get update \
  && apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip

WORKDIR /usr/wilt_django
COPY . ./
RUN pip install -r requirements.txt

# WORKDIR /usr/wilt_django/wilt_api
# EXPOSE 7000
# CMD ["python", "manage.py", "makemigrations"]
# CMD ["python", "manage.py", "migrate"]
# CMD ["python", "manage.py", "runserver", "0.0.0.0:7000"]
# ENTRYPOINT ["python3"]
