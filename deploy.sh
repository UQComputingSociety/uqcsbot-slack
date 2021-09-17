#!/bin/bash

mkdir docker-cert
echo "${DOCKER_CA}" > docker-cert/ca.pem
echo "${DOCKER_KEY}" > docker-cert/key.pem
echo "${DOCKER_CERT}" > docker-cert/cert.pem

export DOCKER_CERT_PATH="$(pwd)/docker-cert"
export DOCKER_TLS_VERIFY=1

docker pull ghcr.io/uqcomputingsociety/uqcsbot-slack:latest
OLDCONTAINERS="$(docker ps -f label=uqcsbot-slack-ci -a -q)"
docker run -d \
  --label uqcsbot-slack-ci \
  --restart always \
  -e SLACK_BOT_TOKEN=${SLACK_BOT_TOKEN} \
  -e SLACK_USER_TOKEN=${SLACK_USER_TOKEN} \
  -e SLACK_VERIFICATION_TOKEN=${SLACK_VERIFICATION_TOKEN} \
  -e YOUTUBE_API_KEY=${YOUTUBE_API_KEY} \
  -e WOLFRAM_APP_ID=${WOLFRAM_APP_ID} \
  -e YOUTUBE_DETERMINISTIC_RESULTS=${YOUTUBE_DETERMINISTIC_RESULTS} \
  -e GOOGLE_API_KEY=${GOOGLE_API_KEY} \
  -e AOC_SESSION_ID=${AOC_SESSION_ID} \
  -e AQI_API_TOKEN=${AQI_API_TOKEN} \
  -e UQCSBOT_DB_URI=${UQCSBOT_DB_URI} \
  ghcr.io/uqcomputingsociety/uqcsbot-slack:latest
for x in $OLDCONTAINERS; do
  docker rm -f ${x}
done
