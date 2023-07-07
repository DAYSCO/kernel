#Use pything debian image
FROM python:3.9-slim-buster

#Copy kernel project to image
COPY . .

#install required python packages
RUN pip install --upgrade pip

#install required python packages
RUN pip install -r /requirements.txt

#expose port 5000
EXPOSE 5000

# Start the server
ENTRYPOINT [ "waitress-serve", "--host", "0.0.0.0", "--port", "5000", "run:app" ]