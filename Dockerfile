FROM python:3-alpine3.7

ENV PROXY=
ENV HTTP_PROXY=$PROXY
ENV HTTPS_PROXY=$PROXY
ENV PYTHONUNBUFFERED 1

COPY ./???-ca-bundle.crt /usr/local/share/ca-certificates/???-ca-bundle.crt
RUN update-ca-certificates

ADD ./requirements.txt /
RUN pip install -r requirements.txt
ADD ./gitlab_stats.py /
ENTRYPOINT ["python3", "./gitlab_stats.py"]
