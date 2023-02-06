pg_dump -U postgres -W -d forms-medsenger-bot -h 127.0.0.1 > forms_bot.sql
zip -r forms.zip forms_bot.sql
