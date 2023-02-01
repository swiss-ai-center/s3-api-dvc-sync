import os

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response, PlainTextResponse
from urllib.parse import parse_qs

from utils.aws import aws_put_object_stream_to_file, aws_list_object_response, aws_get_object_response
from utils.aws_v4_signature import get_aws_v4_signature, get_aws_signature_arguments
from utils.git import git_pull, git_commit_push, init_git_repo
from utils.dvc import dvc_update_dataset_file, dvc_commit_push
from utils.debounce import debounce

from threading import Thread



from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

# create a map to store the bundle countdown for each bucket
bundle_countdown = int(os.getenv("BUNDLE_COUNTDOWN"))
git_folder = os.getenv("GIT_FOLDER")

init_git_repo()

# we must insire that only one sync is running at a time
# we do not use mutex because we want to skip the sync request if a previous sync is already running
sync_lock = False 

@debounce(10) # debounce the sync function for 10 seconds
def do_one_sync(physical_data_path):
    # run the sync in a separate thread
    Thread(target=sync_eventually, args=(physical_data_path,)).start()

# a sync coroutine running in a separate thread
def sync_eventually(physical_data_path):
    global sync_lock
    if sync_lock:
        print("## Sync Already Running | Skipping...")
        return
    sync_lock = True
    print("## Syncing...")
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
        print("## Sync Done | Changes Committed and Pushed : ", dvc_push_response)
    else:
        print("## No Changes | Skipping Git Commit and Push...")
    sync_lock = False
    

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
async def handle_request(req: Request, _):
    
    method = req.method

    if not signature_ok(req):
        return JSONResponse(status_code=403, content={"message": "Forbidden"})

    if method == 'GET': 
        
        path = req.url.path.split("/")
        params = parse_qs(req.url.query)
        bucket = None

        if len(path) > 1:
            bucket = path[1]

        if bucket is None:
            return JSONResponse({"message": "Not Implemented"}, status_code=501)
        
        if len(path) > 2:
            # GetObject - if the path is not empty, then we are requesting a file
            key = "/".join(path[2:])
            content = aws_get_object_response(bucket, key)
            return Response(status_code=200, content=content, headers={"Content-Type": "application/octet-stream"})
        
        elif len(path) == 2:
            # ListObjects - if the path is empty, then we are requesting a list of files
            xml = aws_list_object_response(bucket, params)
            return PlainTextResponse(status_code=200, content=xml, headers={"Content-Type": "application/xml"})

        else:   
            return JSONResponse({"message": "Not Implemented"}, status_code=501)
    
    elif method == 'HEAD':
        return Response(status_code=200)
    
    elif method == 'PUT':
        global bundle_countdown
        # save the data from the request to a file
        physical_data_path, _ = await aws_put_object_stream_to_file(req)

        if bundle_countdown == 0:
            bundle_countdown = int(os.getenv("BUNDLE_COUNTDOWN"))
            do_one_sync(physical_data_path)

        # decrement the bundle countdown
        bundle_countdown -= 1
                
        # send FastAPI response status 200
        return Response(status_code=200)
            
    return JSONResponse({"message": "Not Implemented"}, status_code=501)