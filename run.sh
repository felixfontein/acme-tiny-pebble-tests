#!/bin/bash
set -e

POSTFIX="$(date +'%Y%m%d-%H%M%S')-$(dd if=/dev/urandom bs=1 count=8 2> /dev/null | od -A n -v -t x1 | tr -d ' \n')"

clean() {
  set +e
  docker rm -f ${CONTAINER_NAME} ${CONTAINER_NAME_2}
  rm -rf ${OUTPUT_DIR}
}

# Determine names and set up cleanup
CONTAINER_NAME="acme-certificate-test-controller-${POSTFIX}"
CONTAINER_NAME_2="acme-certificate-test-acme_tiny-${POSTFIX}"
export OUTPUT_DIR="output-${POSTFIX}"
trap "{ docker logs ${CONTAINER_NAME} ; clean ; }" EXIT

# Prepare tests
mkdir ${OUTPUT_DIR}
mkdir ${OUTPUT_DIR}/challenge-files/
ACME_OUTPUT_DIR=$(cd "${OUTPUT_DIR}"; pwd)
ACME_CHALLENGE_DIR=$(cd "${OUTPUT_DIR}/challenge-files/"; pwd)

# Start container
docker run --detach --name ${CONTAINER_NAME} \
    --mount type=bind,src=${ACME_CHALLENGE_DIR},dst=/challenges \
    --publish-all=true \
    local/acme-tiny-pebble-test-container:latest
TEST_CONTAINER_IP=$(docker inspect -f "{{.NetworkSettings.IPAddress}}" ${CONTAINER_NAME})
echo "Container IP: ${TEST_CONTAINER_IP}"

sleep 1

# Run tests
docker run --name ${CONTAINER_NAME_2} -it \
    --mount type=bind,src=${ACME_OUTPUT_DIR},dst=/output \
    --mount type=bind,src=${ACME_CHALLENGE_DIR},dst=/challenges \
    --mount type=bind,src=$(pwd)/acme_tiny.py,dst=/acme_tiny.py \
    --mount type=bind,src=$(pwd)/acme_tiny_wrapper.py,dst=/acme_tiny_wrapper.py \
    --mount type=bind,src=$(pwd)/run-tests.sh,dst=/run-tests.sh \
    --dns=${TEST_CONTAINER_IP} \
    -e ACME_DIRECTORY=https://${TEST_CONTAINER_IP}:14000/dir \
    -e ACME_CONTROLLER=http://${TEST_CONTAINER_IP}:80 \
    python:3 /bin/bash /run-tests.sh

# Cleanup
clean
trap - EXIT
