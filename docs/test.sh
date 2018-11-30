sed -i "s/^    server_name.*/    server_name 10.20.20.12;/g" \
    ~/decode_website/deployment_configs/nginx_decode
cd ~/decode_website/certs/
openssl req -x509 -newkey rsa:4096 -sha256 -keyout key.pem -out cert.pem -days 3650  -nodes \
-subj "/C=CN/ST=Guangdong/L=Shenzhen/O=Shenzhen Research Institute of Big Data/OU=Learning Analytics/CN=10.20.20.12"
sudo systemctl restart nginx
