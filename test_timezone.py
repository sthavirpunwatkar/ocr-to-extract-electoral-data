from datetime import datetime, timezone

naive = datetime.fromisoformat("2023-10-27T14:30:00.123456")
aware = datetime.now(timezone.utc)

try:
    print(f"Naive: {naive}")
    print(f"Aware: {aware}")
    print(naive > aware)
except TypeError as e:
    print(f"Error: {e}")
