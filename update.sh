git pull
flask db migrate
flask db upgrade
sudo cp agents_forms.conf /etc/supervisor/conf.d/
sudo supervisorctl update
sudo ./restart.sh
