
import platform
import time

import psutil
from fastapi import FastAPI, Request
from fastapi.responses import Response
from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    CONTENT_TYPE_LATEST,
    generate_latest,
)

app = FastAPI(
    title="Infrastructure Monitoring Platform",
    description="A Docker and Kubernetes infrastructure monitoring application",
    version="1.0.0",
)

REQUEST_COUNT = Counter(
    "app_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
)

REQUEST_LATENCY = Histogram(
    "app_http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["endpoint"],
)

CPU_USAGE = Gauge("system_cpu_usage_percent", "System CPU usage percentage")
MEMORY_USAGE = Gauge("system_memory_usage_percent", "System memory usage percentage")
DISK_USAGE = Gauge("system_disk_usage_percent", "Root filesystem disk usage percentage")


@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    duration = time.time() - start_time
    endpoint = request.url.path

    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=endpoint,
        status=str(response.status_code),
    ).inc()

    REQUEST_LATENCY.labels(endpoint=endpoint).observe(duration)

    return response


@app.get("/")
def root():
    return {
        "application": "Infrastructure Monitoring Platform",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/api/info")
def system_info():
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    CPU_USAGE.set(psutil.cpu_percent(interval=0.1))
    MEMORY_USAGE.set(memory.percent)
    DISK_USAGE.set(disk.percent)

    return {
        "hostname": platform.node(),
        "operating_system": platform.system(),
        "os_release": platform.release(),
        "architecture": platform.machine(),
        "cpu_count": psutil.cpu_count(),
        "cpu_usage_percent": psutil.cpu_percent(interval=0.1),
        "memory_total_gb": round(memory.total / (1024 ** 3), 2),
        "memory_used_percent": memory.percent,
        "disk_total_gb": round(disk.total / (1024 ** 3), 2),
        "disk_used_percent": disk.percent,
    }


@app.get("/metrics")
def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )
