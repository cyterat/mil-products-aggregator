FROM python:3.12.2-slim

# Create a new user
RUN useradd -m cyterat

# Set the working directory in the container to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Change the ownership of the /app directory to myuser
RUN chown -R cyterat:cyterat /app

# Use the new user to run the application
USER cyterat

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run your script when the container launches
CMD ["python", "telegram-bot.py"]
