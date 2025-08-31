🚀 Installation
1. Prérequis
Python 3.10+
Node.js 18+ et npm
Angular CLI
Git

2. Cloner le projet 
git clone https://github.com/ton-user/ton-repo.git
cd chatbot

3. Backend 
## Aller dans le répertoire 
-> cd backend
## Installer l'environnement virtuel venv
->python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
## Intaller requirements.txt
->pip install -r requirements.txt
## Configurer les variables d’environnement backend/.env
SECRET_KEY=ton_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
## Lancer la migration 
python manage.py migrate
## Lancer le serveur 
python manage.py runserver


4. frontend
## aller dans le dossier frontend
cd frontend
## Installer angular et les dépendances
npm install -g @angular/cli
npm install
## Lancer le serveur angular
ng serve








