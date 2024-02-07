sudo touch /etc/uwsgi/apps/forms.ini
sudo supervisorctl restart agents-forms-jobs
sudo supervisorctl restart agents-forms-celeryd
npm run build
