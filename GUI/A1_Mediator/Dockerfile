# Use a basic Ubuntu image
FROM ubuntu:20.04

# Install Python and necessary tools
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && apt-get clean

# Set the working directory
WORKDIR /A1_Mediator

# Copy the requirements file and application code to the container
COPY requirements.txt /A1_Mediator/
COPY app /A1_Mediator/app

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Expose the port FastAPI will run on
EXPOSE 9000

# Set the default command to run the FastAPI app
CMD ["python3", "app/main.py"]
