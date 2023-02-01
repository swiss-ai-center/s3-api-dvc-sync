import os
import git
import shutil

from subprocess import run, PIPE

from dotenv import load_dotenv
load_dotenv()


def git_pull():
    git_folder = os.getenv("GIT_FOLDER")
    branch = os.getenv("GIT_BRANCH")

    # take the repo
    repo = git.Repo(git_folder)

    # pull the repo
    origin = repo.remote(name="origin")
    origin.pull(branch)


def git_commit_push():
    git_folder = os.getenv("GIT_FOLDER")
    dataset = os.getenv("DVC_DATASET")
    branch = os.getenv("GIT_BRANCH")

    # WARNING: only the .dvc will change in the git repo
    # it is very important to commit only the .dvc file otherwise all the 
    # other files from the repo will be deleted by the push
    
    # take the repo
    repo = git.Repo(git_folder)


    # add the file to the git index
    repo.git.add(f"{dataset}.dvc")

    # create a commit for a specific SINGLE file
    repo.git.commit(f"{dataset}.dvc", m=f"update {dataset}.dvc") 

    # push the single file commit to the remote
    origin = repo.remote(name="origin")
    origin.push(branch)

    # delete the dataset file
    # if os.path.exists(f"{git_folder}/{dataset}"):
       # os.unlink(f"{git_folder}/{dataset}")

def init_git_repo():


    print("## INIT | Project GIT")
    # clone the git repo
    git_folder = os.getenv("GIT_FOLDER")
    git_repo = os.getenv("GIT_REPO")
    git_branch = os.getenv("GIT_BRANCH")
    dataset = os.getenv("DVC_DATASET")
    git_pat_name = os.getenv("GIT_PAT_NAME")

    # delete the git folder if it exists
    if os.path.exists(git_folder):
        os.chmod(git_folder, 0o777)
        # remove "read-only" flag from the git folder and its content
        for root, dirs, files in os.walk(git_folder):
            for d in dirs:
                os.chmod(os.path.join(root, d), 0o777)
            for f in files:
                os.chmod(os.path.join(root, f), 0o777)
        shutil.rmtree(git_folder)

    print("## INIT | Clean GIT folder")

    git.Repo.clone_from(git_repo, git_folder, no_checkout=True)

    print("## INIT | Clone GIT repo")

    # checkout the branch
    repo = git.Repo(git_folder)
        
    repo.git.config("user.name", git_pat_name)
    repo.git.config("user.email", f"{ git_pat_name }@mlops.com")

    print("## INIT | GIT config")

    repo.git.checkout(git_branch, ".dvc")
    repo.git.checkout(git_branch, f"{dataset}.dvc")

    print("## INIT | DvC")
    
    # setup DvC

    dvc_remote_name = os.getenv("DVC_REMOTE_NAME")
    dvc_cloud_storage_provider = os.getenv("DVC_CLOUD_STORAGE_PROVIDER")
    dvc_bucket_name = os.getenv("DVC_BUCKET_NAME")

    print("## INIT | DvC Add Remote")

    run(
        f"dvc remote add -d {dvc_remote_name} {dvc_cloud_storage_provider}://{dvc_bucket_name}/dvcstore -f", 
        cwd=git_folder, 
        stdout=PIPE,
        shell=True
    )

    if dvc_cloud_storage_provider == "gs":
        print("## INIT | DvC Add Remote | GS")
        # setup DvC to use GCP as remote storage
        google_application_credentials = os.getenv("DVC_GOOGLE_APPLICATION_CREDENTIALS")
        gcp_service_account_key = os.getenv("DVC_GCP_SERVICE_ACCOUNT_KEY")

        with open(f"{git_folder}/{google_application_credentials}", "w") as f:
            f.write(gcp_service_account_key)
        # --local to avoid storing the credentials in the git repo
        run(
            f"dvc remote modify --local {dvc_remote_name} credentialpath {google_application_credentials}",
            cwd=git_folder,
            stdout=PIPE,
            shell=True
        )

    
    if dvc_cloud_storage_provider == "s3":
        print("## INIT | DvC Add Remote | S3")
        # setup DvC to use S3 as remote storage
        dvc_s3_endpoint = os.getenv("DVC_S3_ENDPOINT")

        dvc_s3_access_key_id = os.getenv("DVC_S3_ACCESS_KEY_ID")
        dvc_s3_secret_access_key = os.getenv("DVC_S3_SECRET_ACCESS_KEY")

        run(
            f"dvc remote modify {dvc_remote_name} endpointurl {dvc_s3_endpoint}",
            cwd=git_folder,
            stdout=PIPE,
            shell=True
        )

        # --local to avoid storing the credentials in the git repo
        run(
            f"dvc remote modify --local {dvc_remote_name} access_key_id {dvc_s3_access_key_id}",
            cwd=git_folder,
            stdout=PIPE,
            shell=True
        )

        run(
            f"dvc remote modify --local {dvc_remote_name} secret_access_key {dvc_s3_secret_access_key}",
            cwd=git_folder,
            stdout=PIPE,
            shell=True
        )

    print ("## INIT | Done")

    # repo.git.dvc("remote", "modify", "--local", "data", "credentialpath", f"{git_folder}/${env.GOOGLE_APPLICATION_CREDENTIALS}")

   