echo installing requirements...
sudo pip3 install -r ./requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
cat << EOF >./gunicorn.conf.py 
bind = "127.0.0.1:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
EOF
echo creating service...
cat << EOF >~/fastapimvc.service
    [Unit]
    Description=Gunicorn service for myapp

    [Service]
    User=$USER 
    WorkingDirectory=$PWD
    ExecStart=gunicorn -c gunicorn.conf.py main:app  
    Restart=always
    StandardOutput=file:$PWD/service.log
    StandardError=file:$PWD/service.err

    [Install]
    WantedBy=multi-user.target

EOF

cat << EOF >./localhost.conf
map \$http_upgrade \$connection_upgrade {
          default upgrade;
          '' close;
}


upstream websocket {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name localhost;
    access_log  /var/log/nginx/localhost-access.log;
    error_log   /var/log/nginx/localhost-error.log;
    location / {
        proxy_pass http://websocket;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;   
    }
    location /ws/chat/ {
        proxy_pass http://websocket/ws/chat/;
        proxy_http_version 1.1;
        proxy_redirect off;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        #proxy_read_timeout 3600s;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for; 
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection \$connection_upgrade;


    }

}

EOF


sudo mv ~/fastapimvc.service /etc/systemd/system/
sudo sudo systemctl daemon-reload
sudo systemctl enable --now fastapimvc.service
sudo systemctl start fastapimvc.service
echo service fastapimvc created 
echo if nginx need , mv ./localhost.conf to /etc/nginx/sites-available/  and run  service nginx restart 
echo done.