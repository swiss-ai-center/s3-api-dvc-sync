import json
import os
from subprocess import run, PIPE, STDOUT 

from dotenv import load_dotenv
load_dotenv()

def transform_label_studio_annotation_to_task(annotation):
    label_studio_task = annotation["task"]
    del annotation["task"]
    label_studio_task["annotations"] = []
    label_studio_task["annotations"].append(annotation)
    return label_studio_task


def dvc_update_dataset_file(s3_data_physical_path):
    git_folder = os.getenv("GIT_FOLDER")
    dataset = os.getenv("DVC_DATASET")
    # create an empty dataset file
    open(f"{git_folder}/{dataset}", "w").close()

    # open a write stream to the file
    with open(f"{git_folder}/{dataset}", "w") as w_stream:
        # write the opening "[" character to the write stream
        w_stream.write("[")

        # loop and read the contents of all files in s3_data_physical_path
        for _, file in enumerate(os.listdir(s3_data_physical_path)):
            file_path = f"{s3_data_physical_path}/{file}"
            with open(file_path, "r") as f:
                # read the file contents
                file_content = f.read()

                # transform label studio annotation to an importable task
                ls_task = transform_label_studio_annotation_to_task(json.loads(file_content))

                # write the transformed data to the write stream
                w_stream.write(json.dumps(ls_task))

                # write a comma separator if not the last file
                w_stream.write(",")

        # delete the last comma separator
        w_stream.seek(w_stream.tell() - 1, os.SEEK_SET)
        # write the closing "]" character to the write stream
        w_stream.write("]")



def dvc_commit_push():
    git_folder = os.getenv("GIT_FOLDER")
    dataset = os.getenv("DVC_DATASET")
    # commit the changes to dvc repo
    dvc_commit = run(
        ["dvc", "commit", f"{dataset}.dvc", "-f"],
        cwd=git_folder,
        stdout=PIPE
    )

    # push the changes to dvc remote
    out = run(
        ["dvc", "push"],
        cwd=git_folder,
        stdout=PIPE,
        stderr=STDOUT
    )

    if out.returncode != 0:
        print("## Sync failed | ", out.stdout.decode())
   
    return out.stdout.decode()
