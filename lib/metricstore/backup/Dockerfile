FROM fedora:25

RUN dnf install -y procps net-tools nss_wrapper gettext findutils
RUN dnf install -y postgresql-9.5.7 postgresql-server-9.5.7 \
                  postgresql-libs-9.5.7 postgresql-contrib-9.5.7 \
    && dnf clean all

# RUN localedef -f UTF-8 -i en_US en_US.UTF-8
COPY conf/passwd.template /${HOME}/passwd.template

ARG POSTGRES_PASSWORD
ENV POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
ARG POSTGRES_USER
ENV POSTGRES_USER=${POSTGRES_USER}
ARG POSTGRES_DB
ENV POSTGRES_DB=${POSTGRES_DB}

ENV PGDATA=/var/lib/pgsql/data \
    CONTAINER_SCRIPTS_PATH=/usr/share/container-scripts/postgresql

# RUN chgrp -R 0 /var/lib/pgsql/ \
#   && chown -R postgres:root /var/lib/pgsql/ \
#   && chmod -R g+rwX /var/lib/pgsql/

# && chmod -R 777 /var/lib/pgsql/data \

# VOLUME ["/var/lib/pgsql/data"]
ADD root /

# USER root
RUN mkdir -p /var/lib/pgsql/data && \
    /usr/libexec/fix-permissions /var/lib/pgsql && \
    /usr/libexec/fix-permissions /var/run/postgresql # && chmod g-rwx $PGDATA

# USER postgres
# RUN /usr/libexec/init-pgsql
RUN su - postgres -c "/usr/libexec/init-pgsql $POSTGRES_PASSWORD $POSTGRES_USER $POSTGRES_DB $CONTAINER_SCRIPTS_PATH"
# $PGDATA
# RUN initdb -A trust -D /var/lib/pgsql/data
# RUN sed -i -r s#'.*listen_addresses.*'#"listen_addresses = '*'"#g /var/lib/pgsql/data/postgresql.conf


# RUN echo -e "\nhost all all all md5" >> /var/lib/pgsql/data/pg_hba.conf
# RUN chgrp -R 0 /var/lib/pgsql/ \
#   && chown -R postgres:root /var/lib/pgsql/ \
#   && chmod -R g+rwX /var/lib/pgsql/

# RUN ls -lh /var/lib/pgsql/data/

COPY docker-entrypoint.sh /
ENTRYPOINT ["/docker-entrypoint.sh"]

EXPOSE 5432

# RUN chown postgres:root /usr/bin/{postgres,postmaster,postgresql-setup} && \
#     chmod 777 /usr/bin/{postgres,postmaster,postgresql-setup}

RUN chown postgres:root /var/lib/pgsql/data/userdata/postgresql.conf && \
    chmod 777 /var/lib/pgsql/data/userdata/postgresql.conf

USER postgres

CMD ["metricstore"]
