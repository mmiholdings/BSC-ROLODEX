from api.app.modules.filter_engine import qualifies
from api.app.modules.signal_engine import RawSignal


def test_filter_rejects_unpaid():
    signal = RawSignal(
        source='x',
        title='Need logo volunteer',
        body='unpaid work',
        author=None,
        url='https://example.com',
        created_at_source=None,
    )
    assert not qualifies(signal)
