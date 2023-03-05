FROM node:alpine as build-stage

WORKDIR /app

COPY .npmrc .
COPY .umirc.ts .
COPY package.json .
COPY pnpm-lock.yaml .
COPY src ./src
COPY tsconfig.json .
COPY typings.d.ts .
COPY update_version.sh .

RUN npm install -g pnpm
RUN pnpm install
RUN npm run build
COPY src/pages/index.html ./dist/index.html
COPY src/assets/favicon.ico ./dist/favicon.ico
COPY src/assets/apple-touch-icon.png ./dist/apple-touch-icon.png
COPY src/assets/favicon-16x16.png ./dist/favicon-16x16.png
COPY src/assets/favicon-32x32.png ./dist/favicon-32x32.png
COPY src/assets/og-image.jpg ./dist/og-image.jpg

FROM nginx
COPY --from=build-stage /app/dist/ /usr/share/nginx/html
COPY nginx/nginx.conf /etc/nginx/conf.d/default.conf
