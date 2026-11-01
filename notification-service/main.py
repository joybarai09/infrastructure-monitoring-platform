
from fastapi import FastAPI, HTTPException
from mailer import send_email

app = FastAPI(title="Monitoring Email Notification Service")


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/alert")
def receive_alert(payload: dict):
    alerts = payload.get("alerts", [])

    if not alerts:
        return {"status": "ignored", "reason": "No alerts received"}

    firing = [
        alert for alert in alerts
        if alert.get("status") == "firing"
    ]

    resolved = [
        alert for alert in alerts
        if alert.get("status") == "resolved"
    ]

    lines = [
        "Infrastructure Monitoring Platform",
        "",
        f"Total alerts received: {len(alerts)}",
        f"Firing: {len(firing)}",
        f"Resolved: {len(resolved)}",
        "",
    ]

    for alert in alerts:
        labels = alert.get("labels", {})
        annotations = alert.get("annotations", {})

        lines.extend([
            f"Alert: {labels.get('alertname', 'Unknown')}",
            f"Status: {alert.get('status', 'unknown').upper()}",
            f"Severity: {labels.get('severity', 'unknown')}",
            f"Instance: {labels.get('instance', 'unknown')}",
            f"Summary: {annotations.get('summary', 'No summary')}",
            f"Description: {annotations.get('description', 'No description')}",
            "",
        ])

    if firing and resolved:
        subject = "Infrastructure Monitoring - Alert Update"
    elif firing:
        subject = "Infrastructure Monitoring - ALERT FIRING"
    else:
        subject = "Infrastructure Monitoring - ALERT RESOLVED"

    try:
        send_email(subject, "\n".join(lines))
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Email delivery failed: {exc}"
        )

    return {
        "status": "email_sent",
        "alerts_received": len(alerts),
    }
