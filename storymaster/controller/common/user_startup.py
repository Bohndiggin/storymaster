"""
User startup utilities for ensuring a user exists on application startup.
"""

from PyQt6.QtWidgets import QMessageBox, QInputDialog, QApplication

from storymaster.model.common.common_model import BaseModel
from storymaster.view.common.new_user_dialog import NewUserDialog


def ensure_user_exists(model: BaseModel = None) -> int:
    """
    Ensures at least one user exists in the database.
    If no users exist, prompts the user to create one.
    Returns the ID of the user to use.
    """
    if model is None:
        # Create a temporary model just to check users
        try:
            temp_model = BaseModel(1)  # User ID doesn't matter for checking users
        except Exception:
            # If we can't even create a model, we have bigger problems
            QMessageBox.critical(
                None,
                "Database Error",
                "Could not connect to the database. Please check your setup.",
            )
            QApplication.quit()
            return 1
    else:
        temp_model = model

    try:
        users = temp_model.get_all_users()

        if not users:
            # No users exist, need to create one
            success = create_first_user(temp_model)
            if not success:
                QMessageBox.critical(
                    None,
                    "Startup Error",
                    "Cannot start the application without a user. Exiting.",
                )
                QApplication.quit()
                return 1

            # Get the newly created user
            users = temp_model.get_all_users()
            if users:
                return users[0].id
            else:
                # This shouldn't happen
                return 1
        else:
            # Users exist, return the first one for now
            # In a future update, we could remember the last used user
            return users[0].id

    except Exception as e:
        QMessageBox.critical(None, "Database Error", f"Error checking users: {str(e)}")
        QApplication.quit()
        return 1


def create_first_user(model: BaseModel) -> bool:
    """
    Creates the first user using a dialog.
    Returns True if successful, False if cancelled.
    """
    # Show information dialog first
    QMessageBox.information(
        None,
        "Welcome to Storymaster",
        "Welcome to Storymaster! Since this is your first time using the application, "
        "you need to create a user profile to organize your storylines and settings.\n\n"
        "Please create your first user account.",
    )

    # Show new user dialog
    dialog = NewUserDialog(model)
    user_data = dialog.get_user_data()

    if user_data:
        try:
            new_user = model.create_user(user_data["username"])
            QMessageBox.information(
                None,
                "User Created",
                f"Welcome, {new_user.username}! Your user account has been created successfully.",
            )
            return True
        except Exception as e:
            QMessageBox.critical(
                None, "Error Creating User", f"Failed to create user: {str(e)}"
            )
            return False
    else:
        # User cancelled
        return False


def get_startup_user_id() -> int:
    """
    Gets the user ID to use for application startup.
    This is the main function to call from main.py
    """
    return ensure_user_exists()
