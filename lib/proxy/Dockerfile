FROM fedora:25

RUN dnf install --setopt=deltarpm=false -y net-tools procps nss_wrapper gettext nginx

# RUN rm /etc/nginx/nginx.conf

RUN sed -i -r s#^.*listen.*\ 80.*##g /etc/nginx/nginx.conf && \
    sed -i -r s#'^.*listen.*80.*default_server.*'##g /etc/nginx/nginx.conf && \
    sed -i -r s#^user.*##g /etc/nginx/nginx.conf && \
    sed -i -r s#'^.*types_hash_max_size.*'#'    types_hash_max_size 4096;'#g /etc/nginx/nginx.conf

ARG SERVERENDPOINT=web
COPY conf/sarjitsu_nginx.conf.example /etc/nginx/conf.d/sarjitsu_nginx.conf

RUN sed -i -e "s/%%SERVERENDPOINT%%/$SERVERENDPOINT/g" /etc/nginx/conf.d/sarjitsu_nginx.conf

VOLUME ["/var/cache/nginx"]

COPY conf/passwd.template /${HOME}/passwd.template

# RUN useradd -ms /bin/bash nginx

RUN touch /var/run/nginx.pid

# expose ports for nginx
ARG PROXY_PORT
EXPOSE ${PROXY_PORT}

RUN chgrp -R 0 /var/cache/nginx /etc/nginx /var/run/nginx.pid /var/log/nginx/ /var/lib/nginx/ \
  && chmod -R g+rwX /var/cache/nginx /etc/nginx /var/run/nginx.pid /var/log/nginx/ /var/lib/nginx/ \
  && chown -R nginx:root /var/cache/nginx /etc/nginx/ /var/run/nginx.pid /var/log/nginx/ /var/lib/nginx/

COPY docker-entrypoint.sh /
ENTRYPOINT ["/docker-entrypoint.sh"]

USER nginx

CMD ["proxy_server"]
