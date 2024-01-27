# Use Red Hat Universal Base Image (UBI) with Python
FROM registry.access.redhat.com/ubi9/python-311

# Set the working directory in the Docker container
WORKDIR /app

# Copy the local package files to the container's workspace
COPY . /app

#Install the Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the command to run the main.py file when the container launches
ENTRYPOINT ["python", "main.py"]
CMD ["--url", "http://127.0.0.1:8880", "--drivers", "http://127.0.0.1:8081", "http://127.0.0.1:8082"]
