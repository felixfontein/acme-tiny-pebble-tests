#!/bin/bash
docker pull golang:1.13-stretch
docker pull python:3.6-slim-stretch
PEBBLE_CHECKOUT=746c32eb265131059a2a340388a4bc7c37405cfc
docker image build --network host --build-arg PEBBLE_CHECKOUT=${PEBBLE_CHECKOUT} -t felixfontein/acme-tiny-pebble-test-container:${PEBBLE_CHECKOUT} docker-container
docker push felixfontein/acme-tiny-pebble-test-container:${PEBBLE_CHECKOUT}
