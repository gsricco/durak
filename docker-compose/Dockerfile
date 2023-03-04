FROM nginx:stable-alpine
#COPY vhost.d/default /etc/nginx/vhost.d/default
COPY nginx-setup.conf /etc/nginx/conf.d/default.conf
WORKDIR /usr/share/nginx/html
RUN rm -rf ./*
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]