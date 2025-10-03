from .client_impl import ServiceClient

def get_client(base_url="http://127.0.0.1:8000", **kwargs):
    """Drop-in replacement for mail_client_api.get_client"""
    return ServiceClient(base_url=base_url)

__all__ = ["ServiceClient", "get_client"]
