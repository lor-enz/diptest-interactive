# Single image: builds the Vue frontend, then serves it together with the Flask API.

# --- Stage 1: build the frontend ---
# Pinned: the Vue CLI toolchain in yarn.lock does not support newer Node versions
FROM node:16-alpine AS frontend
WORKDIR /frontend

# API location, baked in at build time. Relative, because the backend serves
# the frontend and the API (under /api) from the same origin.
ARG VUE_APP_API_URL=/api
ENV VUE_APP_API_URL=$VUE_APP_API_URL

# install the exact dependency versions pinned in yarn.lock
COPY frontend/package.json frontend/yarn.lock ./
RUN yarn install --frozen-lockfile

COPY frontend/ .
RUN yarn build

# --- Stage 2: Flask backend serving API and built frontend ---
FROM python:3.14-slim
WORKDIR /app/backend
COPY backend/requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY backend/ .
COPY --from=frontend /frontend/dist /app/frontend/dist

# run as an unprivileged user; the app files stay root-owned and read-only for it
RUN useradd --system --uid 10001 --no-create-home app
USER app

EXPOSE 5000
CMD [ "python3", "diptest_rest.py"]
