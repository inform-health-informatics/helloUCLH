docker build -t hellouclh -f config/helloUCLH.Dockerfile .
docker run --privileged -ti -v ${PWD}:/usr/local/bin/helloUCLH -p 8889:8888 hellouclh