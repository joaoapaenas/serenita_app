import json
from datetime import datetime
from app.services.analytics_service import SqliteAnalyticsService
from app.core.database import SqliteConnectionFactory

def test_daily_performance_calculation(seeded_engine):
    """
    Given a seeded database engine from a known user profile,
    When the analytics service calculates daily performance,
    Then the results should match the aggregates from the source profile.
    """
    profile_name, engine = seeded_engine
    # 1. Arrange: Instantiate the service with our test engine.
    # We mock the connection factory to return connections from our in-memory engine.
    class MockConnectionFactory(SqliteConnectionFactory):
        def get_connection(self):
            return engine.connect()
    analytics_service = SqliteAnalyticsService(MockConnectionFactory(db_path=":memory:"))
    # In a real scenario, we would query the DB for the cycle_id created by the seeder.
    # For simplicity, we assume it's the first one.
    cycle_id = 1

    # 2. Act: Call the method under test.
    daily_data = analytics_service.get_daily_performance(cycle_id=cycle_id)
    # 3. Assert: Verify the output against the source JSON data.
    with open(f"tests/fixtures/profiles/{profile_name}.json") as f:
        profile = json.load(f)
    # Group questions by date from the profile to get expected results
    expected_perf = {}
    for session in profile['cycle']['sessions']:
        date_key = datetime.fromisoformat(session['start_time']).strftime('%Y-%m-%d')
        if date_key not in expected_perf:
            expected_perf[date_key] = {'total': 0, 'correct': 0}

        expected_perf[date_key]['total'] += len(session['questions'])
        expected_perf[date_key]['correct'] += sum(1 for q in session['questions'] if q['is_correct'])
    assert len(daily_data) == len(expected_perf)
    for perf_day in daily_data:
        assert perf_day.date in expected_perf
        assert perf_day.questions_done == expected_perf[perf_day.date]['total']
        assert perf_day.questions_correct == expected_perf[perf_day.date]['correct']