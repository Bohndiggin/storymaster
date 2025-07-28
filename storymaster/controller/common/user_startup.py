"""
User startup utilities for ensuring a user exists on application startup.
"""

from PyQt6.QtWidgets import QMessageBox, QInputDialog, QApplication

from storymaster.model.common.common_model import BaseModel
from storymaster.view.common.new_user_dialog import NewUserDialog
from storymaster.view.common.new_setting_dialog import NewSettingDialog
from storymaster.view.common.new_storyline_dialog import NewStorylineDialog


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
    Creates the first user using a dialog and guides them through initial setup.
    Returns True if successful, False if cancelled.
    """
    # Show information dialog first
    QMessageBox.information(
        None,
        "Welcome to Storymaster",
        "Welcome to Storymaster! Since this is your first time using the application, "
        "we'll guide you through creating your user profile and first project.\n\n"
        "Let's start by creating your user account.",
    )

    # Step 1: Create User
    dialog = NewUserDialog(model)
    user_data = dialog.get_user_data()

    if not user_data:
        return False  # User cancelled

    try:
        new_user = model.create_user(user_data["username"])
        QMessageBox.information(
            None,
            "User Created",
            f"Great! Welcome, {new_user.username}!\n\n"
            "Now let's create your first setting (world) for your stories.",
        )
    except Exception as e:
        QMessageBox.critical(
            None, "Error Creating User", f"Failed to create user: {str(e)}"
        )
        return False

    # Step 2: Create Setting
    # Create a model with the new user ID for the dialogs
    user_model = BaseModel(new_user.id)

    setting_dialog = NewSettingDialog(user_model)
    setting_dialog.user_combo.setCurrentText(
        new_user.username
    )  # Pre-select the new user
    setting_dialog.user_combo.setEnabled(False)  # Don't let them change it
    setting_dialog.name_line_edit.setText("My First World")  # Provide a default name

    setting_data = setting_dialog.get_setting_data()

    if not setting_data:
        QMessageBox.information(
            None,
            "Setup Incomplete",
            "You can create a setting later from the Setting menu. "
            "Your user account has been created successfully.",
        )
        return True

    try:
        user_model.add_row("setting", setting_data)

        # Get the newly created setting
        settings = user_model.get_all_settings()
        new_setting = next(
            (s for s in settings if s.name == setting_data["name"]), None
        )

        if not new_setting:
            raise ValueError("Failed to retrieve newly created setting")

        QMessageBox.information(
            None,
            "Setting Created",
            f"Excellent! Your setting '{new_setting.name}' has been created.\n\n"
            "Now let's create your first storyline.",
        )
    except Exception as e:
        QMessageBox.critical(
            None, "Error Creating Setting", f"Failed to create setting: {str(e)}"
        )
        return True  # User is still created, just continue

    # Step 3: Create Storyline
    storyline_dialog = NewStorylineDialog(user_model)
    storyline_dialog.user_combo.setCurrentText(
        new_user.username
    )  # Pre-select the new user
    storyline_dialog.user_combo.setEnabled(False)  # Don't let them change it
    storyline_dialog.name_line_edit.setText("My First Story")  # Provide a default name

    storyline_data = storyline_dialog.get_storyline_data()

    if not storyline_data:
        QMessageBox.information(
            None,
            "Setup Incomplete",
            "You can create a storyline later from the Storyline menu. "
            "Your user account and setting have been created successfully.",
        )
        return True

    try:
        user_model.add_row("storyline", storyline_data)

        # Get the newly created storyline
        storylines = user_model.get_all_storylines()
        new_storyline = next(
            (s for s in storylines if s.name == storyline_data["name"]), None
        )

        if not new_storyline:
            raise ValueError("Failed to retrieve newly created storyline")

        # Create the storyline-to-setting relationship
        user_model.add_row(
            "storyline_to_setting",
            {"storyline_id": new_storyline.id, "setting_id": new_setting.id},
        )

        # Step 4: Create Initial Plot
        try:
            user_model.add_row(
                "litography_plot",
                {
                    "title": "Main Plot",
                    "description": "The main storyline",
                    "storyline_id": new_storyline.id,
                },
            )

            # For the success message, we don't need to retrieve the plot
            plot_title = "Main Plot"

            QMessageBox.information(
                None,
                "Setup Complete!",
                f"Perfect! Your setup is complete:\n\n"
                f"• User: {new_user.username}\n"
                f"• Setting: {new_setting.name}\n"
                f"• Storyline: {new_storyline.name}\n"
                f"• Plot: {plot_title}\n\n"
                f"You're all ready to start creating your story!",
            )
        except Exception as e:
            QMessageBox.information(
                None,
                "Almost Complete!",
                f"Your setup is mostly complete:\n\n"
                f"• User: {new_user.username}\n"
                f"• Setting: {new_setting.name}\n"
                f"• Storyline: {new_storyline.name}\n\n"
                f"You can create plots from the Storyline menu.",
            )

    except Exception as e:
        QMessageBox.critical(
            None, "Error Creating Storyline", f"Failed to create storyline: {str(e)}"
        )

    return True


def get_startup_user_id() -> int:
    """
    Gets the user ID to use for application startup.
    This is the main function to call from main.py
    """
    return ensure_user_exists()
