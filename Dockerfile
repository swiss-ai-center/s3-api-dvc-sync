FROM python:3.8

ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip

# Copy the current directory contents into the container at /app
COPY . /app

# Set the working directory to /app
WORKDIR /app

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

RUN chmod 644 main.py
