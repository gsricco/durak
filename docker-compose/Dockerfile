FROM nginx:stable-alpine

COPY nginx-setup.conf /etc/nginx/conf.d/default.conf
WORKDIR /usr/share/nginx/html
RUN rm -rf ./*
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]