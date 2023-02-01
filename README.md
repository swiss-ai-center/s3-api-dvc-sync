# DVC Sync S3 API

The data stored in the labeling tools (such as Label Studio) is not directly availabe in the data science pipeline.

It requires collaboration between the labeling team and the data science team to share the data.

The purpose of this project is to provide a minimal S3 API to breach the gap between Data Versioning Control (DVC) and annotation tools. The principle is to set this API as S3 Cloud Storage in the labeling tools and it will push the annotations to DVC. The data science team can then use the fresh data in the ML OPS pipeline.

It has been tested with Label Studio. Label Studio configuration allows to setup a Cloud Storage to store the annotations. The Cloud Storage can be configured to use an S3 API with a custom endpoint.

### Working principles
- Behaves like an S3 API by implementing a minimal subset of the S3 commands
- Stores the objects in a local folder
- Works with the same GIT repository as the data science team - a separate branch can be configured 
- Clone the project repository with sparse checkout to include only the necessary meta files
- API behaves like a team member that updates the dataset file and pushes the changes to DVC and Git.  

### Limitations
- The API is not a full S3 API. It only implements the commands that are required by Label Studio Sync functionality.
- The API is single tenant. It works for on a single project. It is possible to run multiple instances of the API for multiple projects. 


## Configuration

The configuration is done in the .env file. You can base your configuration on the .env.example file.

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


