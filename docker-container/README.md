# acme-test-container

ACME CA test container for testing. Uses [Pebble](https://github.com/letsencrypt/Pebble).

## Usage

Building the image locally
```
docker image build -t local/acme-tiny-pebble-test-container:latest .
```

Building the image locally with a different version of Pebble checked out
```
docker image build --build-arg PEBBLE_CHECKOUT=<hash|branch|tag> -t local/acme-tiny-pebble-test-container:<hash|branch|tag> .
```

## License and Copyright

The controller, Dockerfile and all other files are licensed under the GPL v3 (or later).
You can find the license in [LICENSE](LICENSE).
