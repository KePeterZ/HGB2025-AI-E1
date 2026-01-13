from kafka import KafkaConsumer
import json
from collections import deque
import time

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
    group_id="fraud-agent-2",
    value_deserializer=lambda x: json.loads(x.decode("utf-8"))
)

# -------------------------
# In-memory state
# -------------------------
user_history = {}

def analyze_fraud(transaction):
    user_id = transaction["user_id"]
    amount = float(transaction["amount"])
    now = time.time()

    if user_id not in user_history:
        user_history[user_id] = deque()

    user_history[user_id].append(now)
    while user_history[user_id] and user_history[user_id][0] < now - 60:
        user_history[user_id].popleft()

    velocity = len(user_history[user_id])

    score = 0
    if velocity > 5:
        score += 40
    if amount > 4000:
        score += 50

    return score

print("⚡ Fraud Agent 2 (Velocity Detection) started...")

for message in consumer:
    payload = message.value.get("payload", {})
    data = payload.get("after")

    if data:
        score = analyze_fraud(data)
        if score > 70:
            print(
                f"⚠️ HIGH FRAUD ALERT | User {data['user_id']} | "
                f"Score {score} | Amount ${data['amount']}"
            )
        else:
            print(
                f"✅ Transaction OK | ID {data['id']} | Score {score}"
            )
