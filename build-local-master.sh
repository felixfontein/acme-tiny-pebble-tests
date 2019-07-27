#!/bin/bash
# docker pull golang:1.10-stretch
# docker pull python:3.6-slim-stretch
docker image build --network host --build-arg PEBBLE_CHECKOUT=master -t local/acme-tiny-pebble-test-container:latest docker-container
