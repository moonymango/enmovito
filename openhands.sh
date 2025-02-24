docker run -it --rm --pull=always \
    -e SANDBOX_RUNTIME_CONTAINER_IMAGE=docker.all-hands.dev/all-hands-ai/runtime:0.25-nikolaik \
    -e LOG_ALL_EVENTS=true \
    -e SANDBOX_LOCAL_RUNTIME_URL=http://localhost \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v ~/.openhands-state:/.openhands-state \
    -p 3000:3000 \
    --network="host" \
    --name openhands-app \
    docker.all-hands.dev/all-hands-ai/openhands:0.25
    