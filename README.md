# DVC Sync S3 API

## Bridging the Gap between Annotation Tools and Data Science Pipelines

Data stored in labeling tools, such as Label Studio, is not directly accessible in the data science pipeline. This project aims to address this issue by providing a minimal S3 API that can serve as a bridge between the annotation tools and Data Versioning Control (DVC).

The API will be integrated with labeling tools, such as Label Studio, as a cloud storage for annotations. This will allow annotations to be automatically pushed to DVC, making them easily accessible to the data science team in their machine learning operations pipeline.

### Working principles
- Implements a minimal subset of S3 commands to behave like an S3 API
- Stores the objects in a local folder
- Works with the same Git repository as the data science team, with the option to configure a separate branch
- Project repository is cloned with sparse checkout to include only necessary meta files
- Behaves like a team member, updating the dataset file and pushing changes to both DVC and Git

### Limitations
- The API is not a complete S3 implementation, only providing the necessary commands for Label Studio Sync functionality
- Currently designed for single-tenant use, only working with one project at a time. However, multiple instances of the API can be run for multiple projects.

This project has been tested with Label Studio and its configuration allows for the setup of a cloud storage solution to store annotations. The cloud storage can be configured to use this S3 API with a custom endpoint.


## Configuration

The configuration is done in the .env file. You can base your configuration on the .env.example file.

### Sync S3 Access key
These are the credentials that will be used by label studio (using Boto3) to access the S3 API abstraction of dvc. The credentials are used to authenticate the user and to authorize the user to perform specific actions on the S3 API.

You can define whatever Key ID and Secret you want. The only requirement is that the Key ID and Secret are the same as the ones defined in the Label Studio configuration.

```shell
AWS_ACCESS_KEY_ID="test-id" 
AWS_SECRET_ACCESS_KEY="test-secret"
```

### Git configuration
First we need to specify the local path where the git repository will be cloned. This is the path where the project repository will be cloned.

```shell
GIT_FOLDER="./storage/git"
S3_DATA_FOLDER="./storage/s3/objects"
```

Then we need a personal access token (PAT) to access the project repository.

```shell
GIT_PAT_NAME="dvc-sync"
GIT_PAT_TOKEN="glpat-xxx"
```

Finally, we need to specify the project repository URL and the branch to use.

```shell
GIT_REPO="https://dvc-xxx:glpat-xxx@git-ext.iict.ch//stefan.teofanov/mlops_example_git_test.git"
GIT_BRANCH="main"
```

### DVC configuration
configure DvC dataset, should correspond to the dataset location in the git repo

```shell
DVC_DATASET="data/data.json"
```
Setup DvC Clound Storage Provider, currently supported: "gs" (Google Cloud Platform) and "s3" (Amazon Web Services)

```shell
DVC_CLOUD_STORAGE_PROVIDER="s3" 
```

Setup DvC Remote Name

```shell
DVC_REMOTE_NAME="data"
```

Setup the name of your bucket in the cloud storage provider

```shell
DVC_BUCKET_NAME="s3-label-studio-sync"
```

### Google App Credentials
If you are using Google Cloud Platform (GCP) as your cloud storage provider, you need to setup the credentials for DvC to access your bucket.



DVC requires a variable called GOOGLE_APPLICATION_CREDENTIALS that contain the path to the service account key file.
```shell
DVC_GOOGLE_APPLICATION_CREDENTIALS="google-service-account-key.json"
```

GCP_SERVICE_ACCOUNT_KEY is a variable that contains the service account key in JSON format.

```shell
DVC_GCP_SERVICE_ACCOUNT_KEY={"type": "service_account", "project_id": "mlopsdemo-xxx","private_key_id": "xxxx","private_key": "-----BEGIN PRIVATE KEY----------END PRIVATE KEY-----\n","client_email": "mlopsdemo@mlopsdemo-366216.iam.gserviceaccount.com", "client_id": "xxxx","auth_uri": "https://accounts.google.com/o/oauth2/auth", "token_uri": "https://oauth2.googleapis.com/token","auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs","client_x509_cert_url": "xxxx"}
```

### AWS Credentials

If you are using Amazon Web Services (AWS) as your cloud storage provider, you need to setup the credentials for DvC to access your bucket.

```shell
DVC_S3_ENDPOINT = 'https://xyxxx:yyyy'
DVC_S3_ACCESS_KEY_ID = 'xxx'
DVC_S3_SECRET_ACCESS_KEY = 'xxx'
```

# Run in development mode

## Setup the virtual environment

### Create a virtual environment
```bash

# create a virtual environment
python3 -m venv .venv
```

### Activate the virtual environment

#### Windows

```bash
.venv\Scripts\activate.bat
```
#### Linux

```bash
source .venv/bin/activate
```

### Install the requirements

```bash
pip install -r requirements.txt
```

## Run the application

```bash
uvicorn main:app --reload --port 8000
```

# Run using docker compose

## Build the docker image

```bash
docker compose up
```


