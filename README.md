
# Serverless and AI

## Description
This is a simple project developed with Python and AWS CDK showing how to create our first project using AWS serverless services (e.g. AWS Lambda) together with AI service Amazon Bedrock. It was used for the demo session on 12th of June 2024 during AWS User Group Meetup in Warsaw, Poland on the session called "Serverless and AI - Can this be the new technological love story?".

## Prerequisite
 * Docker
 * AWS CDK CLI
 * AWS CLI
 * node.js
 * Python 3.12
 * Poetry

## Quick start
1. Clone the repo
   ```sh
   git clone git@github.com:amswiatkowski/serverless-and-ai.git
   ```
2. Install dependencies
    ```sh
    poetry install
    ```
3. Deploy the project
   ```sh
   ./deploy.sh
4. Run frontend locally to be able to have a conversation with chatbot
   ```sh
   ./run_webapp.sh
   ```   ```


## Useful commands
 * `./lint.sh`          Fixes indents and checks your code quality
 * `./destroy.sh --region us-east-1`       Triggers cdk destroy
 * `./deploy.sh --region us-east-1`        Deploys stack to the AWS account
 * `./run_webapp.sh`        Runs frontend locally
 * `pytest -vv ./tests` Run tests

## Useful links
* [AWS CDK](https://docs.aws.amazon.com/cdk/v2/guide/cli.html)

## Author
**Adam Świątkowski**
* [github/amswiatkowski](https://github.com/amswiatkowski)
* [Blog](https://cloudybarz.com/)

### License
Copyright © 2024, [Adam Świątkowski](https://github.com/sz3jdii).
Released under the [MIT License](LICENSE).

