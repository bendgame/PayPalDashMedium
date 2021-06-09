from paypalcheckoutsdk.core import PayPalHttpClient, SandboxEnvironment
from config import client_id, client_secret

# Creating an environment
environment = SandboxEnvironment(client_id=client_id, client_secret=client_secret)
client = PayPalHttpClient(environment)

class SubscriptionRequest:
    """
    Creates an subscriber.
    """
    def __init__(self):
        self.verb = "POST"
        self.path = "/v1/billing/subscriptions"
        self.headers = {}
        self.headers["Content-Type"] = "application/json"
        self.body = None

    def prefer(self, prefer):
        self.headers["Prefer"] = str(prefer)

    def request_body(self, order):
        self.body = order
        return self

class SubscriptionActivate:
    """
    Creates an subscriber.
    """
    def __init__(self, orderID):
        self.verb = "GET"
        self.path = f"/v1/billing/subscriptions/{orderID}"
        self.headers = {}
        self.headers["Content-Type"] = "application/json"
        

    def prefer(self, prefer):
        self.headers["Prefer"] = str(prefer)

    def request_body(self, order):
        self.body = order
        return self