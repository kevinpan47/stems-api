setup:
- create bucket in gcp
- create service account with storage admin role, condition if name starts with projects/{project_id}/buckets/{bucket_name}
- create access key for service account, name service-account-key.json and place in root of project