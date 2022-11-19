git pull
flask db migrate
flask db upgrade
sudo pip3 install -r requirements.txt
sudo cp agents_forms.conf /etc/supervisor/conf.d/
sudo supervisorctl update
sudo supervisorctl restart agents-forms
sudo supervisorctl restart agents-forms-jobs
sudo supervisorctl restart agents-forms-celeryd
