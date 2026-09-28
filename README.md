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

The frontend expects the backend at `/api` on the same domain. Put both containers behind a reverse proxy that forwards `/api/*` to the backend (with the `/api` prefix stripped) and everything else to the frontend. See [Reverse proxy](#reverse-proxy) below.

To point the frontend somewhere else, rebuild it with `docker build --build-arg VUE_APP_API_URL=https://your-backend.example .` (the URL is baked in at build time).

```
docker run -d \ 
-p 8001:8080 \ 
 nicepenguin/diptestinteractive
```

### Reverse proxy

Example nginx config (as used with [SWAG](https://github.com/linuxserver/docker-swag)), assuming the containers are named `dipfront` and `dipback`:

```nginx
server {
    listen 443 ssl;
    server_name diptool.*;
    include /config/nginx/ssl.conf;
    client_max_body_size 0;

    location /api/ {
        include /config/nginx/proxy.conf;
        include /config/nginx/resolver.conf;
        set $upstream_app dipback;
        rewrite ^/api/(.*)$ /$1 break;
        proxy_pass http://$upstream_app:5000;
    }

    location / {
        include /config/nginx/proxy.conf;
        include /config/nginx/resolver.conf;
        set $upstream_app dipfront;
        proxy_pass http://$upstream_app:8080;
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
