from gophish import Gophish
from gophish.models import *
from dotenv import load_dotenv
import json
import os


class Api_utils:

    def __init__(self):
        load_dotenv()
        self.api_key= os.getenv("GOPHISH_API_KEY")
        self.api = Gophish(self.api_key,host='https://localhost:3333',verify=False)

    def get_campaigns(self):
        for campaign in self.api.campaigns.get():
            print (campaign.name)

    def get_usergroups(self):
        for group in self.api.groups.get():
            print ('{} has {} users'.format(group.name, len(group.targets)))
    
    def create_usergroups(self, first_name,last_name,email):
        targets = [
        User(first_name=first_name, last_name=last_name, email='rasmita.damaraju@gmail.com')]

        group = Group(name=first_name+last_name, targets=targets)

        group = self.api.groups.post(group)
        return group.name
    
    def create_template(self,firstname,lastname,subject,body):
        template = Template(name=firstname+lastname, subject=subject,html=body)
        template = self.api.templates.post(template)
        return template.name
    
    
    
    def create_campaign(self,firstname,lastname,groups,template):
        sender_profile="gmail_test"
        landing_page="Successful_Phish"
        groups = [Group(name=groups)]
        page = Page(name=landing_page)
        template = Template(name=template)
        smtp = SMTP(name=sender_profile)
        url="http://127.0.0.1"
        campaign = Campaign(
        name=firstname+lastname, groups=groups, page=page,
        template=template, smtp=smtp,url=url)

        campaign = self.api.campaigns.post(campaign)

        return campaign.name




def main(input_file= "./assets/emails.json"):
    api=Api_utils()
    f = open(input_file,'r')
    employees= json.load(f)
    for emp in employees:
        group=api.create_usergroups(emp['FirstName'],emp['LastName'],emp["Email"])
        template=api.create_template(emp['FirstName'],emp['LastName'],emp["Subject"],emp["body"])
        campaign=api.create_campaign(emp['FirstName'],emp['LastName'],group,template)
        print(campaign)


