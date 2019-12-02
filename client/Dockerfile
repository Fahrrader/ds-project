FROM python:3.7-alpine
# Copy particular file
COPY requirements.txt /tmp/
# Execute commands inside container, so that you can customize it
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt
# Create and cd to this directory, set default command to run container
WORKDIR /app
# Copy files from project dir into container’s folder
COPY ./ /app
# Specify port that could(!) be opened from container later
EXPOSE 12607 19609
# CMD python3 name_server.py