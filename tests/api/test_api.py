"""
Test the API connections.
Relies on client/secret supplied in config.ini
"""

from reddy.api import RedditAPI


def test_authenticate():
    """Test the credentials"""
    client = RedditAPI()
    assert client._access_token is not None
