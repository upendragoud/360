# Stage 1: Base stage for installing dependencies and static code analysis tools
FROM python:3.9-slim as base
WORKDIR /app

# Install system dependencies for static code analysis tools

# RUN pip install pylint bandit

# Copy the application code to the Docker image
COPY . /app/spectrum_360

# Stage 2: Compilation and Static Analysis

FROM base as analysis
WORKDIR /app/spectrum_360

# Perform linting
# RUN pylint app config.py run.py plugins

# Perform static code analysis
# RUN bandit -r .

# Stage 3: Build the application image
FROM python:3.9-slim as builder
WORKDIR /app

# Copy compiled and analyzed code from the previous stage
COPY --from=analysis /app/spectrum_360 /app/spectrum_360

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install -r requirements.txt

# Copy the rest of the application (if anything was left out)
COPY . /app/spectrum_360

# Expose the port the app runs on
EXPOSE 8080

# Command to run the application
CMD ["python", "spectrum_360/run.py"]
