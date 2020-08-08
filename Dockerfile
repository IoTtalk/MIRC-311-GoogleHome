FROM python:3.7-alpine

WORKDIR /voicetalk

COPY voicetalk-src /voicetalk-src

RUN apk update && \
    apk add -t BUILD gcc musl-dev linux-headers libffi-dev && \
    pip3 install /voicetalk-src && \
    apk del BUILD && \
    voice-talk genconf voicetalk.ini.sample && \
    voice-talk gen-sample-device-file device.json.sample
