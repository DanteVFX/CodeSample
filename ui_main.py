""" Configuration for the Login UI for ActionVFX.

This module contains the configuration for the login UI for ActionVFX. It
includes the imports for the necessary modules, the class definition for the
ActionVFXLoginUI, and the function to show the login window.
"""

# Standard modules
import os
import json

# Third-party modules
import nuke
from PySide2 import QtWidgets, QtGui, QtCore

# Local modules
from api.auth import authenticate, load_session, save_session, SESSION_FILE
from ui.ui_container_base import ImageGridWidget, FreeFootageWidget
from ui.ui_container_base import OwnershipWidget
from ui.ui_items_detail import ItemDetailWidget

from ui.ui_items_detail_freefootage import FreeFootageDetailWidget

from ui.ui_items_detail import FreeFootageDetailWidget, Collection_DetailWidget, OwnershipDetailWidget

# Constants for the login UI
# File to store the authentication token
TOKEN_FILE = os.path.join(os.path.expanduser("~"), ".actionvfx_token.json")
# Path to the logo image
image_path = os.path.join(os.path.dirname(os.path.dirname(
    __file__)), "assets", "img", "logo_01.png")

# Global variables
ACTIONVFX_URL = "https://www.actionvfx.com/"
login_window = None
dashboard_window = None


class ActionVFXLoginUI(QtWidgets.QWidget):
    def __init__(self):
        super(ActionVFXLoginUI, self).__init__()
        self.setWindowTitle("ActionVFX Login")
        self.setFixedSize(350, 300)
        self.init_ui()
        self.check_existing_token()

    def init_ui(self):
        """Initialize the user interface."""
        layout = QtWidgets.QVBoxLayout()

        # ActionVFX logo
        self.logo_ActionVFX = QtWidgets.QLabel()
        self.logo_ActionVFX.setPixmap(QtGui.QPixmap(image_path))
        layout.addWidget(self.logo_ActionVFX)

        # Email input field
        self.email_label = QtWidgets.QLabel("Email:")
        self.email_input = QtWidgets.QLineEdit()
        self.email_input.setPlaceholderText("Enter your email")
        layout.addWidget(self.email_label)
        layout.addWidget(self.email_input)

        # Password input field
        self.password_label = QtWidgets.QLabel("Password:")
        self.password_input = QtWidgets.QLineEdit()
        self.password_input.setPlaceholderText("Enter your password")
        self.password_input.setEchoMode(QtWidgets.QLineEdit.Password)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)

        # Forgot password link
        self.forgot_password = QtWidgets.QLabel(
            "<a href='https://www.actionvfx.com/users/reset'>Forgot Password?</a>")
        self.forgot_password.setOpenExternalLinks(True)
        self.forgot_password.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)

        layout.addWidget(self.forgot_password)

        # Login button
        self.login_button = QtWidgets.QPushButton("Login")
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)

        # Remember me checkbox
        self.remember_checkbox = QtWidgets.QCheckBox("Remember me")
        self.remember_checkbox.setChecked(True)
        layout.addWidget(self.remember_checkbox)

        # Set layout
        self.setLayout(layout)

    def check_existing_token(self):
        """Check if a saved authentication token exists and auto-login if valid."""
        if os.path.exists(TOKEN_FILE):
            try:
                with open(TOKEN_FILE, "r") as file:
                    user_session = json.load(file)
                if "Authorization" in user_session:
                    self.open_dashboard(user_session)  # Auto-login
            except Exception as e:
                print(f"Error loading token: {e}")

    def login(self):
        """Handle user login."""
        email = self.email_input.text()
        password = self.password_input.text()

        if not email or not password:
            self.show_error("Please enter your email and password.")
            return

        try:
            # Autenticar al usuario
            user_session = authenticate(email, password)
            if not user_session:
                self.show_error("Invalid email or password.")
                return

            # Save session with token
            if self.remember_checkbox.isChecked():
                save_session(user_session, user_session["Authorization"])

            else:
                pass

            # Open dashboard
            self.open_dashboard(user_session)

        except ValueError as e:
            self.show_error(f"Login error: {str(e)}")
        except Exception as e:
            self.show_error(f"Unexpected error: {str(e)}")

    def show_error(self, message):
        """Display an error message to the user."""
        error_dialog = QtWidgets.QMessageBox(self)
        error_dialog.setIcon(QtWidgets.QMessageBox.Critical)
        error_dialog.setWindowTitle("Error")
        error_dialog.setText(message)
        error_dialog.exec_()

    def open_dashboard(self, user_session):
        """Open the dashboard window and close the login UI."""
        self.board = DashboardWindow(user_session)
        self.board.show()
        self.close()


