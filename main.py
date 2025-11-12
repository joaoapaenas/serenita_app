import argparse
import logging
import os
import sys

from PySide6.QtGui import QFontDatabase, QFont
from PySide6.QtWidgets import QApplication

from app.core.context import AppContext
from app.core.database import SqliteConnectionFactory, get_db_file_path
from app.core.logger import setup_logging
from app.core.migrations import run_migrations
from app.core.simulation.seeder import seed_profile
from app.core.theme_manager import apply_theme
from app.features.main_window.main_controller import MainWindowController
from app.features.main_window.main_window_view import MainWindow
from app.features.welcome.welcome_controller import WelcomeController
from app.features.welcome.welcome_view import WelcomeView
from app.services.analytics_service import SqliteAnalyticsService
from app.services.cycle_service import SqliteCycleService
from app.services.cycle_subject_service import SqliteCycleSubjectService
from app.services.exam_service import SqliteExamService
from app.services.master_subject_service import SqliteMasterSubjectService
from app.services.performance_service import SqlitePerformanceService
from app.services.session_service import SqliteSessionService
from app.services.study_queue_service import SqliteStudyQueueService
from app.services.template_subject_service import SqliteTemplateSubjectService
from app.services.user_service import SqliteUserService
from app.services.work_unit_service import SqliteWorkUnitService

log = logging.getLogger(__name__)
BASE_PATH = os.path.dirname(os.path.abspath(__file__))


def check_for_pending_reset(base_path: str):
    """
    Checks for a reset flag file. If found, it deletes the database
    and the flag file itself before the application proceeds.
    """
    db_file = get_db_file_path(base_path)
    reset_flag_path = os.path.join(base_path, ".reset_on_next_boot")

    if os.path.exists(reset_flag_path):
        log.warning("Reset flag found. Deleting database file...")
        try:
            if os.path.exists(db_file):
                os.remove(db_file)
                log.info(f"Successfully deleted database file: {db_file}")

            os.remove(reset_flag_path)
            log.info("Reset flag removed. Application will start fresh.")

        except Exception as e:
            log.critical(f"Failed to perform pending reset: {e}", exc_info=True)
            sys.exit(1)


def main():
    """
    The main function that sets up and runs the application.
    """
    parser = argparse.ArgumentParser(description="Serenita Study App")
    parser.add_argument("--dev", action="store_true", help="Run in development mode with a seeded profile.")
    parser.add_argument("--user", type=str, help="User profile to seed for development mode (e.g., 'alex').")
    args = parser.parse_args()

    setup_logging()
    check_for_pending_reset(BASE_PATH)
    log.info("--- Serenita Application Starting Up ---")

    if args.dev and args.user:
        log.info(f"Running in DEV mode for user profile: {args.user}")
        profile_path = os.path.join(BASE_PATH, "tests", "fixtures", "profiles", f"{args.user}.json")
        if not os.path.exists(profile_path):
            log.critical(f"Profile file not found at {profile_path}. Exiting.")
            sys.exit(1)
        
        # Use a dedicated dev database for the user
        dev_db_path = os.path.join(BASE_PATH, "data", f"{args.user}.db")
        os.makedirs(os.path.dirname(dev_db_path), exist_ok=True)
        log.info(f"Seeding development database at: {dev_db_path}")
        seed_profile(profile_path, target=dev_db_path)
        conn_factory = SqliteConnectionFactory(dev_db_path)
    else:
        db_file = get_db_file_path(BASE_PATH)
        conn_factory = SqliteConnectionFactory(db_file)
        run_migrations(conn_factory, BASE_PATH)

    app = QApplication(sys.argv)

    assets_path = os.path.join(BASE_PATH, "app", "assets", "fonts")
    font_id = QFontDatabase.addApplicationFont(os.path.join(assets_path, "Geist.ttf"))
    if font_id != -1:
        font_families = QFontDatabase.applicationFontFamilies(font_id)
        if font_families:
            app_font = QFont(font_families[0], 10)
            app_font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
            app.setFont(app_font)
            log.info(f"Successfully loaded and set default font: {font_families[0]}")
    else:
        log.warning("Could not load 'Geist.ttf' font.")

    log.debug("Composing application services into AppContext...")
    app_context = AppContext(
        cycle_service=SqliteCycleService(conn_factory),
        session_service=SqliteSessionService(conn_factory),
        exam_service=SqliteExamService(conn_factory),
        user_service=SqliteUserService(conn_factory),
        performance_service=SqlitePerformanceService(conn_factory),
        analytics_service=SqliteAnalyticsService(conn_factory),
        master_subject_service=SqliteMasterSubjectService(conn_factory),
        cycle_subject_service=SqliteCycleSubjectService(conn_factory),
        study_queue_service=SqliteStudyQueueService(conn_factory),
        work_unit_service=SqliteWorkUnitService(conn_factory),
        template_subject_service=SqliteTemplateSubjectService(conn_factory),
        conn_factory=conn_factory
    )

    user = app_context.user_service.get_first_user()
    if not user:
        apply_theme(app, "Dark")
        welcome_view = WelcomeView()
        welcome_controller = WelcomeController(view=welcome_view, user_service=app_context.user_service)
        
        # Check if an existing user is found by the controller
        user = welcome_controller.run() 
        
        if not user: # If no user was found by the controller, show the dialog for creation
            welcome_view.exec()
            user = app_context.user_service.get_first_user() # Get the newly created user
            if not user:
                log.critical("User setup was cancelled or failed. Application cannot start.")
                sys.exit(0)

    apply_theme(app, user.theme)
    log.info(f"Application context initialized for user: '{user.name}' (ID: {user.id})")

    log.debug("Initializing main window and controller.")
    window = MainWindow()
    controller = MainWindowController(
        view=window,
        current_user=user,
        app_context=app_context,
        is_dev_mode=args.dev
    )

    window.show()
    log.info("Main window shown. Entering event loop.")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()