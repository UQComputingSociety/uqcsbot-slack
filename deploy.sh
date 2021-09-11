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
  -e SLACK_BOT_TOKEN=${DEPLOY_SLACK_BOT_TOKEN} \
  -e SLACK_USER_TOKEN=${DEPLOY_SLACK_USER_TOKEN} \
  -e SLACK_VERIFICATION_TOKEN=${DEPLOY_SLACK_VERIFICATION_TOKEN} \
  -e YOUTUBE_API_KEY=${DEPLOY_YOUTUBE_API_KEY} \
  -e WOLFRAM_APP_ID=${DEPLOY_WOLFRAM_APP_ID} \
  -e YOUTUBE_DETERMINISTIC_RESULTS=${DEPLOY_YOUTUBE_DETERMINISTIC_RESULTS} \
  -e GOOGLE_API_KEY=${DEPLOY_GOOGLE_API_KEY} \
  -e AOC_SESSION_ID=${DEPLOY_AOC_SESSION_ID} \
  -e AQI_API_TOKEN=${DEPLOY_AQI_API_TOKEN} \
  -e UQCSBOT_DB_URI=${DEPLOY_UQCSBOT_DB_URI} \
  ghcr.io/uqcomputingsociety/uqcsbot-slack:latest
for x in $OLDCONTAINERS; do
  docker rm -f ${x}
done
