docker build . -t wilt_api
docker run -it -v ~/wilt_django/wilt_api:/usr/wilt_django/wilt_api --name test_wilt_api -p 8000:8000 wilt_api /bin/bash
