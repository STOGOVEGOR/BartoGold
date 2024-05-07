# UPD
# 18

# TODO

chmod +x pull_and_restart.sh

sudo apt install python3.10-venv
python3 -m venv venv
source venv/bin/activate
pip install -r req.txt

sudo systemctl daemon-reload
sudo systemctl enable gu8085
sudo systemctl start gu8085

# .env
ALLOWED_HOSTS - add IP and address of the server
GIT_BRANCH - add {ref} data (deploying branch)

# get last 100 rows in log
sudo journalctl -u gu8085 -n 100
