# INSTALLATION

Refer to Official Openshift docs for single node Openshift cluster installation through docker.
Once you have the `oc` origin client installed and all requirements fullfilled, proceed as follows:

```
sudo iptables -F

# needs connection to internet
oc cluster up
oc login -u system:admin
oc whoami

# optionally, to be able to access all projects in web UI of Openshift, from `admin` a/c (pass: `admin`), do this:
sudo oadm policy add-cluster-role-to-user cluster-admin admin --config=/var/lib/origin/openshift.local.config/master/admin.kubeconfig
oadm policy add-role-to-user cluster-admin admin

oc cluster status
```

Note:

If you're looking to proceed with sarjitsu installation from here on, continue to Step 2 of Openshift deployment, as per README.md

Everything below, is just self reference garbage.

---


## Guiding light (sample OCP commands)

Not in this order. This is strictly for self reference.

```
oc new-project arco
oc create -f openshift/templates/
kompose -f docker-compose.yml convert --provider openshift --stdout | oc create -f -

oc get is
oc tag datasource:latest datasource:elasticsearch
oc import-image datasource
oc import-image datasource:elasticsearch

oc get bc

oc edit bc datasource
oc delete bc datasource
oc describe is datasource
oc edit dc datasource
oc start-build datasource -e ES_PORT=9200
oc apply -f openshift/templates/datasource-buildconfig.yaml

oc rollout latest datasource --again
oc rollout latest datasource -h
oc get dc
oc deploy datasource --cancel
oc deploy datasource --latest
oc get pods
oc logs -f dc/datasource

oc get services
curl 172.30.32.23:9200

oc adm policy add-scc-to-user anyuid -n sarjitsu -z default
oc get pods


oc get dc,svc,is,pvc
oc logs datasource-1-build

```


```
kompose -f docker-compose.yml convert --provider openshift -o openshift/templates/
# oc create -f openshift/templates/

OSE_TEMPLATES="middleware-service.yaml,web-service.yaml,datasource-service.yaml,frontend-service.yaml,metricstore-service.yaml"

cd openshift/templates/ && kubectl create -f $OSE_TEMPLATES; cd ../../
## $(ls | paste -sd,)

kubectl describe pod datasource-1-build

oc get pods

oc get services

oc status -v

kompose up --provider openshift
kompose down
kubectl get deployment,svc,pods,pvc

cd openshift/templates/ && kubectl delete -f $OSE_TEMPLATES; cd ../../

```
