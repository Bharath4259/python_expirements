# Bioler Plate

1. pip instatll -r requirements.txt
2. yarn static-install
3. python app.py --port=9999

# DOCKER

## CREATE

1. docker build -t test_frawework:1 .
2. docker ps
3. sudo docker run -it -p 9999:9999 test_frawework:1  bash
4. sudo docker commit --change='CMD ["python", "app.py"]' -c "EXPOSE 9999" ee77d85ad5d9  test_frawework:1

sudo docker container run -it -p 9999:9999 prod_management:1  bash
sudo docker tag prod_management:1 gcr.io/gcp-itbpe-analytics-shared-prd/prod_management:latest
sudo docker push gcr.io/gcp-itbpe-analytics-shared-prd/prod_management:latest

## UPLOAD

1. sudo docker container run test_frawework:1 -it bash
2. sudo docker tag test_frawework:1 gcr.io/gcp-itbpe-analytics-shared-prd/drl-framework:latest
3. sudo docker push gcr.io/gcp-itbpe-analytics-shared-prd/drl-framework:latest

## RUN/DEBUG

1. sudo docker run -it -p 9999:9999 test_frawework:1  bash
