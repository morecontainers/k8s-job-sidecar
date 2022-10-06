Job sidecar termination service.

Public domain software.  Original code by Henrik Holst <hholst@pm.me>.

Pending the availability of an upstream solution:

https://github.com/kubernetes/enhancements/pull/3580

The service will send a SIGTERM to all processes once all containers has terminated,
that is not included in the exclude list.  The exclude list is simply the arguments
given to the Service itself.

This requires `shareProcessNamespace: true` on the Pod.

Example use

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: api-tests
spec:
  backoffLimit: 0
  template:
    metadata:
      name: api-tests
    spec:
      shareProcessNamespace: true
      activeDeadlineSeconds: 600
      restartPolicy: Never
      imagePullSecrets:
      - name: regcred
      containers:
      - name: k8s-job-sidecar
        image: morecontainers/k8s-job-sidecar:latest
        args:
          - k8s-job-sidecar
          - socat
      - name: socat
        image: morecontainers/socat:1.7.4.2-sigterm
        args:
          - -d
          - tcp-listen:8000,reuseaddr,fork,bind=127.0.0.1
          - tcp-connect:serving:8000
      - name: api-tests
        image: myreg.io/PATH/TO/YOUR/container:latest
```
