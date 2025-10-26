from datetime import timezone

from autotrade.core.clock import now


def test_now_returns_aware_timestamps():
    snapshot = now()

    assert snapshot.utc.tzinfo == timezone.utc
    assert snapshot.kst.tzinfo is not None
    assert snapshot.kst.utcoffset() is not None
    assert snapshot.kst.utcoffset().total_seconds() == 9 * 3600
    # Ensure the two timestamps represent the same instant
    assert snapshot.utc.timestamp() == snapshot.kst.timestamp()
