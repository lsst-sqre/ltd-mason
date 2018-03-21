FROM alpine:3.7

ARG LTD_MASON_VER=0.2.5

RUN apk add --no-cache --update python3 && \
    pip3 install ltd-mason==${LTD_MASON_VER} --upgrade --no-cache-dir && \
    rm -rf /root/.cache

CMD ["/usr/bin/ltd-mason-travis"]
