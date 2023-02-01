import os

from urllib.parse import urlparse, parse_qs
from xml.etree import ElementTree
import datetime 
import hashlib
import math

from dotenv import load_dotenv
load_dotenv()

data_folder = os.getenv("S3_DATA_FOLDER")

def physical_path(relative):
    return f"{data_folder}/{relative}"


def create_folder_if_not_exist(relative):
    p_path = physical_path(relative)
    if not os.path.exists(p_path):
        os.makedirs(p_path, exist_ok=True)
    return p_path


def aws_get_object_response(bucket, key):
    # Read the file from the /data directory
    ppath = physical_path(f"{bucket}/{key}")
    with open(ppath, "rb") as file:
        file_content = file.read()

    # Return the file content
    return file_content

def aws_list_object_response(bucket, params):
    # Parse the URL to extract the bucket and search parameters
    # Get the prefix and max-keys search parameters
    
    prefix = ""
    if "prefix" in params:
        prefix = params.get("prefix")[0]
    
    max_keys = "1000"
    if "max-keys" in params:
        max_keys = params.get("max-keys")[0]

    # Read files from the /data directory
    physical_path = create_folder_if_not_exist(f"{bucket}/{prefix}")
    files = os.listdir(physical_path)

    # Create the XML response
    root = ElementTree.Element("ListBucketResult", {"xmlns": "http://s3.amazonaws.com/doc/2006-03-01/"})
    ElementTree.SubElement(root, "Name").text = bucket
    ElementTree.SubElement(root, "Prefix").text = prefix
    ElementTree.SubElement(root, "KeyCount").text = str(len(files))
    ElementTree.SubElement(root, "MaxKeys").text = max_keys
    ElementTree.SubElement(root, "IsTruncated").text = "false"

    # Add the files to the XML response
    for file in files:
        content = ElementTree.SubElement(root, "Contents")
        last_modified_iso = datetime.datetime.fromtimestamp(os.path.getmtime(f"{physical_path}/{file}")).isoformat()
        file_size = os.path.getsize(f"{physical_path}/{file}")
        e_tag = aws_s3_etag(f"{physical_path}/{file}")
        ElementTree.SubElement(content, "Key").text = file
        ElementTree.SubElement(content, "Size").text = str(file_size)
        ElementTree.SubElement(content, "LastModified").text = last_modified_iso
        ElementTree.SubElement(content, "ETag").text = e_tag
        ElementTree.SubElement(content, "StorageClass").text = "STANDARD"

    # Return the XML response
    return ElementTree.tostring(root, encoding="utf-8", method="xml").decode("utf-8")


def aws_list_object_v1_response(req_url, query_string):
    # Parse the URL to extract the bucket and search parameters
    url_parsed = urlparse(req_url)
    bucket = url_parsed.path.split("/")[0]
    params = parse_qs(query_string)

    # check if its a list object v1 request
    if "list-type" in params and params["list-type"][0] != "1":
        return None

    # Get the prefix and max-keys search parameters
    prefix = params.get("prefix")[0]
    max_keys = params.get("max-keys")[0]

    # Read files from the /data directory
    physical_path = create_folder_if_not_exist(f"{bucket}/{prefix}")
    files = os.listdir(physical_path)

    # Create the XML response
    root = ElementTree.Element("ListBucketResult", {"xmlns": "http://s3.amazonaws.com/doc/2006-03-01/"})
    ElementTree.SubElement(root, "Name").text = bucket
    ElementTree.SubElement(root, "Prefix").text = prefix
    ElementTree.SubElement(root, "KeyCount").text = str(len(files))
    ElementTree.SubElement(root, "MaxKeys").text = max_keys
    ElementTree.SubElement(root, "IsTruncated").text = "false"

    # Add the files to the XML response
    for file in files:
        content = ElementTree.SubElement(root, "Contents")
        last_modified_iso = datetime.datetime.fromtimestamp(os.path.getmtime(f"{physical_path}/{file}")).isoformat()
        file_size = os.path.getsize(f"{physical_path}/{file}")
        e_tag = aws_s3_etag(f"{physical_path}/{file}")
        ElementTree.SubElement(content, "Key").text = file
        ElementTree.SubElement(content, "Size").text = str(file_size)
        ElementTree.SubElement(content, "LastModified").text = last_modified_iso
        ElementTree.SubElement(content, "ETag").text = e_tag
        ElementTree.SubElement(content, "StorageClass").text = "STANDARD"

    # Return the XML response
    return ElementTree.tostring(root, encoding="utf-8", method="xml").decode("utf-8")

# transform md5 to python
def md5(data):
    return hashlib.md5(data).hexdigest()

# transform awsS3Etag to python
def aws_s3_etag(file_path, part_size_bytes = 0):
    file = open(file_path, 'rb').read()
    if part_size_bytes == 0:
        return md5(file)
    size = os.stat(file_path).st_size
    part_count = math.floor(size / part_size_bytes)
    file_desc = open(file_path, 'rb')
    str_md5 = ''
    for i in range(part_count):
        skip = i * part_size_bytes
        left = size - skip
        to_read = min(left, part_size_bytes)
        buffer = file_desc.read(to_read)
        str_md5 += md5(buffer)
    file_desc.close()
    complete_md5 = md5(str_md5.encode('utf-8'))
    return f"{complete_md5}-{part_count}"


# PutObject 
# REQUEST PUT TestBucket /TestBucket/Lev1/Lev2/1
async def aws_put_object_stream_to_file(req):
    url_parts = req.url.path.split("/")
    key = url_parts[-1]
    relative_path = "/".join(url_parts[1:-1])
    p_path = create_folder_if_not_exist(relative_path)

    # read the stream and write to file
    body = await req.body()
    with open(f"{p_path}/{key}", "wb") as file:
        file.write(body)
        

    file.close()
    return p_path, key