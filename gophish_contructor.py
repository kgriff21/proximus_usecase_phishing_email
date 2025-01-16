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

    def _make_request(self, method: str, endpoint: str, data: Dict[str, Any] = None) -> Any:
        """
        Makes HTTP requests to the Gophish API.

        :param method: The HTTP method ('GET', 'POST', etc.)
        :param endpoint: The specific API endpoint to call.
        :param data: The data to send with a POST request (optional).
        :return: The response in JSON format, or None if an error occurs.
        """
        url = f"{self.api_url}{endpoint}"
        response = requests.request(method, url, json=data, headers=self.headers)
        
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