"""
Simple Webhook Receiver
Demonstrates receiving and processing webhook payloads
"""
from flask import Flask, request, jsonify
import json
import hmac
import hashlib
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Store received webhooks (in production, use a database)
received_webhooks = []


def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    """Verify webhook signature (GitHub style)"""
    if not signature or not secret:
        return True  # Skip verification if not configured
    
    expected = 'sha256=' + hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(expected, signature)


@app.route('/webhook', methods=['POST'])
def receive_webhook():
    """Receive webhook POST requests"""
    # Get signature header (optional verification)
    signature = request.headers.get('X-Hub-Signature-256', '')
    
    # Log the webhook
    webhook_data = {
        'timestamp': datetime.now().isoformat(),
        'headers': dict(request.headers),
        'payload': request.get_json() or {},
        'raw_body': request.get_data().decode('utf-8')
    }
    
    received_webhooks.append(webhook_data)
    logger.info(f"📨 Webhook received at {webhook_data['timestamp']}")
    
    # Process based on event type
    event_type = request.headers.get('X-GitHub-Event', 'unknown')
    
    if event_type == 'push':
        handle_push_event(webhook_data['payload'])
    elif event_type == 'pull_request':
        handle_pr_event(webhook_data['payload'])
    else:
        logger.info(f"📋 Event type: {event_type}")
    
    return jsonify({'status': 'received', 'event': event_type}), 200


def handle_push_event(payload: dict):
    """Handle GitHub push events"""
    repo = payload.get('repository', {}).get('full_name', 'unknown')
    ref = payload.get('ref', 'unknown')
    commits = len(payload.get('commits', []))
    
    logger.info(f"🚀 Push to {repo}:{ref} ({commits} commits)")


def handle_pr_event(payload: dict):
    """Handle GitHub PR events"""
    action = payload.get('action', 'unknown')
    pr_number = payload.get('pull_request', {}).get('number', 'unknown')
    
    logger.info(f"🔀 PR #{pr_number} {action}")


@app.route('/webhooks', methods=['GET'])
def list_webhooks():
    """List received webhooks"""
    return jsonify({
        'count': len(received_webhooks),
        'webhooks': [
            {
                'timestamp': w['timestamp'],
                'event': w['headers'].get('X-GitHub-Event', 'unknown')
            }
            for w in received_webhooks[-10:]  # Last 10
        ]
    })


@app.route('/', methods=['GET'])
def index():
    """Health check endpoint"""
    return jsonify({
        'status': 'running',
        'endpoints': [
            'POST /webhook - Receive webhooks',
            'GET /webhooks - List received webhooks',
            'GET / - This page'
        ],
        'webhooks_received': len(received_webhooks)
    })


if __name__ == '__main__':
    print("🌐 Webhook Server Starting...")
    print("Endpoints:")
    print("  POST http://localhost:5000/webhook")
    print("  GET  http://localhost:5000/webhooks")
    print()
    
    app.run(host='0.0.0.0', port=5000, debug=False)
