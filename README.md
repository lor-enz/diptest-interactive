# Interactive Diptest

A website / web application that offers a way to to explore and play around with the Hartigan diptest.
First "draw" a barchart. That barchart represents a histogram for data that could exist. The Hartigan Diptest is applied to a possible data set that would match histogram (the drawn barchart). The application also creates a cumulative distribution function based on the histogram.

The results (dip_value, p_value, modal_triangle, low_high) are displayed plus some info on my own experimental shenanigans. 

It's readily available at [diptool.lorenz.kiwi](https://diptool.lorenz.kiwi/). 


## Docker Containers - The easy way of running it yourself. 

There is a frontend and a backend image, which are run separately.

### Backend

Feel free to change the port from 5063 to something else.

```
docker run -d \ 
-p 5063:5000 \ 
 nicepenguin/diptestbackend
```

### Frontend

Feel free to change the frontend port from 8001 to something else that works for your setup. 

~~Change the VUE_APP_API_URL environment variable to the location of your backendserver.~~

**Unfortunately the backend URL is hard set to '_dipapi.lorenz.kiwi_'. Changing the API requires changing the dockerfile and running docker build again.**

```
docker run -d \ 
-p 8001:8080 \ 
 nicepenguin/diptestinteractive
```

## Project setup for development

There is a frontend and a backend. both in separate folders. 

### Frontend development
The frontend is a node application that is created with Vue. You will find html, javascript, typescript and Vue specific code here.
Navigate to the frontend folder and use the familiar yarn commands. I guess you could also use _npm_, but that isn't tested.
```
yarn install
yarn build
yarn lint
yarn serve
```

```yarn serve``` uses the .env file as supplier for the API url. .env defines localhost as the URL environment variable


```yarn serve-prod``` is a custom command, defined in package.json. There it overwrites the VUE_APP_API_URL environment variable before running yarn serve.


### Backend development
The backend is a Flask Server. You will find python code here.
Navigate to the backend folder, here you can run 
```
python diptest_rest.py
``` 
The Server will always run on port 5000.

### Building the docker images

Navigate to **frontend** folder and run this command (with docker daemon running)

```docker build -t diptestinteractive .``` 

Navigate to **backend** folder and run this command (with docker daemon running)

```docker build -t diptestbackend .``` 

This is a personal note to myself: 
These are the commmands to get the right tags to upload them to the docker hub.
```
docker build -t nicepenguin/diptestinteractive .
docker build -t nicepenguin/diptestbackend .
``` 
This only works for myself.
