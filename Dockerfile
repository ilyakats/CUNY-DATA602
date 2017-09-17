FROM python:alpine

RUN apk update && apk upgrade && \
    apk add --no-cache git

WORKDIR /usr/src/app

# COPY requirements.txt ./
# RUN pip install --no-cache-dir -r requirements.txt
RUN git clone https://github.com/ilyakats/CUNY-DATA602/ /usr/src/app/test-app
# EXPOSE 5000
CMD [ "python", "/usr/src/app/test-app/testscript.py" ]
