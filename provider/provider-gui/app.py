import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QStackedWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFormLayout, QSpinBox, QToolButton,
    QMainWindow, QMenuBar, QAction, QFrame, QGridLayout, QGroupBox, QProgressBar, QSystemTrayIcon, QStatusBar, QSplitter, QTabWidget,
    QDialog, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread, QObject, QPropertyAnimation, QEasingCurve, pyqtProperty, QRect
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon, QPixmap
from services.register_service import RegisterService
import os
import socket
import psutil
from services.auth_service import AuthService
from services.secrets_service import SecretsService
from services.files_service import FilesService
from services.docker_runner_service import DockerRunnerService
from dotenv import load_dotenv

load_dotenv()

auth_service = AuthService(os.environ.get('AUTH_SERVICE_URL', "http://localhost:8003"))
secrets_service = SecretsService()
register_service = RegisterService(os.environ.get('REGISTER_SERVICE_URL', "http://localhost:8001"), secrets_service)
files_service = FilesService("CloudlessLocalProvider", "Cloudless")
docker_runner_service = DockerRunnerService()

# --- Dark Mode Palette ---
def set_dark_mode(app):
    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor(30, 30, 30))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(40, 40, 40))
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(45, 45, 45))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(dark_palette)
    app.setStyle("Fusion")

# --- Helper for rounded QLineEdit ---
def rounded_line_edit(password=False):
    le = QLineEdit()
    le.setStyleSheet("""
        QLineEdit {
            border-radius: 12px;
            padding: 14px 16px;
            border: 2px solid #444;
            background: #232323;
            color: #fff;
            font-size: 16px;
            line-height: 1.2;
            selection-background-color: #42A5F5;
        }
        QLineEdit:focus {
            border: 2px solid #42A5F5;
            background: #2a2a2a;
        }
        QLineEdit:hover {
            border: 2px solid #555;
        }
    """)
    le.setMinimumWidth(280)
    le.setMaximumWidth(420)
    le.setMinimumHeight(50)
    if password:
        le.setEchoMode(QLineEdit.Password)
    return le

# --- Professional styled button ---
def styled_button(text, primary=True):
    btn = QPushButton(text)
    if primary:
        btn.setStyleSheet("""
            QPushButton {
                background-color: #42A5F5;
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
    else:
        btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #42A5F5;
                border: 2px solid #42A5F5;
                padding: 12px 24px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #42A5F5;
                color: white;
            }
        """)
    return btn

