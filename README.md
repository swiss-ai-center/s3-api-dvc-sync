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


