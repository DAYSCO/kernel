#Use pything debian image
FROM python:3.9-slim-buster

#Copy kernel project to image
COPY . /app/days-kernel

# kernel needs a logs directory
RUN mkdir /app/logs

#install required python packages
RUN pip3 install -r /app/days-kernel/requirements.txt

#expose port 5000
EXPOSE 5000

# Start the server
ENTRYPOINT ["python3","/app/days-kernel/run.py","5000"]