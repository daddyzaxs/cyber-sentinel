# Step 1: Use an official lightweight Python image
FROM python:3.10-slim

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy the requirements file and install libraries
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Step 4: Copy the rest of your app code
COPY . .

# Step 5: Expose the port Flask runs on
EXPOSE 5000

# Step 6: Run the app using Gunicorn (Production-grade server)
# Note: You'll need to add 'gunicorn' to your requirements.txt
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]