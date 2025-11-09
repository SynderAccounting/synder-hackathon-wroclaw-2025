FROM python:3.11-slim

WORKDIR /app

# Copy shared modules
COPY order_generator/ /app/order_generator/
COPY models/ /app/models/

# Copy service-specific files
COPY services/etsy/requirements.txt /app/requirements.txt
COPY services/etsy/app.py /app/app.py

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

# Run the Flask app
CMD ["python", "app.py"]
