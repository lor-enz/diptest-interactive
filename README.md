# Interactive Diptest


## Docker Containers - The easy way of running this. 

There is a frontend and a backend image, which are run separately.

### Backend

Feel free to change the port from 5063 to something else.

**UNTESTED**
```
docker run -d \ 
-p 5063:5000 \ 
--name diptestbackend \
 nicepenguin/diptestbackend
```

### Frontend

Change the VUE_APP_API_URL variable to the location of your backendserver.
Feel free to change the frontend port from 8001 to something else that works for your setup. 

**UNTESTED**

```
docker run -d \ 
-e VUE_APP_API_URL='www.example.org:5063' \
-p 8001:8080 \ 
--name diptestfrontend \
 nicepenguin/diptestinteractive
```

## Project setup for development

There is a frontend and a backend. both in separate folders. 

### Frontend development
The frontend is a node application that is created with Vue. You will find html, javascript and Vue specific code here.
Navigate to the frontend folder and use the familiar yarn commands. I guess you could also use npm.
```
yarn install
yarn serve
yarn build
yarn lint
```

#### Defining the backend server

define the backend API url as an environment variable named VUE_APP_API_URL either through running the command
``` export VUE_APP_API_URL="localhost:8081" ```
before running yarn serve, or by changing the variable in the ```.env``` file
Or when running docker pass it as an environment variable



### Backend development
The backend is a Flask Server. You will find python code here.
Navigate to the backend folder, here you can run 
```
python diptest_rest.py
``` 
