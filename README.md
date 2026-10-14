# Interactive Diptest

A website / web application that offers a way to to explore and play around with the Hartigan diptest
([Hartigan & Hartigan 1985, *The Dip Test of Unimodality*](https://doi.org/10.1214/aos/1176346577)).
First "draw" a barchart. It is read as the shape of a distribution (a density), not as counts. The Hartigan Diptest is applied to an ideal sample of n points placed exactly along that shape; n can be picked and only really affects the p-value.

That ideal sample has no sampling noise, so its p-value is not what a real sample of n points would get: noise adds to a real sample's dip, and for a faint dip the difference is large. The tool therefore also shows a **typical p-value**, the median over 100 random samples of n drawn from the shape, and how often those samples reach p < 0.05 (the test's power).

The results (dip value, p-value, modal triangle, low/high) are shown on the histogram and on the sample's empirical cumulative distribution function (ECDF):

- **Modal interval** (low, high): the shaded band.
- **Modal triangle**: a chord of the convex minorant (left of the modal interval) or concave majorant (right of it) and the ECDF point furthest from it. The gap is exactly 2·dip.
- **Race track**: walls at ECDF ± a half-width. The racing line is the shortest path through the track. Turning left means the distribution gets denser, turning right means it thins out, so every switch from left to right is a mode. The dip is half the width of the narrowest track whose racing line has only one mode; a slider shows how narrower tracks force more modes.

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

## Automatic builds and dependency updates

**Docker image.** GitHub Actions (`.github/workflows/build.yml`) lints and builds the frontend, builds the image and smoke-tests the running container. Pull requests are only checked. Pushes to `main`, a weekly run (Mondays) and manual runs also push `nicepenguin/diptestinteractive:latest` and `:<commit>` to Docker Hub. The weekly run rebuilds from scratch, so base-image and Python security fixes arrive even without code changes. A server stays current if it regularly pulls `:latest` and recreates the container, e.g. with a daily `docker compose pull && docker compose up -d`.

**Dependabot** (`.github/dependabot.yml`) opens grouped pull requests for npm and pip packages, base images and GitHub Actions: monthly, security fixes immediately.

**Maintenance**
- Merge Dependabot pull requests once their checks are green. Don't merge red ones; check the failing step first.
- Major updates (e.g. chart.js, vue-chartjs) can pass CI and still break the charts. Click through the app before merging those.
- Pushing needs the repository secrets `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN`. Renew the token before it expires.
- Check now and then that the weekly Build run is green. A failing run means updates have stopped.

## Project setup for development

There is a frontend and a backend. both in separate folders. 

### Frontend development
The frontend is a Vue 3 application built with [Vite](https://vite.dev). You will find html, javascript, typescript and Vue specific code here. It needs Node 22.12 or newer.
Navigate to the frontend folder and use the familiar yarn commands. I guess you could also use _npm_, but that isn't tested.
```
yarn install
yarn build
yarn lint
yarn serve
```

```yarn serve``` starts the Vite dev server on http://localhost:8080 and uses the .env file as supplier for the API url. .env points to the local backend at http://localhost:5000/api


```yarn serve-prod``` does the same, but takes the API url from .env.prodapi, which points at the live backend at https://diptool.lorenz.kiwi/api.


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
