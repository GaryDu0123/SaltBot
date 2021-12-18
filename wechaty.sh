#!/usr/bin/env bash

# 理论上在docker中运行这个就能跑起来
#docker pull wechaty/wechaty:0.65

export WECHATY_LOG="verbose"
# wechaty-puppet-wechat
export WECHATY_PUPPET="wechaty-puppet-wechat"
export WECHATY_PUPPET_SERVER_PORT="8080"
export WECHATY_TOKEN="python-wechaty-97b5ee4f-f9bb-44d2-af1e-919b7d122539"
export WECHATY_PUPPET_SERVICE_NO_TLS_INSECURE_SERVER="true"

# save login session
if [ ! -f "${WECHATY_TOKEN}.memory-card.json" ]; then
touch "${WECHATY_TOKEN}.memory-card.json"
fi

docker run -ti \
--name wechaty_puppet_service_token_gateway \
--rm \
-v "`pwd`/${WECHATY_TOKEN}.memory-card.json":"/wechaty/${WECHATY_TOKEN}.memory-card.json" \
-e WECHATY_LOG \
-e WECHATY_PUPPET \
-e WECHATY_PUPPET_SERVER_PORT \
-e WECHATY_PUPPET_SERVICE_NO_TLS_INSECURE_SERVER \
-e WECHATY_TOKEN \
-p "$WECHATY_PUPPET_SERVER_PORT:$WECHATY_PUPPET_SERVER_PORT" \
wechaty/wechaty:0.65