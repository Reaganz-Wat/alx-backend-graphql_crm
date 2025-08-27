#!/bin/bash

# Script to delete customers with no orders in the past year
# Logs the number of deleted customers to /tmp/customer_cleanup_log.txt

LOG_FILE="/tmp/customer_cleanup_log.txt"

# Get current timestamp
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

# Run Django shell command
DELETED_COUNT=$(python3 manage.py shell <<EOF
from django.utils import timezone
from datetime import timedelta
from crm.models import Customer

# Define cutoff date (1 year ago)
cutoff_date = timezone.now() - timedelta(days=365)

# Select customers with no orders since cutoff
inactive_customers = Customer.objects.filter(orders__order_date__lt=cutoff_date).distinct()

count = inactive_customers.count()

# Delete the customers
inactive_customers.delete()

# Return count
print(count)
EOF
)

# Log the result
echo "$TIMESTAMP - Deleted $DELETED_COUNT inactive customers" >> $LOG_FILE