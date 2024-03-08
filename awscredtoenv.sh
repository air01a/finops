#!/bin/bash
export AWS_ACCESS_KEY_ID=$(cat ../../.aws/credentials | grep "aws_access_key_id" | cut -d'=' -f2 | sed -e "s/ //")
export AWS_SECRET_ACCESS_KEY=$(cat ../../.aws/credentials | grep "aws_secret_access_key" | cut -d'=' -f2 | sed -e "s/ //")
