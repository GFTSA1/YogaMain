import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()


class S3Service:
    def __init__(self):
        self.client = boto3.client(
            "s3", os.getenv("AWS_ACCESS_KEY_ID"), os.getenv("AWS_SECRET_ACCESS_KEY")
        )
        self.bucket_name = os.getenv("AWS_BUCKET_NAME")

    def upload_file(self, file_object, content_type: str, object_name: str = None):
        try:
            self.client.upload_fileobj(
                file_object,
                self.bucket_name,
                object_name,
                ExtraArgs={"ContentType": content_type},
            )
            return True
        except ClientError as e:
            print(f"S3 upload error {e}")
            return False

    def delete_file(self, object_name: str):
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=object_name)
            return True
        except ClientError as e:
            print(f"S3 delete error {e}")
            return False

    def presigned_url(self, object_name: str, expiration: int = 3600):
        try:
            response = self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": object_name},
                ExpiresIn=expiration,
            )
            return response
        except ClientError as e:
            print(f"S3 presigned url error: {e}")
            return None
