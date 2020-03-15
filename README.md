# ModularMedia

## Docker instrutions to build image and launch the container

cd to the dir with the docker file and run the following commands (**replace the davidspumpkins with your own docker namespace**):

#### Build the image

`docker build -t davidspumpkins/modular .`

#### Launch the container

`docker run -p 6969:6969 davidspumpkins/modular`

Navigate to the app in your browser: http://0.0.0.0:6969/
