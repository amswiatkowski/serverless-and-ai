#!/bin/bash
while test $# -gt 0; do
    case "$1" in
    --region)
        shift
        export REGION=$1
        shift
        ;;
    --deploy_env)
        shift
        export DEPLOY_ENV=$2
        shift
        ;;
    *)
        echo "$1 is not a recognized flag!"
        return 1
        ;;
    esac
done
if [ -z "$REGION" ]; then
    REGION="eu-central-1"
fi
if [ -z "$DEPLOY_ENV" ]; then
    DEPLOY_ENV="dev"
fi
echo "Region: $REGION"
echo "Environment: $DEPLOY_ENV"
rm -rf .build
mkdir -p .build/lambdas ; cp -r lambda_handlers .build/lambdas
mkdir -p .build/common_layer ; poetry export --without=dev --without-hashes --format=requirements.txt > .build/common_layer/requirements.txt
REGION=$REGION AWS_REGION=$REGION AWS_DEFAULT_REGION=$REGION DEPLOY_ENV=$DEPLOY_ENV cdk deploy --all --verbose --region $REGION --require-approval never
