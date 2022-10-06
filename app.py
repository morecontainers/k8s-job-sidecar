import platform
import sys
from os import system, environ
from signal import signal, SIGTERM
from time import sleep

import requests


def monitor(namespace_name, pod_name, excluded_container_names):
    kubernetes_service_host = environ.get("KUBERNETES_SERVICE_HOST", "localhost")
    kubernetes_service_port = environ.get("KUBERNETES_SERVICE_PORT", "8001")
    with open('/run/secrets/kubernetes.io/serviceaccount/token') as f:
        token = f.read().strip()
    path = f"/api/v1/namespaces/{namespace_name}/pods/{pod_name}"
    endpoint = f"https://{kubernetes_service_host}:{kubernetes_service_port}{path}"
    headers = {"Authorization": f"Bearer {token}"}
    while True:
        sleep(3)
        response = requests.get(endpoint, verify="/run/secrets/kubernetes.io/serviceaccount/ca.crt", headers=headers)
        response.raise_for_status()
        pod = response.json()
        status = pod.get("status", {})
        container_statuses = status.get("containerStatuses", [])
        #print(json.dumps(pod, indent=2))
        all_terminated = True
        for container in container_statuses:
            if container.get("name") not in excluded_container_names:
#               print(f'{container.get("name"):20s}', end='')
                for state in container.get("state", {}).keys():
                    if state == "terminated":
#                       print('terminated')
                        break
                else:
#                   print('running')
                    all_terminated = False
        if all_terminated:
            break


if __name__ == '__main__':
    namespace_name = environ.get("NAMESPACE_NAME")
    if namespace_name is None:
        try:
            with open('/run/secrets/kubernetes.io/serviceaccount/namespace') as f:
                namespace_name = f.read().strip()
        except:
            namespace_name = "default"

    pod_name = environ.get("POD_NAME", platform.node())

    excluded_container_names = sys.argv[1:]

    print(f"NAMESPACE_NAME={namespace_name}")
    print(f"POD_NAME={pod_name}")
    print(f"EXCLUDED_CONTAINER_NAMES={' '.join(excluded_container_names)}")

    def dummy_handler(_signum, _frame):
        pass

    signal(SIGTERM, dummy_handler)

    monitor(namespace_name, pod_name, excluded_container_names)

    print("Signalling all processes to terminate")
    system("kill -15 -1")
    sys.exit(0)
