PROJECT_ID=$(gcloud config get-value project 2> /dev/null)
docker build -t gcr.io/"$PROJECT_ID"/project-worker:latest .
docker push gcr.io/"$PROJECT_ID"/project-worker:latest
