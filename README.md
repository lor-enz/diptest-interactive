# Interactive Diptest


## Easy project setup with docker

There is a frontend and a backend, that can be built with the docker files in the respective subdirectories. 
If you'll familiar with building docker images, run the familiar commands, otherwise you'll need to wait until I add information in this readme, at a future point in time.

## Project setup for development

There is a frontend and a backend. both in separate folder. 

### Frontend development
The frontend is a node application that is created with Vue. You will find html, javascript and Vue specific code here.
Navigate to the frontend folder and use the familiar yarn commands. I guess you could also use npm.
```
yarn install
yarn serve
yarn build
yarn lint
```

### Backend development
The backend is a Django Server. You will find python code here.
Navigate to the backend folder, here you can run 
```
python manage.py runserver
```
