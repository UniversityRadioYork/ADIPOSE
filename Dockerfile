FROM python:3-onbuild
COPY . /usr/src/app
CMD ["python", "sequenceController.py"]
EXPOSE 3000