class DashboardWindow(QtWidgets.QMainWindow):
    def __init__(self, user_session):
        super(DashboardWindow, self).__init__()
        self.setWindowTitle("ActionVFX Dashboard - Nuke Plugin")
        self.setFixedSize(1200, 800)

        self.current_widget = None
        self.previous_widget = None

        self.setup_ui(user_session)

    def setup_ui(self, user_session):
        """Set up the UI for the dashboard window."""
        # --- Central Widget Layout ---
        central_widget = QtWidgets.QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QHBoxLayout(central_widget)

        # --- LEFT PANEL ---
        left_panel = QtWidgets.QVBoxLayout()

        # Title
        self.title = QtWidgets.QLabel("Dashboard")
        self.title.setFont(QtGui.QFont(
            "Bahnschrift SemiBold SemiConden", 20, QtGui.QFont.Bold))
        self.title.setStyleSheet("color: #FFFFFF;")
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        left_panel.addWidget(self.title)

        # Logo
        self.logo_ActionVFX = QtWidgets.QLabel()
        self.logo_ActionVFX.setPixmap(QtGui.QPixmap(image_path))
        self.logo_ActionVFX.setMaximumSize(260, 120)
        self.logo_ActionVFX.setScaledContents(True)
        left_panel.addWidget(self.logo_ActionVFX)

        # Separator
        for _ in range(2):
            separator = QtWidgets.QFrame()
            separator.setFrameShape(QtWidgets.QFrame.HLine)
            separator.setFrameShadow(QtWidgets.QFrame.Sunken)
            left_panel.addWidget(separator)

        # User info
        self.user_name = QtWidgets.QLabel(
            f"User : {user_session.get('username', 'Unknown')}")
        self.user_name.setAlignment(QtCore.Qt.AlignCenter)
        left_panel.addWidget(self.user_name)

        subscription_type = "Free" if user_session.get(
            "Status", True) else "Premium"
        self.subscription_label = QtWidgets.QLabel(
            f"Subscription : {subscription_type}")
        self.subscription_label.setAlignment(QtCore.Qt.AlignCenter)
        left_panel.addWidget(self.subscription_label)

        # Buttons
        buttons_style = """
            QPushButton {
                background-color: #3ad1ff;
                color: white;
                border: solid;
                padding: 6px;
                border-radius: 2px;
            }
            QPushButton:hover {
                background-color: #288ead;
            }
            QPushButton:pressed {
                background-color: #124351;
            }
        """

        self.create_button_2D = QtWidgets.QPushButton("2D")
        self.create_button_2D.setStyleSheet(buttons_style)
        self.create_button_2D.clicked.connect(self.show_2d_elements)
        left_panel.addWidget(self.create_button_2D)

        self.create_button_freefootage = QtWidgets.QPushButton("FreeFootage")
        self.create_button_freefootage.setStyleSheet(buttons_style)
        self.create_button_freefootage.clicked.connect(
            self.show_freefootage_elements)
        left_panel.addWidget(self.create_button_freefootage)

        self.create_ownership = QtWidgets.QPushButton("MyDownloads")
        self.create_ownership.setStyleSheet(buttons_style)
        self.create_ownership.clicked.connect(self.show_ownership_elements)
        left_panel.addWidget(self.create_ownership)

        # Spacer
        left_panel.addStretch()

        # Download path field
        self.path_input = QtWidgets.QLineEdit()
        self.path_input.setPlaceholderText("Enter path")
        left_panel.addWidget(self.path_input)

        # Download button
        self.create_button_download = QtWidgets.QPushButton("Download")
        self.create_button_download.setStyleSheet(buttons_style)
        self.create_button_download.clicked.connect(self.download)
        left_panel.addWidget(self.create_button_download)

        # --- RIGHT PANEL ---
        right_panel = QtWidgets.QVBoxLayout()

        top_row = QtWidgets.QHBoxLayout()
        top_row.addStretch()
        self.logout_button = QtWidgets.QPushButton("Logout")
        self.logout_button.clicked.connect(self.logout)
        top_row.addWidget(self.logout_button)
        right_panel.addLayout(top_row)

        # Widgets container
        self.widget_container = QtWidgets.QWidget()
        container_layout = QtWidgets.QVBoxLayout(self.widget_container)

        self.grid_2d_elements = ImageGridWidget()
        self.grid_freefootage_elements = FreeFootageWidget()
        self.grid_ownership_elements = OwnershipWidget()

        self.detail_widget_freefootage = FreeFootageDetailWidget()
        self.detail_widget_2d = Collection_DetailWidget()
        self.detail_widget_ownership = OwnershipDetailWidget()

        self.grid_2d_elements.itemSelected.connect(self.show_item_detail)
        self.grid_freefootage_elements.itemSelected.connect(
            self.show_item_detail)
        self.grid_ownership_elements.itemSelected.connect(
            self.show_item_detail)

        self.detail_widget_freefootage.back_button.clicked.connect(
            self.go_back)
        self.detail_widget_2d.back_button.clicked.connect(self.go_back)
        self.detail_widget_ownership.back_button.clicked.connect(self.go_back)

        container_layout.addWidget(self.grid_2d_elements)
        container_layout.addWidget(self.grid_freefootage_elements)
        container_layout.addWidget(self.grid_ownership_elements)
        container_layout.addWidget(self.detail_widget_freefootage)
        container_layout.addWidget(self.detail_widget_2d)
        container_layout.addWidget(self.detail_widget_ownership)

        self.grid_freefootage_elements.hide()
        self.grid_ownership_elements.hide()
        self.detail_widget_freefootage.hide()
        self.detail_widget_2d.hide()
        self.detail_widget_ownership.hide()

        self.current_widget = self.grid_2d_elements

        right_panel.addWidget(self.widget_container, 1)

        # Vertical Separator
        vertical_separator = QtWidgets.QFrame()
        vertical_separator.setFrameShape(QtWidgets.QFrame.VLine)
        vertical_separator.setFrameShadow(QtWidgets.QFrame.Sunken)

        # Assemble final layout
        main_layout.addLayout(left_panel, 1)
        main_layout.addWidget(vertical_separator)
        main_layout.addLayout(right_panel, 4)

    def show_2d_elements(self):
        self.switch_widget(self.grid_2d_elements)

    def show_freefootage_elements(self):
        self.switch_widget(self.grid_freefootage_elements)

    def show_ownership_elements(self):
        self.switch_widget(self.grid_ownership_elements)

    def switch_widget(self, new_widget):
        if self.current_widget:
            self.current_widget.hide()
        new_widget.show()
        self.current_widget = new_widget

    def detail_widget_for_current_type(self):
        if self.current_widget == self.grid_freefootage_elements:
            return self.detail_widget_free
        elif self.current_widget == self.grid_ownership_elements:
            return self.detail_widget_ownership
        elif self.current_widget == self.grid_2d_elements:
            return self.detail_widget_2d
        return None

    def show_item_detail(self, item):
        self.previous_widget = self.current_widget

        if self.current_widget == self.grid_freefootage_elements:
            scene_id = item.get("id")
            if scene_id:
                self.detail_widget_free.load_scene(scene_id)
            else:
                print("[⚠️]No Id found in item")

        elif self.current_widget == self.grid_ownership_elements or self.current_widget == self.grid_2d_elements:
            item_id = item.get("id")
            if item_id:
                detail_widget = self.detail_widget_for_current_type()
                if detail_widget:
                    detail_widget.load_item_by_slug(
                        item_id, item_type="collection_by_id")
            else:
                print("[⚠️] No Id found in item")

        # Cambiar vista al detalle correspondiente
        self.switch_widget(self.detail_widget_for_current_type())

    def go_back(self):
        if hasattr(self, 'previous_widget') and self.previous_widget:
            self.switch_widget(self.previous_widget)

    def download(self):

        nuke.message("Downloading...")

    def logout(self):
        """Logout and return to login screen."""
        global login_window, dashboard_window

        # Delete the saved session
        if os.path.exists(SESSION_FILE):
            os.remove(SESSION_FILE)

        # Close dashboard window
        if dashboard_window:
            dashboard_window.close()
            dashboard_window.deleteLater()
            dashboard_window = None

        # Show login window
        show_login()


def show_login():
    """Show the login window."""
    global login_window, dashboard_window

    # Close existing windows
    if login_window:
        login_window.close()
        login_window.deleteLater()
        login_window = None

    if dashboard_window:
        dashboard_window.close()
        dashboard_window.deleteLater()
        dashboard_window = None

    # Check if there is a saved session
    user_session = load_session()
    if user_session:
        # Auto-login if there is a saved session
        dashboard_window = DashboardWindow(user_session)
        dashboard_window.show()
        return

    # If there is no saved session, show the login window
    login_window = ActionVFXLoginUI()
    login_window.show()
