FROM node:alpine as build-stage

WORKDIR /app

COPY .npmrc .
COPY .umirc.ts .
COPY package.json .
COPY pnpm-lock.yaml .
COPY src ./src
COPY tsconfig.json .
COPY typings.d.ts .

RUN npm install -g pnpm
RUN pnpm install
RUN npm run build

FROM nginx
COPY --from=build-stage /app/dist/ /usr/share/nginx/html
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf
