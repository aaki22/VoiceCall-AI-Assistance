from src.schema.call import CallSession, CallTurn


def test_call_schema_table_names():
    assert CallSession.__tablename__ == "call_sessions"
    assert CallTurn.__tablename__ == "call_turns"
