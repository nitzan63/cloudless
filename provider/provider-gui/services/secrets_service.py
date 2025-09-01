import keyring
import tkinter as tk
from tkinter import messagebox

class SecretsService:
    def __init__(self, service_name="SecretsService", key_name="user_token"):
        self.service_name = service_name
        self.key_name = key_name
        self.username_key = "username"
    
    def save_token(self, token):
        keyring.set_password(self.service_name, self.key_name, token)
    
    def get_token(self):
        return keyring.get_password(self.service_name, self.key_name)
    
    def delete_token(self):
        try:
            keyring.delete_password(self.service_name, self.key_name)
        except keyring.errors.PasswordDeleteError:
            pass
    
    def logout(self):
        self.delete_token(self.key_name)
        self.delete_username()
    
    def save_username(self, username):
        keyring.set_password(self.service_name, self.username_key, username)
    
    def get_username(self):
        return keyring.get_password(self.service_name, self.username_key)
    
    def delete_username(self):
        try:
            keyring.delete_password(self.service_name, self.username_key)
        except keyring.errors.PasswordDeleteError:
            pass
