#!/bin/bash

set -e


log(){
  echo -e "[$(date +'%D %H:%M:%S %Z')] - $*"
}

# Add as command if needed
if [ "${1:0:1}" = '-' ]; then
  set -- proxy_server "$@"
fi

if [ "$1" = 'proxy_server' ]; then
  export USER_ID=$(id -u)
  export GROUP_ID=$(id -g)
  envsubst < /passwd.template > /tmp/passwd
  export LD_PRELOAD=/usr/lib64/libnss_wrapper.so
  export NSS_WRAPPER_PASSWD=/tmp/passwd
  export NSS_WRAPPER_GROUP=/etc/group

  echo $(id)

  /usr/bin/rm -f /run/nginx.pi
  /usr/sbin/nginx -t
  /usr/sbin/nginx -g 'daemon off;'

fi

exec "$@"
