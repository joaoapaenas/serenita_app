# tests/features/main_window/test_navigator.py
import pytest
from unittest.mock import MagicMock

from app.features.main_window.navigator import Navigator


@pytest.fixture
def mock_main_controller(mocker):
    """Creates a mock main controller with all necessary sub-managers and services."""
    controller = MagicMock()

    # Mock nested managers
    controller.view_controller_factory = MagicMock()
    controller.session_manager = MagicMock()
    controller.plan_manager = MagicMock()

    # Patch the actual method on the class
    mocker.patch('app.features.main_window.main_window_view.MainWindow.set_main_pane_widget')

    # Create a MagicMock for the view, which will now have the patched method
    from app.features.main_window.main_window_view import MainWindow
    controller.view = MagicMock(spec=MainWindow)

    # The navigator is the class under test
    controller.navigator = Navigator(controller)
    return controller


@pytest.mark.skip(reason="UI tests require QApplication setup")
def test_navigator_show_overview_with_active_cycle_and_plan(mock_main_controller, mocker):
    """Test showing overview when a plan is cached."""
    # Arrange
    mock_main_controller.navigator.active_cycle = True
    mock_main_controller.session_manager.is_session_active.return_value = False

    # Simulate a cached plan being available
    cached_plan = {"meta": {"human_factor_input": {}}}
    mock_main_controller.plan_manager.get_cached_plan.return_value = cached_plan

    # Mock the show_dual_plan_view method on the navigator instance
    mocker.patch.object(mock_main_controller.navigator, 'show_dual_plan_view')

    # Act
    mock_main_controller.navigator.show_overview()

    # Assert
    # It should not regenerate the plan
    mock_main_controller.plan_manager.regenerate_plan.assert_not_called()
    # It should call the factory to create the dual plan view
    mock_main_controller.navigator.show_dual_plan_view.assert_called_once_with(cached_plan)


@pytest.mark.skip(reason="UI tests require QApplication setup")
def test_navigator_show_overview_with_active_cycle_no_plan(mock_main_controller, mocker):
    """Test showing overview when no plan is cached, forcing regeneration."""
    # Arrange
    mock_main_controller.navigator.active_cycle = True
    mock_main_controller.session_manager.is_session_active.return_value = False

    # No cached plan
    mock_main_controller.plan_manager.get_cached_plan.return_value = None

    # Mock the show_dual_plan_view method on the navigator instance
    mocker.patch.object(mock_main_controller.navigator, 'show_dual_plan_view')

    # Act
    mock_main_controller.navigator.show_overview()

    # Assert
    # It MUST call for a plan regeneration
    mock_main_controller.plan_manager.regenerate_plan.assert_called_once()
    # It should not try to show the plan view directly
    mock_main_controller.navigator.show_dual_plan_view.assert_not_called()


@pytest.mark.skip(reason="UI tests require QApplication setup")
def test_navigator_show_overview_no_active_cycle(mock_main_controller, mocker):
    """Test showing the empty dashboard when no cycle is active."""
    # Arrange
    mock_main_controller.navigator.active_cycle = None
    mock_main_controller.session_manager.is_session_active.return_value = False

    # Explicitly mock set_main_pane_widget on the mock view instance
    mocker.patch.object(mock_main_controller.view, 'set_main_pane_widget')

    # Act
    mock_main_controller.navigator.show_overview()

    # Assert
    # It should directly set the main widget, not via a factory method in this test setup
    # We just need to know that *some* widget was set.
    from app.features.main_window.components.empty_dashboard_widget import EmptyDashboardWidget
    mock_main_controller.view.set_main_pane_widget.assert_called_once()
    widget_arg = mock_main_controller.view.set_main_pane_widget.call_args[0][0]

    # Check that the widget passed is the EmptyDashboardWidget
    assert isinstance(widget_arg, EmptyDashboardWidget)


@pytest.mark.skip(reason="UI tests require QApplication setup")
def test_navigator_redirects_to_session_if_active(mock_main_controller):
    """Test that any navigation attempt redirects to the session view if a session is active."""
    # Arrange
    mock_main_controller.session_manager.is_session_active.return_value = True
    mock_session_view = MagicMock()
    mock_main_controller.session_manager.session_view = mock_session_view

    # Act: Try to navigate to "configurations"
    mock_main_controller.navigator.handle_navigation({"type": "configurations"})

    # Assert
    # It should NOT create the configurations view
    mock_main_controller.view_controller_factory.create_configurations_landing.assert_not_called()
    # It SHOULD show the active session view
    mock_main_controller.view.set_main_pane_widget.assert_called_once_with(mock_session_view)