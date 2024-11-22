# Use the official Python image.
FROM python:latest
ENV DEBIAN_FRONTEND=noninteractive
# Set the working directory in the container.
WORKDIR /app

RUN apt-get -y update
RUN apt-get -y install nano sudo ffmpeg wget curl mediainfo mkvtoolnix stun
RUN wget -q https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get install -y ./google-chrome-stable_current_amd64.deb

# Copy the requirements file into the container and install dependencies.
COPY requirements.txt .
RUN pip install -r requirements.txt
# Copy the rest of the application code.
COPY . .

# Expose port 8000 and start the application.
EXPOSE 8000
CMD ["python", "app.py"]
