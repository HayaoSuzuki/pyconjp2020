import csv
import io
import json
import urllib.parse
import urllib.request
import zipfile

import boto3


class S3Client:
    """S3関連のメソッドを取り扱う."""

    def __init__(self) -> None:
        self.client = boto3.client("s3")
        self.bucket = "target_bucket"

    def upload_file(self, byte_stream: io.BytesIO, file_name: str) -> None:
        """ファイルをアップロードする。"""
        byte_stream.seek(0)  # Seekしておくのがミソ
        self.client.upload_fileobj(byte_stream, self.bucket, file_name)


params = urllib.parse.urlencode({"keyword": "Python", "count": 20})
url = f"https://connpass.com/api/v1/event/?{params}"
s3_client = S3Client()

with urllib.request.urlopen(url) as response:
    events = json.load(response)["events"]

with io.StringIO() as test_stream:
    header = ["title", "started_at", "ended_at"]
    writer = csv.DictWriter(test_stream, fieldnames=header, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(events)

    with io.BytesIO() as bytes_stream:
        with zipfile.ZipFile(bytes_stream, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
            zf.writestr("python_events.csv", test_stream.getvalue())
        s3_client.upload_file(bytes_stream, "python_events.zip")
