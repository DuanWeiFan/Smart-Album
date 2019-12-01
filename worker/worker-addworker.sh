PROJECT_ID=$(gcloud config get-value project 2> /dev/null)
echo "Adding worker: $1"
kubectl create deployment "$1"-server --image=gcr.io/"$PROJECT_ID"/project-worker:latest
