FROM nginx

# RUN dnf install -y nss_wrapper gettext

RUN rm /etc/nginx/conf.d/default.conf
# RUN sed -i -r s#^.*listen.*\ 80.*##g /etc/nginx/nginx.conf

RUN sed -i -r s#^user.*##g /etc/nginx/nginx.conf

COPY conf/sarjitsu_nginx.conf.example /etc/nginx/conf.d/sarjitsu_nginx.conf

VOLUME ["/var/cache/nginx"]
RUN chown -R nginx:nginx /var/cache/nginx

# USER nginx

# RUN touch /opt/sarjitsu/src/flaskapp.sock
# RUN chmod 710 /opt/sarjitsu/{src,conf} && chown -R nginx:nginx /opt/sarjitsu
# RUN usermod -a -G root nginx

