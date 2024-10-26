# Use the official Python image.
FROM python:3.9

# Set the working directory in the container.
WORKDIR /app

# Copy the requirements file into the container and install dependencies.
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the rest of the application code.
COPY . .

# Expose port 8000 and start the application.
EXPOSE 8000
CMD ["python", "app.py"]
