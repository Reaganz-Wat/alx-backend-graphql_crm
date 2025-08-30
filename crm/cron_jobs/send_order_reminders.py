#!/usr/bin/env python3
import requests
from datetime import datetime, timedelta

# GraphQL endpoint
GRAPHQL_URL = "http://localhost:8000/graphql"

# Define cutoff date (orders placed in last 7 days)
cutoff_date = (datetime.now() - timedelta(days=7)).isoformat()

# GraphQL query (adapted to your models)
query = """
query RecentOrders($cutoff: DateTime!) {
  orders(orderDate_Gte: $cutoff) {
    id
    customer {
      email
    }
  }
}
"""

variables = {"cutoff": cutoff_date}

try:
    response = requests.post(
        GRAPHQL_URL,
        json={"query": query, "variables": variables},
        headers={"Content-Type": "application/json"},
    )
    response.raise_for_status()
    data = response.json()

    # Extract orders list
    orders = data.get("data", {}).get("orders", [])

    with open("/tmp/order_reminders_log.txt", "a") as log_file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for order in orders:
            log_file.write(
                f"[{timestamp}] Reminder: Order #{order['id']} for customer {order['customer']['email']}\n"
            )

    print("Order reminders processed!")

except Exception as e:
    with open("/tmp/order_reminders_log.txt", "a") as log_file:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(f"[{timestamp}] ERROR: {str(e)}\n")
    print("Failed to process order reminders. Check log.")