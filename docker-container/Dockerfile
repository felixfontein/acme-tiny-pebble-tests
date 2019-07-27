FROM golang:1.10-stretch as builder
# Install pebble
ARG PEBBLE_REMOTE=
ARG PEBBLE_CHECKOUT="ddbb755c42b4c087caae93dc181e6353dd54cedb"
ENV GOPATH=/go
RUN go get -u github.com/letsencrypt/pebble/...
RUN cd /go/src/github.com/letsencrypt/pebble && \
    if [ "${PEBBLE_REMOTE}" != "" ]; then \
      git remote add other ${PEBBLE_REMOTE} && \
      git fetch other && \
      git checkout -b other-${PEBBLE_CHECKOUT} --track other/${PEBBLE_CHECKOUT}; \
    else \
      git checkout ${PEBBLE_CHECKOUT}; \
    fi && \
    go install ./...

FROM python:3.6-slim-stretch
# Install software
ADD requirements.txt /root/
RUN pip3 install -r /root/requirements.txt
# Install pebble
COPY --from=builder /go/bin /go/bin
COPY --from=builder /go/pkg /go/pkg
COPY --from=builder /go/src/github.com/letsencrypt/pebble/test /go/src/github.com/letsencrypt/pebble/test
ADD pebble-config.json /go/src/github.com/letsencrypt/pebble/test/config/pebble-config.json
# Setup controller.py and run.sh
ADD run.sh controller.py dns_server.py LICENSE README.md /root/
EXPOSE 53 80 14000 15000
CMD [ "/bin/sh", "-c", "/root/run.sh" ]
