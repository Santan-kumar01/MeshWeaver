import time

from meshweaver.heartbeat import HeartbeatMonitor


def test_peer_is_alive_after_registration():
    monitor = HeartbeatMonitor(timeout=10)

    monitor.register_peer("peer-1")

    assert monitor.is_alive("peer-1") is True


def test_heartbeat_updates_peer():
    monitor = HeartbeatMonitor(timeout=10)

    monitor.register_peer("peer-1")

    old_time = monitor.peers["peer-1"].last_seen

    time.sleep(0.01)

    monitor.heartbeat("peer-1")

    new_time = monitor.peers["peer-1"].last_seen

    assert new_time > old_time
    assert monitor.is_alive("peer-1") is True


def test_failed_peer_is_detected():
    monitor = HeartbeatMonitor(timeout=0.05)

    monitor.register_peer("peer-1")

    time.sleep(0.1)

    failed = monitor.get_failed_peers()

    assert "peer-1" in failed
    assert monitor.is_alive("peer-1") is False


def test_heartbeat_removes_peer():
    monitor = HeartbeatMonitor(timeout=10)

    monitor.register_peer("peer-1")

    assert monitor.remove_peer("peer-1") is True
    assert monitor.is_alive("peer-1") is False


def test_unknown_peer_is_not_alive():
    monitor = HeartbeatMonitor()

    assert monitor.is_alive("unknown-peer") is False