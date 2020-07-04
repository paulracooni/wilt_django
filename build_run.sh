docker build --tag wilt_api:0.0.1 .
docker run -it -v ./wilt_api:/usr/wilt_django/wilt_api --name test_wilt_api -p 7000:7000 wilt_api:0.0.1 /bin/bash
