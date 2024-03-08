#!/bin/bash
export AWS_ACCESS_KEY_ID=$(awk -F "[[:space:]]*=[[:space:]]*" '/aws_access_key_id/{print $2}' $HOME/.aws/credentials)
export AWS_SECRET_ACCESS_KEY=$(awk -F "[[:space:]]*=[[:space:]]*" '/aws_secret_access_key/{print $2}' $HOME/.aws/credentials)
