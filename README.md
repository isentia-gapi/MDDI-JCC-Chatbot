1. pip install django
2. Set interpreter to 'venv'
3. py manage.py makemigrations
4. py manage.py migrate
5. pip install -r requirements.txt
6. py manage.py collectstatic
7. py manage.py runserver

--for making new apps--
py manage.py startapp app_name
*make sure to add the app_name into mddi_chatbot/settings.py -> INSTALLED_APPS