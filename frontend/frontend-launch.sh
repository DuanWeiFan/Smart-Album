PROJECT_ID=$(gcloud config get-value project 2> /dev/null)
docker build -t gcr.io/"$PROJECT_ID"/rest-server:latest .
docker push gcr.io/"$PROJECT_ID"/rest-server:latest
kubectl create deployment rest-server --image=gcr.io/"$PROJECT_ID"/rest-server:latest
# kubectl expose deployment rest-server --type=LoadBalancer --port 5000 --target-port 5000
