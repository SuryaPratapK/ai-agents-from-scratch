class ProductionEnvironment:

    def __init__(self, scenario="database", allow_actions=False):
        self.allow_actions = allow_actions

        self.max_connections = 20
        self.checkout_connections = 4

        self.reporting_connections = (
            16 if scenario == "database" else 2
        )

        self.reporting_job_running = True
        self.payment_healthy = scenario != "payment"

    # Tool 1: Inspect checkout service logs
    def get_logs(self):

        if self.reporting_connections == 16:
            return [
                "ERROR: DB connection timeout",
                "ERROR: Unable to acquire database connection",
                "ERROR: Checkout request failed"
            ]

        if not self.payment_healthy:
            return [
                "ERROR: Payment service unavailable",
                "ERROR: HTTP 503",
                "ERROR: Checkout request failed"
            ]

        return ["INFO: Checkout requests successful"]

    # Tool 2: Inspect database metrics
    def get_db_metrics(self):

        active = (
            self.checkout_connections
            + self.reporting_connections
        )

        return {
            "max_connections": self.max_connections,
            "active_connections": active,
            "available_connections": (
                self.max_connections - active
            )
        }

    # Tool 3: Inspect active database queries
    def get_active_queries(self):

        return [
            {
                "service": "checkout_service",
                "connections": self.checkout_connections
            },
            {
                "service": "reporting_job",
                "connections": self.reporting_connections,
                "duration_seconds": (
                    180 if self.reporting_connections == 16 else 0
                )
            }
        ]

    # Tool 4: Inspect payment service
    def get_payment_health(self):

        return {
            "status": (
                "healthy" if self.payment_healthy else "unhealthy"
            ),
            "http_status": 200 if self.payment_healthy else 503
        }

    # Tool 5: Inspect deployment history
    def get_deployment_history(self):

        return [
            {
                "service": "reporting_service",
                "change": "New reporting task deployed"
            }
        ]

    # Tool 6: Suspend reporting job
    def suspend_reporting_job(self):

        if not self.allow_actions:
            return {"status": "approval_required"}

        self.reporting_job_running = False
        self.reporting_connections = 0

        return {
            "status": "success",
            "message": "Reporting job suspended"
        }

    # Tool 7: Restart payment service
    def restart_payment_service(self):

        if not self.allow_actions:
            return {"status": "approval_required"}

        self.payment_healthy = True

        return {
            "status": "success",
            "message": "Payment service restarted"
        }

    # Tool 8: Verify system recovery
    def verify_health(self):

        db_metrics = self.get_db_metrics()

        healthy = (
            db_metrics["available_connections"] > 0
            and self.payment_healthy
        )

        return {
            "checkout_status": (
                "healthy" if healthy else "unhealthy"
            ),
            "checkout_error_rate": "0.5%" if healthy else "35%",
            "database": db_metrics,
            "payment": self.get_payment_health()
        }