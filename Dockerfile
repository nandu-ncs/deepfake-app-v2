# Use an official Python runtime as a parent image
FROM python:3.10.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    cmake \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /python-docker

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .
RUN ls
# Create a new group with gid 10016
RUN addgroup --gid 10016 choreo

# Create a new user with UID 10016 and add it to the group
RUN adduser --disabled-password --no-create-home --uid 10016 --ingroup choreo choreouser

USER 10016
EXPOSE 5000
CMD [ "flask", "run", "--host=0.0.0.0"]