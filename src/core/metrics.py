from prometheus_client import Counter, Gauge, Histogram

# WebSocket Metrics
websocket_active_connections = Gauge(
    "websocket_active_connections",
    "Number of currently active WebSocket connections"
)
websocket_disconnects_total = Counter(
    "websocket_disconnects_total",
    "Total number of WebSocket disconnects"
)

# Messaging Metrics
message_send_failures_total = Counter(
    "message_send_failures_total",
    "Total number of failed message send attempts"
)
message_delivery_latency_seconds = Histogram(
    "message_delivery_latency_seconds",
    "Latency of message delivery processing",
    buckets=[0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

# AI Worker Metrics
ai_job_duration_seconds = Histogram(
    "ai_job_duration_seconds",
    "Duration of AI worker jobs",
    ["worker_type"],
    buckets=[0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0]
)
ai_job_failures_total = Counter(
    "ai_job_failures_total",
    "Total number of failed AI worker jobs",
    ["worker_type"]
)

# Outbox Queue Metric
outbox_queue_backlog = Gauge(
    "outbox_queue_backlog",
    "Current number of unprocessed outbox events"
)
