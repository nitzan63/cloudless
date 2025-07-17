import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QStackedWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFormLayout, QSpinBox, QToolButton
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon

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
            padding: 10px 14px;
            border: 1px solid #444;
            background: #232323;
            color: #fff;
            font-size: 16px;
        }
    """)
    le.setMinimumWidth(240)
    le.setMaximumWidth(420)
    if password:
        le.setEchoMode(QLineEdit.Password)
    return le

# --- Login Page ---
class LoginPage(QWidget):
    def __init__(self, switch_to_register, switch_to_main):
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        title = QLabel("Login")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        self.username = rounded_line_edit()
        self.username.setPlaceholderText("Username")
        self.password = rounded_line_edit(password=True)
        self.password.setPlaceholderText("Password")
        # Center fields with margins
        field_box = QVBoxLayout()
        field_box.setAlignment(Qt.AlignCenter)
        field_box.setContentsMargins(32, 8, 32, 8)
        field_box.addWidget(self.username)
        field_box.addWidget(self.password)
        field_box.setSpacing(18)
        layout.addLayout(field_box)
        btn_login = QPushButton("Login")
        btn_login.clicked.connect(switch_to_main)
        btn_register = QPushButton("Register")
        btn_register.clicked.connect(switch_to_register)
        btn_row = QHBoxLayout()
        btn_row.setAlignment(Qt.AlignCenter)
        btn_row.addWidget(btn_login)
        btn_row.addWidget(btn_register)
        layout.addLayout(btn_row)
        layout.addStretch()
        self.setLayout(layout)

# --- Register Page ---
class RegisterPage(QWidget):
    def __init__(self, switch_to_login):
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        title = QLabel("Register")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        self.username = rounded_line_edit()
        self.username.setPlaceholderText("Username")
        self.password = rounded_line_edit(password=True)
        self.password.setPlaceholderText("Password")
        self.confirm_password = rounded_line_edit(password=True)
        self.confirm_password.setPlaceholderText("Confirm Password")
        field_box = QVBoxLayout()
        field_box.setAlignment(Qt.AlignCenter)
        field_box.setContentsMargins(32, 8, 32, 8)
        field_box.addWidget(self.username)
        field_box.addWidget(self.password)
        field_box.addWidget(self.confirm_password)
        field_box.setSpacing(18)
        layout.addLayout(field_box)
        btn_register = QPushButton("Register")
        btn_register.clicked.connect(lambda: switch_to_login())
        btn_back = QPushButton("Back to Login")
        btn_back.clicked.connect(lambda: switch_to_login())
        btn_row = QHBoxLayout()
        btn_row.setAlignment(Qt.AlignCenter)
        btn_row.addWidget(btn_register)
        btn_row.addWidget(btn_back)
        layout.addLayout(btn_row)
        layout.addStretch()
        self.setLayout(layout)

# --- Main Resource Page ---
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
        # Placeholder for starting logic
        pass

    def stop_logic(self):
        # Placeholder for stopping logic
        pass

# --- Main Application ---
class MainWindow(QStackedWidget):
    def __init__(self):
        super().__init__()
        # Main title at the top (easy to change)
        self.main_title = QLabel("Cloudless Provider Agent (Change Me)")
        self.main_title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        self.main_title.setAlignment(Qt.AlignCenter)
        self.main_title.setStyleSheet("color: #7ecfff; margin: 16px 0 8px 0;")

        self.login_page = LoginPage(self.show_register, self.show_main)
        self.register_page = RegisterPage(self.show_login)
        self.resource_page = ResourcePage()

        # Wrap pages in a vertical layout with the main title
        self.page_container = QWidget()
        vbox = QVBoxLayout()
        vbox.addWidget(self.main_title)
        vbox.addWidget(self.login_page)
        vbox.setContentsMargins(16, 8, 16, 16)
        self.page_container.setLayout(vbox)

        super().addWidget(self.page_container)      # index 0 (login)
        super().addWidget(self.register_page)       # index 1
        super().addWidget(self.resource_page)       # index 2
        self.setCurrentIndex(0)
        self.setWindowTitle("Cloudless Provider Agent")
        self.resize(520, 420)
        self.setFont(QFont("Segoe UI", 11))

    def show_login(self):
        # Show login page with main title
        self.page_container.layout().removeWidget(self.page_container.layout().itemAt(1).widget())
        self.page_container.layout().addWidget(self.login_page)
        self.setCurrentIndex(0)

    def show_register(self):
        self.setCurrentIndex(1)

    def show_main(self):
        self.setCurrentIndex(2)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    set_dark_mode(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
