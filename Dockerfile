FROM python:3

ADD thingino-backup.py /

RUN pip install pyyaml schedule

CMD [ "python", "./thingino-backup.py" ]