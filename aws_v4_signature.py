"""
This module contains functions to generate AWS V4 signatures for requests. 
It is used to validate signature sent by the client.
The details of the AWS V4 signature process can be found here:
https://docs.aws.amazon.com/AmazonS3/latest/API/sig-v4-header-based-auth.html
"""

import os
import hmac
import hashlib

def sign(key, msg):
    # from https://docs.aws.amazon.com/general/latest/gr/sigv4-signed-request-examples.html
    return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

def get_aws_v4_signature_key(key, datestamp, region, service):
    #  from https://docs.aws.amazon.com/general/latest/gr/sigv4-signed-request-examples.html
    key_date = sign(('AWS4' + key).encode('utf-8'), datestamp)
    key_region = sign(key_date, region)
    key_service = sign(key_region, service)
    return sign(key_service, 'aws4_request')

def get_aws_v4_canonical_request(request):
    # Get the HTTP method, URI, and query string from the starlette request object
    http_method = request.method
    request_uri = request.url.path
    query_string = request.url.query

    # Get the authorization header from the request
    authorization_header = request.headers['Authorization']
    # Extract the list of signed headers from the authorization header
    signed_headers = authorization_header.split(",")[1].split("=")[1].split(";")

    # Get the headers from the request
    headers = {}
    for key in request.headers:
        # Convert the header key to lowercase and remove any underscores
        key_low = key.lower().replace('_', '-')
        # Only include the header if it is listed in the signed headers

        if key_low in signed_headers:
            # Only include the header if it is listed in the signed headers
            headers[key_low] = request.headers[key]

    # Get the payload from the request
    payload = request.headers['x-amz-content-sha256']
    # Create a list of header keys in the request
    header_keys = sorted(headers.keys())
    # Create a list of header values in the request
    header_values = [headers[key] for key in header_keys]
    # Create a list of headers in key1;key2 format
    headers_str = '\n'.join(f'{key}:{value}' for key, value in zip(header_keys, header_values))
    # Create the AWS Canonical Request string
    canonical_request = f'{http_method}\n{request_uri}\n{query_string}\n{headers_str}\n\n{";".join(header_keys)}\n{payload}'

    return canonical_request

def get_aws_signature_arguments(request):
    # get the AWS signature arguments from the request
    authorization = request.headers['Authorization']
    credentials = authorization.split(",")[0].split("=")[1]
    amzdate = request.headers['x-amz-date']
    return os.getenv("AWS_SECRET_ACCESS_KEY"), get_aws_v4_canonical_request(request), credentials.split("/")[1], credentials.split("/")[2], credentials.split("/")[3], amzdate

def get_aws_v4_signature(aws_secret_access_key, canonical_request, date_stamp, aws_region, service, amzdate):
    algorithm = 'AWS4-HMAC-SHA256'
    scope = date_stamp + '/' + aws_region + '/' + service + '/' + 'aws4_request'
    
    # Create the StringToSign
    string_to_sign = algorithm + '\n' + amzdate + '\n' + scope +'\n' + hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()

    # Create the signing key 
    signing_key = get_aws_v4_signature_key(aws_secret_access_key, date_stamp, aws_region, service)

    # Sign the string_to_sign using the signing_key
    string_to_sign_utf8 = string_to_sign.encode('utf-8')
    signature = hmac.new(signing_key, string_to_sign_utf8, hashlib.sha256).hexdigest()
    return signature