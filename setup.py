import os

os.system('pip install -r requirements.txt')
os.system('pip install Angaza_Nexus_SDK_Python-0.0.1-py3-none-any.whl')
os.system('python manage.py migrate')
os.system('python manage.py createsuperuser')
