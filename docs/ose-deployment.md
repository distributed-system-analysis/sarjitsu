Not in this order. This is strictly for self reference and WIP.

```
sudo iptables -F
oc cluster up
oc login -u system:admin
oc whoami

oc cluster status
```

---

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
