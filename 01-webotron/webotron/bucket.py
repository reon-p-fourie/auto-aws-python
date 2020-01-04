# -*- utf-8 -*-

""" Classes for s3 buckets. """
class BucketManager:
    """ Manage a S3 Bucket. """

    def __init__(self, session):
        """ Create a Bucket Masnager object. """
        self.s3 = session.resource('s3')

    def all_buckets(self):
        """Get an iterator for all buckets."""
        return self.s3.buckets.all()

    def all_objects(self, bucket_name):
        return self.s3.Bucket(bucket_name).objects.all()

