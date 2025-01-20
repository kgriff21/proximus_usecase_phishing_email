import requests
from dotenv import load_dotenv
from typing import Dict, Any
import os

class GophishWrapper:
    def __init__(self, api_url: str, api_key: str):
        """
        Initializes the GophishWrapper class to interact with the Gophish API.

        :param api_url: The base URL for the Gophish instance.
        :param api_key: The API key to authenticate requests to Gophish.
        """
        load_dotenv()
        
        self.api_url = os.getenv('GOPHISH_API_URL', api_url)
        self.api_key = os.getenv('GOPHISH_API_KEY', api_key)
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def create_smtp_profile(self, name: str, host: str, port: int, username: str, password: str, from_address: str, tls: bool = True) -> Dict[str, Any]:
        """
        Create a new SMTP profile.

        :param name: The name of the SMTP profile.
        :param host: The SMTP server host (e.g., 'smtp.gmail.com').
        :param port: The SMTP server port (usually 465 for SSL or 587 for TLS).
        :param username: The username for SMTP authentication.
        :param password: The password for SMTP authentication.
        :param from_address: The "from" email address that will appear in the phishing emails.
        :param ssl: Whether to use SSL (default is True). 
        :return: The response from the API call (SMTP profile data).
        """
        data = {
            "name": name,
            "host": host,
            "port": port,
            "username": username,
            "password": password,
            "from_address": from_address,
            "tls": tls
            # ssl: is possibly but outdated and insecure
        }
        return self._make_request("POST", "/smtp", data)

    def get_smtp_profiles(self) -> Dict[str, Any]:
        """
        Get all SMTP profiles.

        :return: A list of all SMTP profiles.
        """
        return self._make_request("GET", "/smtp")

    def update_smtp_profile(self, profile_id: int, name: str, host: str, port: int, username: str, password: str, from_address: str, tls: bool = True) -> Dict[str, Any]:
        """
        Update an existing SMTP profile.

        :param profile_id: The ID of the SMTP profile to update.
        :param name: The new name for the SMTP profile.
        :param host: The new SMTP server host.
        :param port: The new SMTP server port.
        :param username: The new username for SMTP authentication.
        :param password: The new password for SMTP authentication.
        :param from_address: The new "from" email address.
        :param ssl: Whether to use SSL (default is True).
        :return: The response from the API call (updated SMTP profile data).
        """
        data = {
            "name": name,
            "host": host,
            "port": port,
            "username": username,
            "password": password,
            "from_address": from_address,
            "tls":tls
        }
        return self._make_request("PUT", f"/smtp/{profile_id}", data)

    def delete_smtp_profile(self, profile_id: int) -> Dict[str, Any]:
        """
        Delete an SMTP profile.

        :param profile_id: The ID of the SMTP profile to delete.
        :return: The response from the API call (confirmation of deletion).
        """
        return self._make_request("DELETE", f"/smtp/{profile_id}")

    def _make_request(self, method: str, endpoint: str, data: Dict[str, Any] = None) -> Any:
        """
        Makes HTTP requests to the Gophish API.

        :param method: The HTTP method ('GET', 'POST', etc.)
        :param endpoint: The specific API endpoint to call.
        :param data: The data to send with a POST request (optional).
        :return: The response in JSON format, or None if an error occurs.
        """
        url = f"{self.api_url}{endpoint}"
        response = requests.request(method, url, json=data, headers=self.headers, verify="C:/Program Files/GoPhish/gophish_admin.crt")
        
        # Handle errors
        if response.status_code != 200:
            print(f"Error: {response.status_code}, {response.text}")
            return None
        return response.json()

    def create_target_group(self, group_name: str, recipients: list) -> Dict[str, Any]:
        """
        Create a target group for the campaign.

        :param group_name: The name of the group.
        :param recipients: A list of email addresses to include in the group.
        :return: The response from the API call (group data).
        """
        data = {
            "name": group_name,
            "targets": [{"email": recipient} for recipient in recipients]
        }
        return self._make_request("POST", "/groups", data)

    def create_campaign(self, name: str, template_id: int, url: str, from_address: str, subject: str, group_id: int) -> Dict[str, Any]:
        """
        Create a new phishing campaign.

        :param name: The name of the campaign.
        :param template_id: The ID of the template to use.
        :param url: The URL to send to the target.
        :param from_address: The from address for the campaign emails.
        :param subject: The subject for the phishing email.
        :param group_id: The ID of the target group.
        :return: The response from the API call (campaign data).
        """
        data = {
            "name": name,
            "template": template_id,
            "url": url,
            "from_address": from_address,
            "subject": subject,
            "group_id": group_id  # Associate the target group with the campaign
        }
        return self._make_request("POST", "/campaigns", data)

    def create_template(self, name: str, html: str, text: str) -> Dict[str, Any]:
        """
        Create a new phishing template.

        :param name: The name of the template.
        :param html: The HTML content of the phishing email.
        :param text: The plain text version of the phishing email.
        :return: The response from the API call (template data).
        """
        data = {
            "name": name,
            "html": html,
            "text": text
        }
        return self._make_request("POST", "/templates", data)

    def get_campaigns(self) -> Dict[str, Any]:
        """
        Get all campaigns.

        :return: A list of all campaigns.
        """
        return self._make_request("GET", "/campaigns")

    def get_templates(self) -> Dict[str, Any]:
        """
        Get all templates.

        :return: A list of all templates.
        """
        return self._make_request("GET", "/templates")

    def get_campaign_results(self, campaign_id: int) -> Dict[str, Any]:
        """
        Get results of a specific campaign.

        :param campaign_id: The ID of the campaign.
        :return: The results of the campaign.
        """
        return self._make_request("GET", f"/campaigns/{campaign_id}/results")

    def get_campaign_report(self, campaign_id: int) -> Dict[str, Any]:
        """
        Get the report for a specific campaign.

        :param campaign_id: The ID of the campaign.
        :return: The report data of the campaign.
        """
        return self._make_request("GET", f"/campaigns/{campaign_id}/report")
    
