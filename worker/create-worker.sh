PROJECT_ID=$(gcloud config get-value project 2> /dev/null)
kubectl create deployment image-worker --image=gcr.io/"$PROJECT_ID"/project-worker:latest
# kubectl expose deployment image-worker --port 50051 --target-port=50051
