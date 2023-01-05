# PySimpleGUI_test

```sh
pip3 install pysimplegui pexpect
```

```sh
docker image build -t caret/caret_ssh --build-arg CARET_VERSION="v0.3.3" ./docker

docker run -it --rm \
    --user $(id -u):$(id -g) \
    -p 22:22 \
    -v /etc/localtime:/etc/localtime:ro caret/caret_ssh

ssh autoware@127.0.0.1
```


