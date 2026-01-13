from kafka import KafkaConsumer
import json
import statistics
from collections import defaultdict

# -------------------------
# Kafka Configuration
# -------------------------
KAFKA_BROKER = "localhost:9092"
TOPIC = "dbserver1.public.transactions"

consumer = KafkaConsumer(
    TOPIC,
    bootstrap_servers=[KAFKA_BROKER],
    auto_offset_reset="latest",
    enable_auto_commit=True,
    group_id="fraud-agent-1",
    value_deserializer=lambda x: json.loads(x.decode("utf-8"))
)

# -------------------------
# In-memory state
# -------------------------
user_spending_profiles = defaultdict(list)

def analyze_pattern(data):
    user_id = data["user_id"]
    amount = float(data["amount"])
    history = user_spending_profiles[user_id]

    is_anomaly = False
    if len(history) >= 3:
        avg = statistics.mean(history)
        if amount > avg * 3 and amount > 500:
            is_anomaly = True

    history.append(amount)
    if len(history) > 50:
        history.pop(0)

    return is_anomaly

print("🧬 Fraud Agent 1 (Spending Pattern) started...")

for message in consumer:
    payload = message.value.get("payload", {})
    data = payload.get("after")

    if data:
        if analyze_pattern(data):
            print(
                f"🚨 ANOMALY DETECTED | User {data['user_id']} | "
                f"Amount ${data['amount']}"
            )
        else:
            print(f"📊 Profile updated for User {data['user_id']}")
