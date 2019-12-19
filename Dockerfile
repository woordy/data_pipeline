FROM python:3.7 AS base
ARG CI_USER_TOKEN
RUN echo "machine github.com\n  login $CI_USER_TOKEN\n" >~/.netrc

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install git+https://github.com/csci-e-29/2019fa-csci-utils-e-omollo.git#egg=csci-utils

CMD ["python3"]
