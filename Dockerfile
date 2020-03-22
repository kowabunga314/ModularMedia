FROM python:3

# set a directory for the app
WORKDIR /usr/src/app

# copy all the files to the container
COPY . .

ENV FLASK_APP "app"
ENV FLASK_DEBUG True

# install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# tell the port number the container should expose
EXPOSE 5000


# run the command
CMD ["python", "./dbcreate.py"]
CMD flask run --host=0.0.0.0
