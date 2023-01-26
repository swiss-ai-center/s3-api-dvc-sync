import os


from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from aws import aws_put_object_stream_to_file, aws_list_object_v2_response
from aws_v4_signature import get_aws_v4_signature, get_aws_signature_arguments
from git_utils import git_pull, git_commit_push, init_git_repo
from dvc import dvc_update_dataset_file, dvc_commit_push

from threading import Thread

from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

# create a map to store the bundle countdown for each bucket
bundle_countdown = int(os.getenv("BUNDLE_COUNTDOWN"))
git_folder = os.getenv("GIT_FOLDER")

init_git_repo()

# a sync coroutine that will be called asynchronously
def sync_eventually(physical_data_path):
    global bundle_countdown
    if bundle_countdown == 0:
        print("## Bundle Countdown Reached | Syncing...")
        # set the bundle countdown to the configured value
        bundle_countdown = int(os.getenv("BUNDLE_COUNTDOWN"))
        # git pull the repo
        git_pull()
        # update the dataset file
        dvc_update_dataset_file(physical_data_path)
        # commit and push the changes with dvc
        dvc_push_response = dvc_commit_push()
        # check if dvc_push_response contains "Everything is up to date."
        # if it does, then there is no need to commit and push the changes with git
        if not "Everything is up to date." in dvc_push_response:
            # commit and push the changes with git
            git_commit_push()
            print("## Sync Done | Changes Committed and Pushed ")
        else:
            print("## No Changes | Skipping Git Commit and Push...")
    # decrement the bundle countdown
    bundle_countdown -= 1

def signature_ok(req: Request):
    authorization = req.headers['Authorization']
    request_signature = authorization.split(",")[2].split("=")[1]    
    aws_access_key_id = authorization.split(",")[0].split("=")[1].split("/")[0]
    if aws_access_key_id != os.getenv("AWS_ACCESS_KEY_ID"): # implemented but not used in single tenant mode
        return False
    aws_secret_access_key, canonical_request, datestamp, aws_region, service, amzdate = get_aws_signature_arguments(req)
    reversed_signature = get_aws_v4_signature(aws_secret_access_key, canonical_request, datestamp, aws_region, service, amzdate)
    return request_signature == reversed_signature

# handle all GET, HEAD and PUT requests
@app.middleware("http")
async def handle_request(req: Request, call_next):
    url = req.url.path
    method = req.method
    query_string = req.url.query
    # check if the request is a GET, HEAD or PUT request
    if method == "GET" or method == "HEAD" or method == "PUT":
        if not signature_ok(req):
            return JSONResponse(status_code=403, content={"message": "Forbidden"})
        
        if method == 'GET': 
            if query_string.startswith("list-type=2"):
                xml = aws_list_object_v2_response(req, query_string)
                return JSONResponse(status_code=200, content=xml, content_type="application/xml")
            
        elif method == 'HEAD':
            return Response(status_code=200)
        
        elif method == 'PUT':
             # save the data from the request to a file
            physical_data_path, _ = await aws_put_object_stream_to_file(req)

            # create a thread to handle the sync without blocking the response 
            thread = Thread(target=sync_eventually, args=(physical_data_path,))
            thread.start()
                    
            # send FastAPI response status 200
            return Response(status_code=200)
            
    return JSONResponse({"message": "Not Implemented"}, status_code=501)