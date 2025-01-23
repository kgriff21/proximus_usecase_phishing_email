from gophish import Gophish
from gophish.models import *
from typing import List

class GophishWrapper:
    def __init__(self, api_key: str):
        """
        Initializes the GophishWrapper class to interact with the Gophish API.
        
        :param api_key: The API key to authenticate requests to Gophish.
        """
        self.api = Gophish(api_key,host='https://localhost:3333',verify=False)

    def check_existing_template(self, name: str) -> str:
        """
        Check if a template with the same name exists.
        
        :param name: The name of the template.
        :return: The ID of the existing template or None if not found.
        """
        templates = self.api.templates.get()
        for template in templates:
            if template.name == name:
                print(f"Template with name '{name}' already exists.")
                return template.id
        return None

    def create_template(self, name: str, html: str, subject: str) -> str:
        """
        Create a new phishing email template, checking for duplicates.
        
        :param name: The name of the template.
        :param html: The HTML content of the phishing email.
        :param subject: The subject of the phishing email.
        :return: The ID of the created template or the existing template ID.
        """
        template_id = self.check_existing_template(name)
        if template_id:
            return template_id

        template = Template(name=name, html=html, subject=subject)
        created_template = self.api.templates.post(template)
        return created_template.id

    def check_existing_campaign(self, name: str) -> str:
        """
        Check if a campaign with the same name exists.
        
        :param name: The name of the campaign.
        :return: The ID of the existing campaign or None if not found.
        """
        campaigns = self.api.campaigns.get()
        for campaign in campaigns:
            if campaign.name == name:
                print(f"Campaign with name '{name}' already exists.")
                return campaign.id
        return None

    def create_campaign(self, name: str, template_id: str, phishing_url: str, smtp_id: str, group_id: str) -> str:
        """
        Create a new phishing campaign, checking for duplicates.
        
        :param name: The name of the campaign.
        :param template_id: The ID of the template.
        :param phishing_url: The phishing URL for the campaign.
        :param smtp_id: The ID of the SMTP profile.
        :param group_id: The ID of the target group.
        :return: The ID of the created campaign or the existing campaign ID.
        """
        campaign_id = self.check_existing_campaign(name)
        if campaign_id:
            return campaign_id

        campaign = Campaign(name=name, template=template_id, url=phishing_url, smtp=smtp_id, group=group_id)
        created_campaign = self.api.campaigns.post(campaign)
        return created_campaign.id

    def check_existing_group(self, name: str) -> str:
        """
        Check if a target group with the same name exists.
        
        :param name: The name of the target group.
        :return: The ID of the existing group or None if not found.
        """
        groups = self.api.groups.get()
        for group in groups:
            if group.name == name:
                print(f"Group with name '{name}' already exists.")
                return group.id
        return None

    def create_target_group(self, name: str, recipients: List[str]) -> str:
        """
        Create a new target group, checking for duplicates.
        
        :param name: The name of the target group.
        :param recipients: A list of email addresses for the target group.
        :return: The ID of the created group or the existing group ID.
        """
        group_id = self.check_existing_group(name)
        if group_id:
            return group_id

        targets = [User(email=email) for email in recipients]  # Ensure that you have all required fields here
        group = Group(name=name, targets=targets)
        created_group = self.api.groups.post(group)
        return created_group.id

    def check_existing_smtp(self, name: str) -> str:
        """
        Check if an SMTP profile with the same name exists.
        
        :param name: The name of the SMTP profile.
        :return: The ID of the existing SMTP profile or None if not found.
        """
        smtps = self.api.smtp.get()
        for smtp in smtps:
            if smtp.name == name:
                print(f"SMTP profile with name '{name}' already exists.")
                return smtp.id
        return None

    def create_smtp_profile(self, name: str, host: str, port: int, from_address: str) -> str:
        """
        Create a new SMTP profile, checking for duplicates.
        
        :param name: The name of the SMTP profile.
        :param host: The SMTP server host (e.g., 'smtp.gmail.com').
        :param port: The SMTP server port (usually 465 for SSL or 587 for TLS).
        :param from_address: The "from" email address for phishing emails.
        :return: The ID of the created SMTP profile or the existing profile ID.
        """
        smtp_id = self.check_existing_smtp(name)
        if smtp_id:
            return smtp_id

        smtp = SMTP(name=name, host=host, port=port, from_address=from_address)
        created_smtp = self.api.smtp.post(smtp)
        return created_smtp.id