gcloud config set account duongdhk@angular-land-419708.iam.gserviceaccount.com
gcloud auth activate-service-account duongdhk@angular-land-419708.iam.gserviceaccount.com
gcloud auth activate-service-account --key-file /mnt/data1/PycharmProjects/research/duongdhk_research/paper_recommender_web/configs/angular-land-419708-ae255fcab897.json
sudo docker tag paper_recommender_web:v1 asia-southeast1-docker.pkg.dev/angular-land-419708/paper-recommender-web-registry/paper_recommender_web_image
docker run -it -e NGROK_AUTHTOKEN=2f5ZUIrZDCiSAWwbWo8bBzYnLd2_3hBJsTpph7wNNYNPaNXc3 ngrok/ngrok:latest http 8080