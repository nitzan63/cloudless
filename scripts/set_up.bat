@echo off

cd ..
cd server

python -m venv venv

call venv\Scripts\activate

pip install -r requirements.txt

