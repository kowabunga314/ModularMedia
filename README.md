# ModularMedia

## Docker instrutions to build image and launch the container

cd to the dir with the docker file and run the following commands (**replace the davidspumpkins with your own docker namespace**):

#### Build and launch image
`docker-compose up --build -d`

Navigate to the app in your browser: http://0.0.0.0:6969/

### View running logs
docker logs --tail 50 --follow --timestamps <container_id>
https://docs.docker.com/engine/reference/commandline/logs/

### Database Stuff ###

### Migrate changes to database or models
`flask db migrate`

### Update database with new migrations
`flask db upgrade`

### Undo migrations
`flask db downgrade`
