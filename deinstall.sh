
sudo rm /etc/supervisor/conf.d/agents_forms.conf
sudo rm /etc/nginx/sites-enabled/agents_forms_nginx.conf
sudo supervisorctl update
sudo systemctl restart nginx
