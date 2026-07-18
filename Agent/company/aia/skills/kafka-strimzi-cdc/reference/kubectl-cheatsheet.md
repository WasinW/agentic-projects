# kubectl cheat-sheet for a Strimzi/Kafka/Debezium DE (AIA)

> Read-only inspection first (ask for read access before write). `NS=<namespace>` e.g. `651563-kbdev-cluster`. Nothing here exports AIA code — it inspects live cluster state.

## Orient — where am I, what's here
```bash
kubectl config get-contexts                 # clusters you can reach
kubectl config current-context
kubectl get ns                              # namespaces
kubectl get crds | grep strimzi             # Strimzi CRDs installed (proves operator + which kinds)
kubectl api-resources | grep strimzi        # short names: kafka, kt (topic), ku (user), kc, kctr
kubectl get all -n $NS                       # everything in the namespace (pods/deploy/sts/svc)
```

## The Strimzi custom resources
```bash
kubectl get kafka -n $NS                     # broker clusters (READY?)
kubectl get kafkaconnect -n $NS              # Connect runtimes
kubectl get kafkaconnector -n $NS            # Debezium connectors (READY / TASKS)
kubectl get kafkatopic -n $NS                # topics (kt)
kubectl get kafkauser -n $NS                 # users (ku)
kubectl get kafkabridge,kafkamirrormaker2 -n $NS 2>/dev/null
# desired-vs-actual + events + last error:
kubectl describe kafka <name> -n $NS
kubectl describe kafkaconnector <name> -n $NS
# read a live spec (adapt patterns from it — read only):
kubectl get kafkaconnector <name> -n $NS -o yaml
```

## Pods / workloads
```bash
kubectl get pods -n $NS -o wide              # brokers, zk, connect workers, operators
kubectl get statefulset -n $NS               # Kafka brokers (+ zk) live here
kubectl get deployment -n $NS                # operators + Connect workers + entity-operator
kubectl get pvc -n $NS                       # broker storage (Azure Disk)
kubectl get secret -n $NS | grep -Ei 'kafka|user'   # credentials the User Operator generated
```

## Logs / debugging
```bash
# operator (reconcile errors for ANY CR):
kubectl logs deploy/strimzi-cluster-operator -n $NS --tail=300 -f
# entity operator (topic + user sync issues):
kubectl logs deploy/<cluster>-entity-operator -c topic-operator -n $NS
kubectl logs deploy/<cluster>-entity-operator -c user-operator  -n $NS
# a Connect worker (see Debezium plugin load + connector state):
kubectl logs <connect-pod> -n $NS | grep -iE 'debezium|snapshot|ERROR'
kubectl logs <connect-pod> -n $NS -f
# a broker:
kubectl logs <cluster>-kafka-0 -n $NS --tail=200
# events (why is a pod not starting):
kubectl get events -n $NS --sort-by=.lastTimestamp | tail -30
```

## Connector state via the Connect REST API (from inside a Connect pod)
```bash
kubectl exec -it <connect-pod> -n $NS -- bash
# then, against localhost:8083:
curl -s localhost:8083/connectors | jq                    # list connectors
curl -s localhost:8083/connectors/<name>/status | jq      # state + per-task state + traces
curl -s localhost:8083/connectors/<name>/config | jq
curl -s localhost:8083/connector-plugins | jq             # plugins baked into the image (Debezium?)
# restart a failed task (operational fix):
curl -s -X POST localhost:8083/connectors/<name>/restart?includeTasks=true
```

## Peek at topics / consume (from inside a broker pod)
```bash
kubectl exec -it <cluster>-kafka-0 -n $NS -- bash
bin/kafka-topics.sh --bootstrap-server localhost:9092 --list
bin/kafka-topics.sh --bootstrap-server localhost:9092 --describe --topic <topic>
bin/kafka-consumer-groups.sh --bootstrap-server localhost:9092 --describe --group <group>   # lag!
bin/kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic <topic> --max-messages 5
```
> Auth note: real listeners use TLS/SCRAM — you'll need the `--command-config` / properties file with the `KafkaUser` credentials (from the Secret). Confirm the platform's exact bootstrap + auth.

## Apply / change (WRITE — only when authorized, via the repo+Jenkins normally)
```bash
kubectl apply -f <cr>.yaml -n $NS            # normally Jenkins does this, not you by hand
kubectl annotate kafkaconnector <name> strimzi.io/restart="true" -n $NS   # ask operator to restart it
kubectl annotate kafkaconnector <name> strimzi.io/restart-task="0" -n $NS # restart one task
kubectl rollout restart statefulset/<cluster>-kafka -n $NS               # rolling broker restart (careful!)
```

## Safe habits
- **Inspect before act:** `get` → `describe` → logs. Change via **repo + Jenkins**, not ad-hoc `kubectl apply`, unless firefighting.
- **Namespace every command** (`-n $NS`) — prod and non-prod may be different namespaces/clusters.
- **`describe` shows the reconcile story** — desired spec, actual status, and the operator's last error, all in one place.
- Prefer the **operator restart annotation** over deleting pods — it respects Strimzi's safe-rolling logic (leadership migration, drain-cleaner).
