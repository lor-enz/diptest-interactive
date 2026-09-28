# Interactive Diptest

A website / web application that offers a way to to explore and play around with the Hartigan diptest.
First "draw" a barchart. That barchart represents a histogram for data that could exist. The Hartigan Diptest is applied to a possible data set that would match histogram (the drawn barchart). The application also creates a cumulative distribution function based on the histogram.

The results (dip_value, p_value, modal_triangle, low_high) are displayed plus some info on my own experimental shenanigans. 

It's readily available at [diptool.lorenz.kiwi](https://diptool.lorenz.kiwi/). 


## Docker Container - The easy way of running it yourself. 

A single image contains both the frontend and the backend. The Flask backend serves the app at `/` and the API under `/api` (e.g. `/api/dip-from-histo`).

Feel free to change the port from 5063 to something else.

```
docker run -d \
-p 5063:5000 \
 nicepenguin/diptestinteractive
```

Then open http://localhost:5063.

### Reverse proxy

Example nginx config (as used with [SWAG](https://github.com/linuxserver/docker-swag)), assuming the container is named `diptool`:

```nginx
server {
    listen 443 ssl;
    server_name diptool.*;
    include /config/nginx/ssl.conf;
    client_max_body_size 0;

    location / {
        include /config/nginx/proxy.conf;
        include /config/nginx/resolver.conf;
        set $upstream_app diptool;
        proxy_pass http://$upstream_app:5000;
    }
}
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

```yarn serve``` uses the .env file as supplier for the API url. .env points to the local backend at http://localhost:5000/api


```yarn serve-prod``` is a custom command, defined in package.json. There it overwrites the VUE_APP_API_URL environment variable before running yarn serve.


### Backend development
The backend is a Flask Server. You will find python code here.
Navigate to the backend folder, here you can run 
```
python diptest_rest.py
``` 
The Server will always run on port 5000. It also serves the frontend at http://localhost:5000, if it was built with ```yarn build``` beforehand.

### Building the docker image

Run this command in the **root** folder (with docker daemon running)

```docker build -t diptestinteractive .``` 

The API URL the frontend uses is baked in at build time and defaults to `/api`. To point it somewhere else, add `--build-arg VUE_APP_API_URL=https://your-backend.example/api`.

This is a personal note to myself: 
This is the command to get the right tag to upload it to the docker hub.
```
docker build -t nicepenguin/diptestinteractive .
``` 
This only works for myself.
