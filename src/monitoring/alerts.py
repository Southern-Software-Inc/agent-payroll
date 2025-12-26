"""
Alerting Module
Module ID: APEX-MON-ALERTS-001
Version: 0.1.0

Provides comprehensive alerting and notification system for the APEX Agent Payroll System.
"""

import asyncio
import json
import smtplib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from enum import Enum
from typing import Dict, List, Optional, Any, Callable
import logging

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Alert status values."""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


@dataclass
class Alert:
    """Represents an alert."""
    id: str
    name: str
    severity: AlertSeverity
    status: AlertStatus = AlertStatus.ACTIVE
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    source: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AlertRule:
    """Represents an alert rule."""
    name: str
    condition: Callable[[Dict[str, Any]], bool]
    severity: AlertSeverity
    message_template: str
    cooldown_period: timedelta = field(default_factory=lambda: timedelta(minutes=5))
    enabled: bool = True
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class AlertChannel(ABC):
    """Abstract base class for alert channels."""
    
    @abstractmethod
    async def send_alert(self, alert: Alert) -> bool:
        """
        Send an alert through this channel.
        
        Args:
            alert: Alert to send
            
        Returns:
            True if sent successfully, False otherwise
        """
        pass


class LogAlertChannel(AlertChannel):
    """Log-based alert channel."""
    
    def __init__(self, logger_name: str = "alerts"):
        """Initialize log alert channel."""
        self.logger = logging.getLogger(logger_name)
    
    async def send_alert(self, alert: Alert) -> bool:
        """Send alert to log."""
        try:
            log_level = {
                AlertSeverity.LOW: logging.INFO,
                AlertSeverity.MEDIUM: logging.WARNING,
                AlertSeverity.HIGH: logging.ERROR,
                AlertSeverity.CRITICAL: logging.CRITICAL
            }.get(alert.severity, logging.INFO)
            
            self.logger.log(
                log_level,
                f"ALERT [{alert.severity.value.upper()}] {alert.name}: {alert.message}",
                extra={
                    "alert_id": alert.id,
                    "alert_name": alert.name,
                    "alert_severity": alert.severity.value,
                    "alert_status": alert.status.value,
                    "alert_details": alert.details,
                    "alert_source": alert.source,
                    "alert_tags": alert.tags
                }
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send alert to log: {str(e)}")
            return False


class EmailAlertChannel(AlertChannel):
    """Email-based alert channel."""
    
    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        smtp_username: str,
        smtp_password: str,
        from_address: str,
        to_addresses: List[str],
        use_tls: bool = True
    ):
        """
        Initialize email alert channel.
        
        Args:
            smtp_host: SMTP server host
            smtp_port: SMTP server port
            smtp_username: SMTP username
            smtp_password: SMTP password
            from_address: From email address
            to_addresses: List of recipient email addresses
            use_tls: Whether to use TLS
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.from_address = from_address
        self.to_addresses = to_addresses
        self.use_tls = use_tls
    
    async def send_alert(self, alert: Alert) -> bool:
        """Send alert via email."""
        try:
            # Create message
            msg = MimeMultipart()
            msg['From'] = self.from_address
            msg['To'] = ', '.join(self.to_addresses)
            msg['Subject'] = f"[{alert.severity.value.upper()}] APEX Alert: {alert.name}"
            
            # Create body
            body = self._format_alert_body(alert)
            msg.attach(MimeText(body, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Alert email sent: {alert.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to send alert email: {str(e)}")
            return False
    
    def _format_alert_body(self, alert: Alert) -> str:
        """Format alert body as HTML."""
        severity_color = {
            AlertSeverity.LOW: "#28a745",
            AlertSeverity.MEDIUM: "#ffc107",
            AlertSeverity.HIGH: "#fd7e14",
            AlertSeverity.CRITICAL: "#dc3545"
        }.get(alert.severity, "#6c757d")
        
        return f"""
        <html>
        <body>
            <h2 style="color: {severity_color};">APEX System Alert</h2>
            <table border="1" cellpadding="5" cellspacing="0">
                <tr><td><strong>Alert ID</strong></td><td>{alert.id}</td></tr>
                <tr><td><strong>Name</strong></td><td>{alert.name}</td></tr>
                <tr><td><strong>Severity</strong></td><td style="color: {severity_color};">{alert.severity.value.upper()}</td></tr>
                <tr><td><strong>Status</strong></td><td>{alert.status.value}</td></tr>
                <tr><td><strong>Message</strong></td><td>{alert.message}</td></tr>
                <tr><td><strong>Source</strong></td><td>{alert.source}</td></tr>
                <tr><td><strong>Timestamp</strong></td><td>{alert.timestamp.isoformat()}</td></tr>
                <tr><td><strong>Tags</strong></td><td>{', '.join(alert.tags)}</td></tr>
            </table>
            
            {f'<h3>Details</h3><pre>{json.dumps(alert.details, indent=2)}</pre>' if alert.details else ''}
            
            <hr>
            <p><small>This alert was generated by the APEX Agent Payroll System.</small></p>
        </body>
        </html>
        """


class WebhookAlertChannel(AlertChannel):
    """Webhook-based alert channel."""
    
    def __init__(self, webhook_url: str, headers: Dict[str, str] = None):
        """
        Initialize webhook alert channel.
        
        Args:
            webhook_url: Webhook URL
            headers: HTTP headers to send with webhook
        """
        self.webhook_url = webhook_url
        self.headers = headers or {}
    
    async def send_alert(self, alert: Alert) -> bool:
        """Send alert via webhook."""
        try:
            import httpx
            
            # Prepare payload
            payload = {
                "alert_id": alert.id,
                "name": alert.name,
                "severity": alert.severity.value,
                "status": alert.status.value,
                "message": alert.message,
                "details": alert.details,
                "source": alert.source,
                "timestamp": alert.timestamp.isoformat(),
                "tags": alert.tags,
                "metadata": alert.metadata
            }
            
            # Send webhook
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.webhook_url,
                    json=payload,
                    headers=self.headers,
                    timeout=10.0
                )
                response.raise_for_status()
            
            logger.info(f"Alert webhook sent: {alert.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to send alert webhook: {str(e)}")
            return False


class SlackAlertChannel(AlertChannel):
    """Slack-based alert channel."""
    
    def __init__(self, webhook_url: str, channel: str = None):
        """
        Initialize Slack alert channel.
        
        Args:
            webhook_url: Slack webhook URL
            channel: Slack channel (optional, overrides webhook default)
        """
        self.webhook_url = webhook_url
        self.channel = channel
    
    async def send_alert(self, alert: Alert) -> bool:
        """Send alert to Slack."""
        try:
            import httpx
            
            # Determine color based on severity
            color = {
                AlertSeverity.LOW: "good",
                AlertSeverity.MEDIUM: "warning",
                AlertSeverity.HIGH: "danger",
                AlertSeverity.CRITICAL: "danger"
            }.get(alert.severity, "warning")
            
            # Prepare payload
            payload = {
                "attachments": [
                    {
                        "color": color,
                        "title": f"APEX Alert: {alert.name}",
                        "text": alert.message,
                        "fields": [
                            {"title": "Severity", "value": alert.severity.value.upper(), "short": True},
                            {"title": "Status", "value": alert.status.value, "short": True},
                            {"title": "Source", "value": alert.source, "short": True},
                            {"title": "Timestamp", "value": alert.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC"), "short": True}
                        ],
                        "footer": f"Alert ID: {alert.id}",
                        "ts": int(alert.timestamp.timestamp())
                    }
                ]
            }
            
            # Add channel if specified
            if self.channel:
                payload["channel"] = self.channel
            
            # Send to Slack
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.webhook_url,
                    json=payload,
                    timeout=10.0
                )
                response.raise_for_status()
            
            logger.info(f"Alert sent to Slack: {alert.id}")
            return True
        except Exception as e:
            logger.error(f"Failed to send alert to Slack: {str(e)}")
            return False


class AlertManager:
    """
    Comprehensive alert manager for the APEX system.
    
    Manages alert rules, channels, and alert lifecycle.
    """
    
    def __init__(self):
        """Initialize the alert manager."""
        self._rules: List[AlertRule] = []
        self._channels: List[AlertChannel] = []
        self._alerts: Dict[str, Alert] = {}
        self._alert_history: List[Alert] = []
        self._last_triggered: Dict[str, datetime] = {}
        
        logger.info("AlertManager initialized")
    
    def add_rule(self, rule: AlertRule) -> None:
        """Add an alert rule."""
        self._rules.append(rule)
        logger.info(f"Added alert rule: {rule.name}")
    
    def remove_rule(self, name: str) -> bool:
        """Remove an alert rule by name."""
        for i, rule in enumerate(self._rules):
            if rule.name == name:
                removed = self._rules.pop(i)
                logger.info(f"Removed alert rule: {removed.name}")
                return True
        return False
    
    def add_channel(self, channel: AlertChannel) -> None:
        """Add an alert channel."""
        self._channels.append(channel)
        channel_type = channel.__class__.__name__
        logger.info(f"Added alert channel: {channel_type}")
    
    def remove_channel(self, channel: AlertChannel) -> bool:
        """Remove an alert channel."""
        if channel in self._channels:
            self._channels.remove(channel)
            channel_type = channel.__class__.__name__
            logger.info(f"Removed alert channel: {channel_type}")
            return True
        return False
    
    async def evaluate_rules(self, data: Dict[str, Any]) -> List[Alert]:
        """
        Evaluate all alert rules against data.
        
        Args:
            data: Data to evaluate against rules
            
        Returns:
            List of triggered alerts
        """
        triggered_alerts = []
        
        for rule in self._rules:
            if not rule.enabled:
                continue
            
            try:
                # Check cooldown period
                if rule.name in self._last_triggered:
                    time_since_last = datetime.utcnow() - self._last_triggered[rule.name]
                    if time_since_last < rule.cooldown_period:
                        continue
                
                # Evaluate rule condition
                if rule.condition(data):
                    # Create alert
                    alert = Alert(
                        id=f"{rule.name}_{int(datetime.utcnow().timestamp())}",
                        name=rule.name,
                        severity=rule.severity,
                        message=rule.message_template.format(**data),
                        details=data,
                        tags=rule.tags,
                        metadata=rule.metadata
                    )
                    
                    triggered_alerts.append(alert)
                    self._last_triggered[rule.name] = datetime.utcnow()
                    
                    logger.info(f"Alert rule triggered: {rule.name}")
            except Exception as e:
                logger.error(f"Error evaluating alert rule {rule.name}: {str(e)}")
        
        return triggered_alerts
    
    async def send_alert(self, alert: Alert) -> bool:
        """
        Send an alert through all configured channels.
        
        Args:
            alert: Alert to send
            
        Returns:
            True if sent to at least one channel successfully
        """
        # Store alert
        self._alerts[alert.id] = alert
        self._alert_history.append(alert)
        
        # Send to all channels
        success_count = 0
        for channel in self._channels:
            try:
                if await channel.send_alert(alert):
                    success_count += 1
            except Exception as e:
                logger.error(f"Error sending alert to channel {channel.__class__.__name__}: {str(e)}")
        
        return success_count > 0
    
    async def process_data(self, data: Dict[str, Any]) -> List[Alert]:
        """
        Process data and trigger alerts if rules are met.
        
        Args:
            data: Data to process
            
        Returns:
            List of triggered alerts
        """
        # Evaluate rules
        triggered_alerts = await self.evaluate_rules(data)
        
        # Send alerts
        for alert in triggered_alerts:
            await self.send_alert(alert)
        
        return triggered_alerts
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """
        Acknowledge an alert.
        
        Args:
            alert_id: Alert ID
            acknowledged_by: Who acknowledged the alert
            
        Returns:
            True if acknowledged successfully
        """
        if alert_id in self._alerts:
            alert = self._alerts[alert_id]
            alert.status = AlertStatus.ACKNOWLEDGED
            alert.acknowledged_by = acknowledged_by
            alert.acknowledged_at = datetime.utcnow()
            logger.info(f"Alert acknowledged: {alert_id} by {acknowledged_by}")
            return True
        return False
    
    def resolve_alert(self, alert_id: str) -> bool:
        """
        Resolve an alert.
        
        Args:
            alert_id: Alert ID
            
        Returns:
            True if resolved successfully
        """
        if alert_id in self._alerts:
            alert = self._alerts[alert_id]
            alert.status = AlertStatus.RESOLVED
            alert.resolved_at = datetime.utcnow()
            logger.info(f"Alert resolved: {alert_id}")
            return True
        return False
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts."""
        return [alert for alert in self._alerts.values() if alert.status == AlertStatus.ACTIVE]
    
    def get_alert_history(self, limit: int = 100) -> List[Alert]:
        """Get alert history."""
        return self._alert_history[-limit:]
    
    def get_alert(self, alert_id: str) -> Optional[Alert]:
        """Get alert by ID."""
        return self._alerts.get(alert_id)


# Global alert manager instance
alert_manager = AlertManager()