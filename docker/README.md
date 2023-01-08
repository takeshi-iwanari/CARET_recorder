# Docker image to test CARET via SSH

```sh
docker image build -t caret/caret_ssh --build-arg CARET_VERSION="v0.4.1" ./docker

docker run -it --rm \
    --user $(id -u):$(id -g) \
    -p 22:22 \
    -v /etc/localtime:/etc/localtime:ro caret/caret_ssh

ssh autoware@127.0.0.1
```
