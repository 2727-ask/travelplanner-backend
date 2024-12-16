# Use the official Python image as the base
FROM python:3.11

# Set the working directory in the container
WORKDIR /app

# Copy only the requirements file to leverage Docker's caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install 'uvicorn[standard]'

# Copy the FastAPI application code
COPY . .

# Expose the port FastAPI will run on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
