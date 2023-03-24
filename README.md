# DVC Sync S3 API

## Bridging the Gap between Annotation Tools and Data Science Pipelines

Data stored in labeling tools, such as Label Studio, is not directly accessible in the data science pipeline. This project aims to address this issue by providing a minimal S3 API that can serve as a bridge between the annotation tools and Data Versioning Control (DVC).

The API will be integrated with labeling tools, such as Label Studio, as a cloud storage for annotations. This will allow annotations to be automatically pushed to DVC, making them easily accessible to the data science team in their machine learning operations pipeline.

<div class="center">
<h3>
  <center> 
    Inital state of the project repository
  </center> 
</h3>
<center>

```mermaid
sequenceDiagram
    participant DataAnnotators
    participant LabelStudio
    participant DVCSyncS3API
    participant DVC
    participant DataScienceTeam
    DataAnnotators->>+LabelStudio: Annotate Label Studio Tasks
    LabelStudio->>-LabelStudio: Stores annotations in local storage
    LabelStudio->>+DVCSyncS3API: Sync out annotations
    Note right of DVCSyncS3API: DVCSyncS3API serves as a bridge
    DVCSyncS3API-->>-LabelStudio: Successful storage
    DVCSyncS3API->>+DVC: Sync
    DVC-->>-CloudStorage for DvC: Successful push
    Note right of DVC: Annotations are now<br/> accessible to the data science team
    DataScienceTeam->>+DVC: Pull dataset
```
  </center> 
</div>

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

<div class="center">
<h3>
  <center> 
    Inital state of the project repository
  </center> 
</h3>
<center>

```mermaid
graph TD

A[Git with ML Codebase]
B[DVC] -- tracks--> C[Dataset]
D[tasks] -- in--> C
E[annotations] -- in--> C
B -- stores metadata--> A
B -- stores data --> F[Cloud storage S3]
```
  </center> 
</div>

## Configuration

The configuration is done in the .env file. You can base your configuration on the .env.example file.

### Sync S3 Access key
These are the credentials that will be used by label studio (using Boto3) to access the S3 API abstraction of dvc. 

You can define whatever Key ID and Secret you want. The only requirement is that the Key ID and Secret are the same as the ones defined in the Label Studio project cloud storage configuration.  

```shell
AWS_ACCESS_KEY_ID="my-super-id" 
AWS_SECRET_ACCESS_KEY="my-super-secret"
```

You now need to chose the location of the local path where the S3 objects will be stored. This will store the annotations with their reference to the corresponding task (data). 

```shell
S3_DATA_FOLDER="./storage/s3/objects"
```

### Git configuration

First, we need to specify the project repository URL and the branch to use. This repository is the way DVC will store it's metadata files to track changes on the dataset. It needs to be a DVC initialized repository. This includes the data already being tracked by DVC. 

> Note we put a Personal Access Token (PAT) in the URL. This is because the repository is private and we need to authenticate to clone it.

```shell
GIT_REPO="https://dvc-xxx:glpat-xxx@git-ext.iict.ch//stefan.teofanov/mlops_example_git_test.git"
GIT_BRANCH="main"
```

Then we need to specify the local path where the git repository will be cloned. This is the path where the project repository will be cloned.

```shell
GIT_FOLDER="./storage/git"
```

Then we need a personal access token (PAT) push to the project repository. This is the same PAT you used in the repo url.

```shell
GIT_PAT_NAME="dvc-sync"
GIT_PAT_TOKEN="glpat-xxx"
```

### DVC configuration
Configure DvC dataset, should correspond to the dataset location in the git repo. This data file will be gitignored and managed by DVC. A metadata file named data.json.dvc will be created in the git repo to track changes.

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


