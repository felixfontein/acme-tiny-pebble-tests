#!/bin/bash
set -e

# Create account keys
echo "[$(date)] ================================================================"
curl ${ACME_CONTROLLER}/root-certificate-for-ca --output /output/root.pem

# Create account keys
echo "[$(date)] ================================================================"
echo "[$(date)] Create account keys"
openssl genrsa 2048 > /output/account-1.key

# Create private keys
echo "[$(date)] ================================================================"
echo "[$(date)] Create private keys"
openssl genrsa 2048 > /output/cert-1.key

# Create CSRs
echo "[$(date)] ================================================================"
echo "[$(date)] Create CSRs"
cat > /output/config-1 <<ENDOFCONFIG
[ req ]
distinguished_name = req_distinguished_name
req_extensions = req_ext
[ req_distinguished_name ]
commonName = example.com
[ req_ext ]
subjectAltName = @alt_names
[alt_names]
DNS.1   = example.com
ENDOFCONFIG
openssl req -new -sha256 -key /output/cert-1.key -out /output/cert-1.csr -subj '/CN=example.com' -config /output/config-1

# Tests

echo "[$(date)] ================================================================"
echo "[$(date)] Test 1: get certificate"
openssl req -in /output/cert-1.csr -noout -text
python acme_tiny_wrapper.py /output/ca-ca-root.pem \
    --account-key /output/account-1.key \
    --csr /output/cert-1.csr \
    --acme-dir /challenges \
    --directory-url ${ACME_DIRECTORY} \
    --contact mailto:me@example.com \
    > /output/cert-1-chain.pem

echo Validate certificate 1
openssl verify -CAfile /output/root.pem -untrusted /output/cert-1-chain.pem /output/cert-1-chain.pem
