#!/usr/bin/env python3
"""Alertmanager webhook -> ntfy.sh bridge.

Receives Alertmanager's default webhook JSON on POST /hook, formats a title
and body, and pushes to https://ntfy.sh/$NTFY_TOPIC with Title/Priority
headers. GET /healthz returns 200 for the compose healthcheck.
"""
import json
import logging
import os
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

NTFY_TOPIC = os.environ["NTFY_TOPIC"]
NTFY_URL = f"https://ntfy.sh/{NTFY_TOPIC}"
SEVERITY_RANK = {"critical": 3, "warning": 2, "info": 1}
SEVERITY_PRIORITY = {"critical": "5", "warning": "4", "info": "3"}

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger("bridge")


def format_push(payload: dict) -> tuple[str, str, str]:
    status = payload.get("status", "firing")
    alertname = payload.get("commonLabels", {}).get("alertname", "alert")
    alerts = payload.get("alerts", [])

    if status == "firing":
        title = f"FIRING: {alertname}"
        blocks = []
        for a in alerts:
            sev = a.get("labels", {}).get("severity", "info")
            summary = a.get("annotations", {}).get("summary", "")
            desc = a.get("annotations", {}).get("description", "")
            blocks.append(f"[{sev}] {summary}\n{desc}\n")
        body = "\n".join(blocks)
        worst = max(
            (a.get("labels", {}).get("severity", "info") for a in alerts),
            key=lambda s: SEVERITY_RANK.get(s, 0),
            default="info",
        )
        priority = SEVERITY_PRIORITY.get(worst, "3")
    else:
        title = f"RESOLVED: {alertname}"
        body = "\n".join(
            f"{a.get('annotations', {}).get('summary', '')} (resolved)"
            for a in alerts
        )
        priority = "3"

    return title, body, priority


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/healthz":
            self.send_response(200)
            self.end_headers()
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        if self.path != "/hook":
            self.send_response(404)
            self.end_headers()
            return
        length = int(self.headers.get("Content-Length", 0))
        payload = json.loads(self.rfile.read(length))
        title, body, priority = format_push(payload)

        req = urllib.request.Request(
            NTFY_URL,
            data=body.encode("utf-8"),
            headers={
                "Title": title,
                "Priority": priority,
                "Content-Type": "text/plain; charset=utf-8",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            log.info("pushed %s -> ntfy (%d)", title, resp.status)

        self.send_response(204)
        self.end_headers()

    def log_message(self, *_):
        return


if __name__ == "__main__":
    HTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