# --- Loading Widget ---
class LoadingWidget(QWidget):
    def __init__(self, message="Loading..."):
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        self.message_label = QLabel(message)
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setStyleSheet("color: #7ecfff; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(self.message_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #555;
                border-radius: 8px;
                background-color: #2a2a2a;
                text-align: center;
                color: white;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #42A5F5, stop:1 #1976D2);
                border-radius: 6px;
            }
        """)
        self.progress_bar.setMinimumWidth(200)
        layout.addWidget(self.progress_bar)
        
        self.setLayout(layout)
    
    def set_message(self, message):
        self.message_label.setText(message)

# --- Worker Classes for Threading ---
class AuthWorker(QObject):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    
    def __init__(self, operation, *args):
        super().__init__()
        self.operation = operation
        self.args = args
    
    def run(self):
        try:
            if self.operation == "login":
                result = auth_service.login(self.args[0], self.args[1])
                self.finished.emit(result)
            elif self.operation == "register":
                result = auth_service.register(self.args[0], self.args[1])
                self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

class ResourceWorker(QObject):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)
    
    def __init__(self, operation, *args):
        super().__init__()
        self.operation = operation
        self.args = args
    
    def run(self):
        try:
            if self.operation == "start":
                self.progress.emit("Registering with network...")
                data = register_service.register()
                
                self.progress.emit("Configuring network...")
                if 'status' in data and data['status'] == "NEW_USER_REGISTERED":
                    files_service.save_config("wg0.conf", data['conf'])
                
                self.progress.emit("Starting container...")
                network_ip = data.get('network_ip')
                container_id = docker_runner_service.run(
                    image="spark-worker-vpn",
                    container_name="spark-worker-1",
                    port_map="8881:8881",
                    env_vars={
                        "SPARK_MASTER_IP": "10.10.0.1",
                        "SPARK_LOCAL_IP": network_ip,
                        "SPARK_LOCAL_HOSTNAME": network_ip
                    },
                    volume_map={
                        files_service.get_config_path(): "/etc/wireguard"
                    },
                    additional_flags=["--cap-add=NET_ADMIN", "--device", "/dev/net/tun"]
                )
                
                result = {
                    'container_id': container_id,
                    'network_ip': network_ip,
                    'credits': data.get('credits', 0)
                }
                self.finished.emit(result)
                
            elif self.operation == "stop":
                self.progress.emit("Stopping container...")
                
                # First try to stop by container key
                success = docker_runner_service.stop_and_remove("spark-worker-1")
                if success:
                    self.finished.emit({"status": "stopped"})
                else:
                    # Check if there are any saved containers and try to stop them
                    containers = docker_runner_service.list_saved_containers()
                    if containers:
                        # Try to stop each saved container
                        for key in containers.keys():
                            docker_runner_service.stop_and_remove(key)
                    
                    # Also try the generic stop (uses self.container_id)
                    docker_runner_service.stop_and_remove()
                    
                    self.finished.emit({"status": "stopped"})
                
        except Exception as e:
            self.error.emit(str(e))

# --- User Profile Dialog ---
class UserProfileDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("User Profile & Settings")
        self.setFixedSize(500, 400)
        self.setModal(True)
        
        # Set dialog background and styling
        self.setStyleSheet("""
            QDialog {
                background-color: #1e1e1e;
                color: white;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Profile header
        header = QLabel("Account Settings")
        header.setFont(QFont("Segoe UI", 20, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet("color: #7ecfff; margin-bottom: 20px;")
        layout.addWidget(header)
        
        # User info group
        user_group = QGroupBox("User Information")
        user_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        user_layout = QFormLayout()
        
        # Get saved username
        try:
            saved_username = secrets_service.get_username()
            token = secrets_service.get_token()
            
            if saved_username and token:
                username_label = QLabel(saved_username)
                username_label.setStyleSheet("font-weight: bold; color: #42A5F5;")
                
                # Also show login status
                status_label = QLabel("Logged In")
                status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")
            elif saved_username:
                username_label = QLabel(saved_username)
                username_label.setStyleSheet("font-weight: bold; color: #999;")
                
                status_label = QLabel("Not Logged In")
                status_label.setStyleSheet("color: #f44336; font-weight: bold;")
            else:
                username_label = QLabel("No username saved")
                username_label.setStyleSheet("color: #999;")
                
                status_label = QLabel("Not Logged In")
                status_label.setStyleSheet("color: #f44336; font-weight: bold;")
        except:
            username_label = QLabel("Unknown")
            username_label.setStyleSheet("color: #999;")
            status_label = QLabel("Unknown")
            status_label.setStyleSheet("color: #999;")
            
        user_layout.addRow("Username:", username_label)
        user_layout.addRow("Status:", status_label)
        user_group.setLayout(user_layout)
        layout.addWidget(user_group)
        
        # Settings group
        settings_group = QGroupBox("Application Settings")
        settings_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        settings_layout = QVBoxLayout()
        
        # Placeholder for future settings
        settings_text = QLabel("Auto-start resource sharing: Disabled\nNotifications: Enabled\nUpdate checks: Enabled")
        settings_text.setStyleSheet("color: #ccc; line-height: 1.5;")
        settings_layout.addWidget(settings_text)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # Close button
        close_btn = styled_button("Close", primary=True)
        close_btn.clicked.connect(self.accept)  # Use accept() for proper dialog closing
        layout.addWidget(close_btn)
        
        self.setLayout(layout)

# --- Login Page ---
class LoginPage(QWidget):
    def __init__(self, switch_to_register, switch_to_main):
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        
        # Welcome message
        welcome = QLabel("Welcome Back")
        welcome.setFont(QFont("Segoe UI", 28, QFont.Bold))
        welcome.setAlignment(Qt.AlignCenter)
        welcome.setStyleSheet("color: #7ecfff; margin-bottom: 10px;")
        layout.addWidget(welcome)
        
        subtitle = QLabel("Sign in to start earning credits")
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #999; margin-bottom: 30px;")
        layout.addWidget(subtitle)
        
        # Login form in a container
        form_container = QFrame()
        form_container.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        form_container.setMaximumWidth(450)
        form_container.setMinimumWidth(450)
        
        form_layout = QVBoxLayout()
        form_layout.setSpacing(20)
        
        self.username = rounded_line_edit()
        self.username.setPlaceholderText("Enter your username")
        self.password = rounded_line_edit(password=True)
        self.password.setPlaceholderText("Enter your password")
        
        form_layout.addWidget(self.username)
        form_layout.addWidget(self.password)
        
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #f44336; font-size: 14px; margin: 5px 0;")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setWordWrap(True)
        form_layout.addWidget(self.error_label)
        
        self.btn_login = styled_button("Sign In", primary=True)
        self.btn_login.clicked.connect(self.handle_login)
        form_layout.addWidget(self.btn_login)
        
        # Loading widget (initially hidden)
        self.loading_widget = LoadingWidget("Signing in...")
        self.loading_widget.hide()
        form_layout.addWidget(self.loading_widget)
        
        # Register link
        register_layout = QHBoxLayout()
        register_layout.setAlignment(Qt.AlignCenter)
        register_text = QLabel("Don't have an account?")
        register_text.setStyleSheet("color: #999;")
        btn_register = QPushButton("Create Account")
        btn_register.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #42A5F5;
                border: none;
                text-decoration: underline;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #1976D2;
            }
        """)
        btn_register.clicked.connect(switch_to_register)
        register_layout.addWidget(register_text)
        register_layout.addWidget(btn_register)
        form_layout.addLayout(register_layout)
        
        form_container.setLayout(form_layout)
        
        # Center the form container
        container_layout = QHBoxLayout()
        container_layout.addStretch()
        container_layout.addWidget(form_container)
        container_layout.addStretch()
        
        layout.addLayout(container_layout)
        layout.addStretch()
        self.setLayout(layout)
        self._switch_to_main = switch_to_main

    def handle_login(self):
        username = self.username.text()
        password = self.password.text()
        
        if not username or not password:
            self.error_label.setText("Please enter both username and password")
            return
        
        self.error_label.setText("")
        self.show_loading()
        
        # Create worker and thread for login
        self.thread = QThread()
        self.worker = AuthWorker("login", username, password)
        self.worker.moveToThread(self.thread)
        
        # Connect signals
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_login_success)
        self.worker.error.connect(self.on_login_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        self.thread.start()
    
    def show_loading(self):
        self.btn_login.setEnabled(False)
        self.username.setEnabled(False)
        self.password.setEnabled(False)
        self.loading_widget.show()
    
    def hide_loading(self):
        self.btn_login.setEnabled(True)
        self.username.setEnabled(True)
        self.password.setEnabled(True)
        self.loading_widget.hide()
    
    def on_login_success(self, result):
        self.hide_loading()
        if 'access_token' in result:
            secrets_service.save_token(result['access_token'])
            # Save the username for display in settings
            secrets_service.save_username(self.username.text())
            parent = self.parent()
            while parent is not None and not hasattr(parent, 'access_token'):
                parent = parent.parent()
            if parent is not None:
                parent.access_token = result['access_token']
            self._switch_to_main()
        else:
            self.error_label.setText("Login failed: Incorrect username or password.")
    
    def on_login_error(self, error_msg):
        self.hide_loading()
        self.error_label.setText(f"Login error: {error_msg}")

# --- Register Page ---
class RegisterPage(QWidget):
    def __init__(self, switch_to_login):
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        
        # Welcome message
        welcome = QLabel("Create Account")
        welcome.setFont(QFont("Segoe UI", 28, QFont.Bold))
        welcome.setAlignment(Qt.AlignCenter)
        welcome.setStyleSheet("color: #7ecfff; margin-bottom: 10px;")
        layout.addWidget(welcome)
        
        subtitle = QLabel("Join the network and start earning")
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #999; margin-bottom: 30px;")
        layout.addWidget(subtitle)
        
        # Registration form in a container
        form_container = QFrame()
        form_container.setStyleSheet("""
            QFrame {
                background-color: #2a2a2a;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        form_container.setMaximumWidth(450)
        form_container.setMinimumWidth(450)
        
        form_layout = QVBoxLayout()
        form_layout.setSpacing(20)
        
        self.username = rounded_line_edit()
        self.username.setPlaceholderText("Choose a username")
        self.password = rounded_line_edit(password=True)
        self.password.setPlaceholderText("Create a password")
        self.confirm_password = rounded_line_edit(password=True)
        self.confirm_password.setPlaceholderText("Confirm your password")
        
        form_layout.addWidget(self.username)
        form_layout.addWidget(self.password)
        form_layout.addWidget(self.confirm_password)
        
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: #f44336; font-size: 14px; margin: 5px 0;")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setWordWrap(True)
        form_layout.addWidget(self.error_label)
        
        self.btn_register = styled_button("Create Account", primary=True)
        self.btn_register.clicked.connect(self.handle_register)
        form_layout.addWidget(self.btn_register)
        
        # Loading widget (initially hidden)
        self.loading_widget = LoadingWidget("Creating account...")
        self.loading_widget.hide()
        form_layout.addWidget(self.loading_widget)
        
        # Login link
        login_layout = QHBoxLayout()
        login_layout.setAlignment(Qt.AlignCenter)
        login_text = QLabel("Already have an account?")
        login_text.setStyleSheet("color: #999;")
        btn_back = QPushButton("Sign In")
        btn_back.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #42A5F5;
                border: none;
                text-decoration: underline;
                font-weight: bold;
            }
            QPushButton:hover {
                color: #1976D2;
            }
        """)
        btn_back.clicked.connect(lambda: switch_to_login())
        login_layout.addWidget(login_text)
        login_layout.addWidget(btn_back)
        form_layout.addLayout(login_layout)
        
        form_container.setLayout(form_layout)
        
        # Center the form container
        container_layout = QHBoxLayout()
        container_layout.addStretch()
        container_layout.addWidget(form_container)
        container_layout.addStretch()
        
        layout.addLayout(container_layout)
        layout.addStretch()
        self.setLayout(layout)
        self._switch_to_login = switch_to_login

    def handle_register(self):
        username = self.username.text()
        password = self.password.text()
        confirm_password = self.confirm_password.text()
        
        self.error_label.setText("")
        
        if not username or not password or not confirm_password:
            self.error_label.setText("Please fill in all fields")
            return
            
        if password != confirm_password:
            self.error_label.setText("Passwords do not match.")
            return
        
        self.show_loading()
        
        # Create worker and thread for registration
        self.thread = QThread()
        self.worker = AuthWorker("register", username, password)
        self.worker.moveToThread(self.thread)
        
        # Connect signals
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_register_success)
        self.worker.error.connect(self.on_register_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        self.thread.start()
    
    def show_loading(self):
        self.btn_register.setEnabled(False)
        self.username.setEnabled(False)
        self.password.setEnabled(False)
        self.confirm_password.setEnabled(False)
        self.loading_widget.show()
    
    def hide_loading(self):
        self.btn_register.setEnabled(True)
        self.username.setEnabled(True)
        self.password.setEnabled(True)
        self.confirm_password.setEnabled(True)
        self.loading_widget.hide()
    
    def on_register_success(self, result):
        self.hide_loading()
        if result.get('status') == 'success':
            # Save the username for future reference
            secrets_service.save_username(self.username.text())
            self._switch_to_login()
        else:
            self.error_label.setText("Registration failed.")
    
    def on_register_error(self, error_msg):
        self.hide_loading()
        self.error_label.setText(f"Registration error: {error_msg}")

# --- Simple Animated Credits Widget ---
class AnimatedCreditsWidget(QGroupBox):
    def __init__(self):
        super().__init__("Credits")
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        layout = QVBoxLayout()
        self.current_credits = 0
        
        # Main credits display
        self.credits_label = QLabel("0")
        self.credits_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        self.credits_label.setAlignment(Qt.AlignCenter)
        self.credits_label.setStyleSheet("color: #4CAF50; margin: 10px;")
        
        # Simple increase notification label
        self.increase_label = QLabel("")
        self.increase_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.increase_label.setAlignment(Qt.AlignCenter)
        self.increase_label.setStyleSheet("""
            color: #FFD700; 
            background-color: rgba(76, 175, 80, 40);
            border-radius: 8px;
            padding: 4px 12px;
            margin: 2px;
        """)
        self.increase_label.hide()
        
        credits_text = QLabel("Available Credits")
        credits_text.setAlignment(Qt.AlignCenter)
        credits_text.setStyleSheet("color: #999; font-size: 12px;")
        
        layout.addWidget(self.credits_label)
        layout.addWidget(self.increase_label)
        layout.addWidget(credits_text)
        self.setLayout(layout)
        
        # Periodic update timer - check every 15 seconds
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_credits_from_server)
        self.update_timer.start(15000)
    
    def update_credits_from_server(self):
        """Periodically fetch credits from server"""
        try:
            data = register_service.get_details()
            if 'credits' in data:
                new_credits = int(data['credits'])
                if new_credits > self.current_credits and self.current_credits > 0:
                    # Credits increased - show simple animation
                    increase = new_credits - self.current_credits
                    self.show_credits_increase(increase)
                self.current_credits = new_credits
                self.credits_label.setText(str(new_credits))
        except Exception as e:
            print(f"Error updating credits: {e}")
    
    def show_credits_increase(self, increase):
        """Show simple notification when credits increase"""
        # Show the increase message
        self.increase_label.setText(f"+{increase} Credits Earned! 🎉")
        self.increase_label.show()
        
        # Briefly highlight the main credits label
        original_style = self.credits_label.styleSheet()
        self.credits_label.setStyleSheet("color: #FFD700; margin: 10px; font-weight: bold;")
        
        # Hide the notification after 3 seconds
        QTimer.singleShot(3000, self.hide_increase_notification)
        
        # Return credits label to normal after 1 second
        QTimer.singleShot(1000, lambda: self.credits_label.setStyleSheet(original_style))
    
    def hide_increase_notification(self):
        """Hide the increase notification"""
        self.increase_label.hide()
    
    def set_credits(self, credits):
        """Manually set credits (used during start/stop operations)"""
        old_credits = self.current_credits
        self.current_credits = credits
        self.credits_label.setText(str(credits))
        
        # If this is an increase and we had previous credits, show notification
        if credits > old_credits and old_credits > 0:
            increase = credits - old_credits
            self.show_credits_increase(increase)

# --- Legacy Credits Widget (for compatibility) ---
class CreditsWidget(AnimatedCreditsWidget):
    pass

# --- Network Info Widget ---
class NetworkInfoWidget(QGroupBox):
    def __init__(self):
        super().__init__("Network Information")
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        layout = QGridLayout()
        
        self.local_ip_label = QLabel("Local IP:")
        self.local_ip_value = QLabel("Getting...")
        self.network_ip_label = QLabel("Network IP:")
        self.network_ip_value = QLabel("Not connected")
        self.status_label = QLabel("Status:")
        self.status_value = QLabel("Offline")
        self.uptime_label = QLabel("Running Time:")
        self.uptime_value = QLabel("Not running")
        
        layout.addWidget(self.local_ip_label, 0, 0)
        layout.addWidget(self.local_ip_value, 0, 1)
        layout.addWidget(self.network_ip_label, 1, 0)
        layout.addWidget(self.network_ip_value, 1, 1)
        layout.addWidget(self.status_label, 2, 0)
        layout.addWidget(self.status_value, 2, 1)
        layout.addWidget(self.uptime_label, 3, 0)
        layout.addWidget(self.uptime_value, 3, 1)
        
        self.setLayout(layout)
        self.get_local_ip()
    
    def get_local_ip(self):
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            self.local_ip_value.setText(local_ip)
        except:
            self.local_ip_value.setText("Unknown")
    
    def set_network_ip(self, ip):
        self.network_ip_value.setText(ip)
    
    def set_status(self, status, color="#4CAF50"):
        self.status_value.setText(status)
        self.status_value.setStyleSheet(f"color: {color}; font-weight: bold;")
    
    def set_uptime(self, uptime):
        self.uptime_value.setText(uptime)
        if uptime == "Not running":
            self.uptime_value.setStyleSheet("color: #999;")
        else:
            self.uptime_value.setStyleSheet("color: #4CAF50; font-weight: bold;")

# --- System Resources Widget ---
class SystemResourcesWidget(QGroupBox):
    def __init__(self):
        super().__init__("System Resources")
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        layout = QVBoxLayout()
        
        # CPU Usage
        cpu_layout = QHBoxLayout()
        cpu_layout.addWidget(QLabel("CPU:"))
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setStyleSheet("QProgressBar::chunk { background-color: #2196F3; }")
        cpu_layout.addWidget(self.cpu_progress)
        self.cpu_label = QLabel("0%")
        cpu_layout.addWidget(self.cpu_label)
        layout.addLayout(cpu_layout)
        
        # Memory Usage
        mem_layout = QHBoxLayout()
        mem_layout.addWidget(QLabel("RAM:"))
        self.mem_progress = QProgressBar()
        self.mem_progress.setStyleSheet("QProgressBar::chunk { background-color: #FF9800; }")
        mem_layout.addWidget(self.mem_progress)
        self.mem_label = QLabel("0%")
        mem_layout.addWidget(self.mem_label)
        layout.addLayout(mem_layout)
        
        self.setLayout(layout)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_resources)
        self.timer.start(2000)  # Update every 2 seconds
    
    def update_resources(self):
        try:
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            
            self.cpu_progress.setValue(int(cpu_percent))
            self.cpu_label.setText(f"{cpu_percent:.1f}%")
            
            self.mem_progress.setValue(int(memory.percent))
            self.mem_label.setText(f"{memory.percent:.1f}%")
        except:
            pass

# --- Professional Main Dashboard ---
class MainDashboard(QMainWindow):
    def __init__(self, logout_callback):
        super().__init__()
        self.logout_callback = logout_callback
        self.is_running = False
        self.network_ip = None
        self.credits = 0
        
        self.setWindowTitle("Cloudless Provider - Dashboard")
        self.setMinimumSize(900, 600)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Create central widget with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout()
        
        # Left sidebar with controls
        left_panel = QFrame()
        left_panel.setFrameStyle(QFrame.StyledPanel)
        left_panel.setMaximumWidth(300)
        left_panel.setStyleSheet("QFrame { background-color: #2a2a2a; border-radius: 8px; }")
        
        left_layout = QVBoxLayout()
        
        # Credits widget
        self.credits_widget = CreditsWidget()
        left_layout.addWidget(self.credits_widget)
        
        # Control panel
        control_group = QGroupBox("Resource Control")
        control_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        control_layout = QVBoxLayout()
        
        # Resource allocation
        form = QFormLayout()
        self.ram_spin = QSpinBox()
        self.ram_spin.setRange(1, 128)
        self.ram_spin.setSuffix(" GB")
        self.ram_spin.setValue(4)
        self.ram_spin.setStyleSheet("QSpinBox { padding: 5px; border-radius: 4px; }")
        
        self.cores_spin = QSpinBox()
        self.cores_spin.setRange(1, 32)
        self.cores_spin.setValue(2)
        self.cores_spin.setSuffix(" Cores")
        self.cores_spin.setStyleSheet("QSpinBox { padding: 5px; border-radius: 4px; }")
        
        form.addRow("RAM Allocation:", self.ram_spin)
        form.addRow("CPU Cores:", self.cores_spin)
        control_layout.addLayout(form)
        
        # Start/Stop button
        self.btn_start = QPushButton("Start Sharing")
        self.btn_start.setCheckable(True)
        self.btn_start.clicked.connect(self.toggle_start_stop)
        self.btn_start.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:checked {
                background-color: #f44336;
            }
            QPushButton:checked:hover {
                background-color: #da190b;
            }
        """)
        control_layout.addWidget(self.btn_start)
        
        # Loading widget for start/stop operations
        self.operation_loading = LoadingWidget("Starting...")
        self.operation_loading.hide()
        control_layout.addWidget(self.operation_loading)
        
        control_group.setLayout(control_layout)
        left_layout.addWidget(control_group)
        
        left_layout.addStretch()
        left_panel.setLayout(left_layout)
        
        # Right panel with tabs
        right_panel = QTabWidget()
        right_panel.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #555;
                background-color: #2a2a2a;
            }
            QTabBar::tab {
                background-color: #3a3a3a;
                color: white;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #555;
            }
        """)
        
        # Dashboard tab
        dashboard_tab = QWidget()
        dashboard_layout = QVBoxLayout()
        
        # Network info
        self.network_widget = NetworkInfoWidget()
        dashboard_layout.addWidget(self.network_widget)
        
        # System resources
        self.resources_widget = SystemResourcesWidget()
        dashboard_layout.addWidget(self.resources_widget)
        
        dashboard_layout.addStretch()
        dashboard_tab.setLayout(dashboard_layout)
        
        # Activity log tab
        activity_tab = QWidget()
        activity_layout = QVBoxLayout()
        
        activity_header = QLabel("Activity Log")
        activity_header.setFont(QFont("Segoe UI", 16, QFont.Bold))
        activity_header.setStyleSheet("color: #7ecfff; margin-bottom: 10px;")
        activity_layout.addWidget(activity_header)
        
        self.activity_log = QLabel("🔄 Waiting for activity...")
        self.activity_log.setStyleSheet("""
            background-color: #1a1a1a; 
            padding: 15px; 
            border-radius: 6px;
            border: 1px solid #333;
            color: #ccc;
            font-family: 'Consolas', monospace;
            line-height: 1.4;
        """)
        self.activity_log.setWordWrap(True)
        self.activity_log.setAlignment(Qt.AlignTop)
        activity_layout.addWidget(self.activity_log)
        activity_tab.setLayout(activity_layout)
        
        right_panel.addTab(dashboard_tab, "Dashboard")
        right_panel.addTab(activity_tab, "Activity")
        
        # Add panels to main layout
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel, 2)  # Give more space to right panel
        
        central_widget.setLayout(main_layout)
        
        # Load initial credits and container state
        self.load_initial_data()
        self.load_container_state()
        
        # Setup uptime update timer - update every 30 seconds
        self.uptime_timer = QTimer()
        self.uptime_timer.timeout.connect(self.update_uptime)
        self.uptime_timer.start(30000)  # Update every 30 seconds
    
    def create_menu_bar(self):
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        profile_action = QAction('Profile and Settings', self)
        profile_action.triggered.connect(self.show_profile)
        file_menu.addAction(profile_action)
        
        file_menu.addSeparator()
        
        logout_action = QAction('Logout', self)
        logout_action.triggered.connect(self.handle_logout)
        file_menu.addAction(logout_action)
        
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu('View')
        refresh_action = QAction('Refresh Data', self)
        refresh_action.triggered.connect(self.refresh_all_data)
        view_menu.addAction(refresh_action)
        
        # Tools menu
        tools_menu = menubar.addMenu('Tools')
        details_action = QAction('Show Details', self)
        details_action.triggered.connect(self.show_details)
        tools_menu.addAction(details_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def show_about(self):
        QMessageBox.about(self, "About Cloudless Provider", 
                         "Cloudless Provider Agent v1.0\n\nShare your computer resources and earn credits!")
    
    def show_profile(self):
        self.profile_dialog = UserProfileDialog(self)
        self.profile_dialog.exec_()
    
    def show_details(self):
        try:
            data = register_service.get_details()
            details_text = f"Credits: {data.get('credits', 'N/A')}\n"
            details_text += f"Status: {'Active' if self.is_running else 'Inactive'}\n"
            details_text += f"Network IP: {self.network_ip or 'Not connected'}\n"
            QMessageBox.information(self, "Account Details", details_text)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Could not fetch details: {str(e)}")
    
    def handle_logout(self):
        """Handle logout with proper cleanup"""
        # Stop sharing if active
        if self.is_running:
            self.stop_logic()
        
        # Clear saved credentials
        secrets_service.logout()
        
        # Call the original logout callback
        self.logout_callback()
    
    def load_initial_data(self):
        try:
            data = register_service.get_details()
            if 'credits' in data:
                self.credits = data['credits']
                # Initialize credits widget with current amount (no animation for initial load)
                self.credits_widget.current_credits = self.credits
                self.credits_widget.credits_label.setText(str(self.credits))
        except:
            pass
    
    def load_container_state(self):
        """Load container state on startup to restore UI state"""
        try:
            # Check if our spark worker container is running
            is_running = docker_runner_service.is_container_running("spark-worker-1")
            
            if is_running:
                # Container is running - restore the running state
                self.is_running = True
                self.btn_start.setChecked(True)
                self.btn_start.setText("Stop Sharing")
                self.network_widget.set_status("Online", "#4CAF50")
                
                # Try to get network IP from register service
                try:
                    data = register_service.get_details()
                    if 'network_ip' in data:
                        self.network_ip = data['network_ip']
                        self.network_widget.set_network_ip(self.network_ip)
                except:
                    self.network_widget.set_network_ip("Connected")
                
                # Set uptime
                uptime = docker_runner_service.get_container_uptime("spark-worker-1")
                self.network_widget.set_uptime(uptime)
                
                self.status_bar.showMessage("Resource sharing active (restored)")
                
                # Update activity log
                import datetime
                timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                containers = docker_runner_service.list_saved_containers()
                container_id = containers.get("spark-worker-1", "unknown")
                
                activity_text = f"🔄 [{timestamp}] Container state restored\n"
                activity_text += f"🐳 Container ID: {container_id}\n"
                activity_text += f"🌐 Status: Online\n"
                activity_text += f"💰 Current Credits: {self.credits}"
                self.activity_log.setText(activity_text)
                
            else:
                # Container not running - ensure UI is in stopped state
                self.is_running = False
                self.btn_start.setChecked(False)
                self.btn_start.setText("Start Sharing")
                self.network_widget.set_status("Offline", "#f44336")
                self.network_widget.set_network_ip("Not connected")
                self.network_widget.set_uptime("Not running")
                self.status_bar.showMessage("Ready")
                
                # Check if we have any saved containers that aren't running
                containers = docker_runner_service.list_saved_containers()
                if containers:
                    import datetime
                    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                    activity_text = f"ℹ️ [{timestamp}] Previous containers found but not running\n"
                    activity_text += f"💰 Current Credits: {self.credits}"
                    self.activity_log.setText(activity_text)
                else:
                    self.activity_log.setText("🔄 Waiting for activity...")
                    
        except Exception as e:
            print(f"Error loading container state: {e}")
            # Default to stopped state on error
            self.is_running = False
            self.btn_start.setChecked(False)
            self.btn_start.setText("Start Sharing")
            self.network_widget.set_status("Offline", "#f44336")
    
    def refresh_all_data(self):
        """Refresh both credits and container state"""
        self.load_initial_data()
        self.load_container_state()
    
    def update_uptime(self):
        """Update the running time display if container is running"""
        if self.is_running:
            try:
                uptime = docker_runner_service.get_container_uptime("spark-worker-1")
                self.network_widget.set_uptime(uptime)
            except Exception as e:
                print(f"Error updating uptime: {e}")
                # Check if container is still running
                if not docker_runner_service.is_container_running("spark-worker-1"):
                    # Container stopped unexpectedly
                    self.is_running = False
                    self.btn_start.setChecked(False)
                    self.btn_start.setText("Start Sharing")
                    self.network_widget.set_status("Offline", "#f44336")
                    self.network_widget.set_uptime("Not running")
                    self.status_bar.showMessage("Container stopped unexpectedly")
                    
                    import datetime
                    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
                    self.activity_log.setText(f"⚠️ [{timestamp}] Container stopped unexpectedly")
    
    def toggle_start_stop(self):
        if self.btn_start.isChecked():
            self.start_logic()
        else:
            self.stop_logic()

    def start_logic(self):
        self.show_operation_loading("Starting resource sharing...")
        
        # Create worker and thread for start operation
        self.thread = QThread()
        self.worker = ResourceWorker("start")
        self.worker.moveToThread(self.thread)
        
        # Connect signals
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.update_operation_progress)
        self.worker.finished.connect(self.on_start_success)
        self.worker.error.connect(self.on_start_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        self.thread.start()
    
    def show_operation_loading(self, message):
        self.btn_start.setEnabled(False)
        self.ram_spin.setEnabled(False)
        self.cores_spin.setEnabled(False)
        self.operation_loading.set_message(message)
        self.operation_loading.show()
        self.status_bar.showMessage(message)
    
    def hide_operation_loading(self):
        self.btn_start.setEnabled(True)
        self.ram_spin.setEnabled(True)
        self.cores_spin.setEnabled(True)
        self.operation_loading.hide()
    
    def update_operation_progress(self, message):
        self.operation_loading.set_message(message)
        self.status_bar.showMessage(message)
    
    def on_start_success(self, result):
        self.hide_operation_loading()
        self.is_running = True
        self.btn_start.setText("Stop Sharing")
        
        if 'network_ip' in result:
            self.network_ip = result['network_ip']
            self.network_widget.set_network_ip(self.network_ip)
        
        if 'credits' in result:
            self.credits = result['credits']
            self.credits_widget.set_credits(self.credits)
        
        self.network_widget.set_status("Online", "#4CAF50")
        self.network_widget.set_uptime("Starting...")
        self.status_bar.showMessage(f"Resource sharing active - Container {result.get('container_id', 'unknown')}")
        
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        activity_text = f"✅ [{timestamp}] Started sharing resources\n"
        activity_text += f"🐳 Container ID: {result.get('container_id', 'unknown')}\n"
        activity_text += f"🌐 Network IP: {self.network_ip}\n"
        activity_text += f"💰 Credits: {self.credits}"
        self.activity_log.setText(activity_text)
    
    def on_start_error(self, error_msg):
        self.hide_operation_loading()
        self.btn_start.setChecked(False)
        self.btn_start.setText("Start Sharing")
        self.status_bar.showMessage(f"Error: {error_msg}")
        
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.activity_log.setText(f"❌ [{timestamp}] Failed to start: {error_msg}")

    def stop_logic(self):
        self.show_operation_loading("Stopping resource sharing...")
        
        # Create worker and thread for stop operation
        self.stop_thread = QThread()
        self.stop_worker = ResourceWorker("stop")
        self.stop_worker.moveToThread(self.stop_thread)
        
        # Connect signals
        self.stop_thread.started.connect(self.stop_worker.run)
        self.stop_worker.progress.connect(self.update_operation_progress)
        self.stop_worker.finished.connect(self.on_stop_success)
        self.stop_worker.error.connect(self.on_stop_error)
        self.stop_worker.finished.connect(self.stop_thread.quit)
        self.stop_worker.finished.connect(self.stop_worker.deleteLater)
        self.stop_thread.finished.connect(self.stop_thread.deleteLater)
        
        self.stop_thread.start()
    
    def on_stop_success(self, result):
        self.hide_operation_loading()
        self.is_running = False
        self.btn_start.setText("Start Sharing")
        self.network_widget.set_status("Offline", "#f44336")
        self.network_widget.set_uptime("Not running")
        self.status_bar.showMessage("Resource sharing stopped")
        
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.activity_log.setText(f"🛑 [{timestamp}] Stopped sharing resources\n💰 Current Credits: {self.credits}")
    
    def on_stop_error(self, error_msg):
        self.hide_operation_loading()
        self.btn_start.setChecked(True)  # Keep it checked since stop failed
        self.btn_start.setText("Stop Sharing")
        self.status_bar.showMessage(f"Error stopping: {error_msg}")
        
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.activity_log.setText(f"❌ [{timestamp}] Failed to stop: {error_msg}")
    
    def cleanup_function(self):
        if self.is_running:
            pass
            # docker_runner_service.stop_and_remove()

# --- Legacy Resource Page (for compatibility) ---
class ResourcePage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        title = QLabel("Resource Allocation")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        form = QFormLayout()
        self.ram_spin = QSpinBox()
        self.ram_spin.setRange(1, 128)
        self.ram_spin.setSuffix(" GB")
        self.ram_spin.setValue(4)
        self.cores_spin = QSpinBox()
        self.cores_spin.setRange(1, 32)
        self.cores_spin.setValue(2)
        self.cores_spin.setSuffix(" Cores")
        form.addRow("RAM", self.ram_spin)
        form.addRow("Cores", self.cores_spin)
        layout.addLayout(form)
        self.btn_start = QPushButton("Start")
        self.btn_start.setCheckable(True)
        self.btn_start.clicked.connect(self.toggle_start_stop)
        layout.addWidget(self.btn_start)
        layout.addStretch()
        self.setLayout(layout)

    def toggle_start_stop(self):
        if self.btn_start.isChecked():
            self.btn_start.setText("Stop")
            self.start_logic()
        else:
            self.btn_start.setText("Start")
            self.stop_logic()

    def start_logic(self):
        data = register_service.register()
        if 'status' in data and data['status'] == "NEW_USER_REGISTERED":
            files_service.save_config("wg0.conf", data['conf'])
        network_ip = data['network_ip']
        container_id = docker_runner_service.run(
            image="spark-worker-vpn",
            container_name="spark-worker-1",
            port_map="8881:8881",
            env_vars={
                "SPARK_MASTER_IP": "10.10.0.1",
                "SPARK_LOCAL_IP": network_ip,
                "SPARK_LOCAL_HOSTNAME": network_ip
            },
            volume_map={
                files_service.get_config_path(): "/etc/wireguard"
            },
            additional_flags=["--cap-add=NET_ADMIN", "--device", "/dev/net/tun"]
        )
        print(f"Container {container_id} started running")

    def stop_logic(self):
        docker_runner_service.stop_and_remove()

# --- Main Application ---
class MainWindow(QStackedWidget):
    def __init__(self):
        super().__init__()
        # Main title at the top (easy to change)
        self.main_title = QLabel("Cloudless Provider Agent")
        self.main_title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        self.main_title.setAlignment(Qt.AlignCenter)
        self.main_title.setStyleSheet("color: #7ecfff; margin: 16px 0 8px 0;")

        self.login_page = LoginPage(self.show_register, self.show_main)
        self.register_page = RegisterPage(self.show_login)
        self.main_dashboard = MainDashboard(self.show_login)

        # Store access token for the session
        self.access_token = None

        # Wrap pages in a vertical layout with the main title
        self.page_container = QWidget()
        vbox = QVBoxLayout()
        vbox.addWidget(self.main_title)
        vbox.addWidget(self.login_page)
        vbox.setContentsMargins(16, 8, 16, 16)
        self.page_container.setLayout(vbox)

        super().addWidget(self.page_container)      # index 0 (login)
        super().addWidget(self.register_page)       # index 1
        super().addWidget(self.main_dashboard)      # index 2
        self.setCurrentIndex(0)
        self.setWindowTitle("Cloudless Provider Agent")
        self.resize(520, 420)
        self.setFont(QFont("Segoe UI", 11))

    def show_login(self):
        # Show login page with main title and resize for login
        self.page_container.layout().removeWidget(self.page_container.layout().itemAt(1).widget())
        self.page_container.layout().addWidget(self.login_page)
        self.setCurrentIndex(0)
        self.resize(520, 420)

    def show_register(self):
        self.setCurrentIndex(1)
        self.resize(520, 420)

    def show_main(self):
        self.setCurrentIndex(2)
        self.resize(900, 600)  # Expand window for dashboard
    
    def cleanup_function(self):
        if hasattr(self.main_dashboard, 'cleanup_function'):
            self.main_dashboard.cleanup_function()
        # docker_runner_service.stop_and_remove()

    def closeEvent(self, event):
        """This function is called when the window is closed"""
        print("Window is closing...")
        
        # Your cleanup code here
        self.cleanup_function()
        
        # Accept the close event (allow window to close)
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    set_dark_mode(app)
    window = MainWindow()
    
    window.show()
    
    # Center the window on screen after showing to ensure proper dimensions
    screen = app.primaryScreen().availableGeometry()
    window_geometry = window.frameGeometry()
    center_point = screen.center()
    window_geometry.moveCenter(center_point)
    window.move(window_geometry.topLeft())
    
    sys.exit(app.exec_())
