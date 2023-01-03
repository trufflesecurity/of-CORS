#!/bin/sh
heroku login && CONFIG_FILE=/config.yml make deploy_and_configure
/bin/sh
