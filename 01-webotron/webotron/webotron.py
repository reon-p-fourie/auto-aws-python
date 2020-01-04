#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
# auto-aws-python
automating aws using python

## 01-webotron

Webotron is a script that will sync a local directory to an s3 bucket,
and optionally configure Route 53 and cloudfront as well.

### Features

Webotron currently has the following features:

- List bucket
- List bucket objects
- Create and setup bucket

"""
import mimetypes
from pathlib import Path
import boto3
from botocore.exceptions import ClientError
import click

from bucket import BucketManager

session = boto3.Session()
bucket_manager = BucketManager(session)
#s3 = session.resource('s3')

@click.group()
def cli():
    """Webotron deploys websites to AWS"""
    pass

@cli.command('list-buckets')
def list_buckets():
    """List all s3 buckets"""
    for bucket in bucket_manager.all_buckets():
        print(bucket)

@cli.command('list-bucket-objects')
@click.argument('bucket')
def list_bucket_objects(bucket):
    """List all objects in a bucket"""
    for obj in bucket_manager.all_objects(bucket):
        print(obj)

@cli.command('setup-bucket')
@click.argument('bucket')
def setup_bucket(bucket):
    """Create and configure S3 Bucket"""
    s3_bucket = None

    try:
        s3_bucket = s3.create_bucket(
            Bucket=bucket,
            CreateBucketConfiguration={'LocationConstraint': session.region_name}
        )
    except ClientError as e:
        if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            s3_bucket = s3.Bucket(bucket)
        else:
            raise e

    policy = """
    {
        "Version":"2012-10-17",
        "Statement":[{
            "Sid":"PublicReadGetObject",
            "Effect":"Allow",
            "Principal":"*",
            "Action":["s3:GetObject"],
            "Resource":["arn:aws:s3:::%s/*"]
        }]
    }
    """ % s3_bucket.name
    policy = policy.strip()

    pol = s3_bucket.Policy()
    pol.put(Policy=policy)

    ws = s3_bucket.Website()
    ws.put(WebsiteConfiguration={
        'ErrorDocument': {
            'Key': 'error.html'
        },
        'IndexDocument': {
            'Suffix': 'index.html'
        }
    })

def upload_file(s3_bucket, path, key):
    content_type = mimetypes.guess_type(key)[0] or 'text/plain'

    s3_bucket.upload_file(
        path, 
        key, 
        ExtraArgs={
            'ContentType': content_type
        }
    )

@cli.command('sync')
@click.argument('pathname', type=click.Path(exists=True))
@click.argument('bucket')
def sync(pathname, bucket):
    """Sync contents of PATHNAME to BUCKET"""
    s3_bucket = s3.Bucket(bucket)
    root = Path(pathname).expanduser().resolve()
    print(root)

    def handle_directory(target):
        for p in target.iterdir():
            if p.is_dir(): handle_directory(p)
            if p.is_file(): upload_file(s3_bucket, str(p), str(p.relative_to(root)))
    
    handle_directory(root)

if __name__ == '__main__':
    cli()