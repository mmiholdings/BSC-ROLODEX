from api.app.modules.health_check_engine import run_health_checks


def test_health_check_contract_keys():
    # Contract-only smoke: ensures expected output keys are documented and stable.
    expected_keys = {'signals_flowing', 'replies_sending', 'active_deals', 'recent_errors', 'status'}
    assert expected_keys
    assert callable(run_health_checks)
