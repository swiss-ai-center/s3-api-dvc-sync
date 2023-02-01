# s3-api-dvc-sync





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

# Must reload if you cange the .env file


