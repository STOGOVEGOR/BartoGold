# UPD
# 4

# TODO
chmod +x pull_and_restart.sh

sudo systemctl daemon-reload
sudo systemctl enable script.service
sudo systemctl start script.service

# .env
ALLOWED_HOSTS - add IP and address of the server
GIT_BRANCH - add {ref} data (deploying branch)

# get last 100 rows in log
sudo journalctl -u gu8085 -n 100
