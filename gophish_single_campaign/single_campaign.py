from gophish import Gophish
from gophish.models import *
from dotenv import load_dotenv
import json
import os
import re
from datetime import date

this_day=date.today()

class SingleCampaign():
    def __init__(self):
        load_dotenv()
        self.api_key= os.getenv("GOPHISH_API_KEY")
        self.gophish_url= os.getenv("GOPHISH_URL")
        self.api = Gophish(self.api_key,host=self.gophish_url,verify=False)

    def get_campaigns(self):
        for campaign in self.api.campaigns.get():
            print (campaign.name)

    def print_usergroups(self):
        for group in self.api.groups.get():
            print ('{} has {} users'.format(group.name, len(group.targets)))

    def get_landing_page_url(self, page_name):
        pages = self.api.pages.get()
        for item in pages:
            if item.name == page_name:
                return (item.redirect_url)
        return None

    def create_landing_page(self, landing_page_name, html_content):
        try:
            # Define the landing page object
            page = Page(
                name=landing_page_name,               # Name of the landing page
                html=html_content,       # HTML content for the landing page
                capture_credentials=False,  # Enable credential capturing
                capture_passwords=False,    # Enable password capturing
                redirect_url="https://example.com"  # Optional redirect after form submission
            )
            #check if page exist with the same name.
            pages = self.api.pages.get()
            for item in pages:
                if item.name == page.name:
                    self.api.pages.delete(item.id)
            # Use the API to create the page
            created_page = self.api.pages.post(page)
            print(f"Landing page created successfully: ID {created_page.id}")
            return created_page

        except Exception as e:
            print(f"Error creating landing page: {e}")

    def create_user(self, first_name,last_name,email,position):
        user = User(
            first_name=first_name,
            last_name=last_name, 
            email=email,
            position=position
        )
        return user
    
    def create_usergroups(self, targets, group_name):
        
        group = Group(
            name=group_name,
            targets=targets
        )

        #Check if already a group exist with same name
        #If existing delete that and create the new
        groups = self.api.groups.get()
        for item in groups:
            if item.name == group.name:
                self.api.groups.delete(item.id)

        group = self.api.groups.post(group)
        return group.name
    
    def create_email_template(self,template_name,subject,body):
        template = Template(
            name=template_name, 
            subject=subject,
            html=body)
        try:
            templates = self.api.templates.get()
            for item in templates:
                if item.name == template.name:
                    self.api.templates.delete(item.id)
            
            created_template = self.api.templates.post(template)
            print(f"Email template created successfully: ID {created_template.id}")
        except Exception as e:
            print(f"Error creating landing page: {e}")
        
    
    
    
    def create_campaign(self, group_name, landing_page_name):
        sender_profile="Test profile"
        landing_page=landing_page_name
        template = "test template final"
        groups = [Group(name=group_name)]
        page = Page(name=landing_page)
        template = Template(name=template)
        smtp = SMTP(name=sender_profile)
        url="http://127.0.0.1"

        campaign = Campaign(
        name=f"proximus_campaign-{this_day}", groups=groups, page=page,
        template=template, smtp=smtp,url=url)

        campaigns = self.api.campaigns.get()
        for item in campaigns:
            if item.name == campaign.name:
                self.api.campaigns.delete(item.id)
        

        campaign = self.api.campaigns.post(campaign)

        return campaign.name

    def modify_email_body(self, body, landing_page_url):
        # Replace all hrefs in the HTML
        updated_html = re.sub(r'href="[^"]+"', f'href="{landing_page_url}"', body)
        return updated_html
    
    def beautify_explanation(self, explanation):
        lines = explanation.split('\n')

        # Remove the leading '*' and any extra whitespace
        points = [line.lstrip('*').strip() for line in lines]
        # Convert points to a beautiful HTML list
        new_explanation_html = "\n<ul>\n"
        for point in points:
            new_explanation_html += f"    <li>{point}</li>\n"
        new_explanation_html += "</ul>"
        return new_explanation_html


def main():
    api=SingleCampaign()
    landing_page_name = "Test landing"
    template_name = "test template final"
    landing_page_url = api.get_landing_page_url(landing_page_name)
    
    targets = []
    f = open("./assets/emails.json",'r')
    employees= json.load(f)
    for emp in employees:
        
            email_body = emp["body"]#api.modify_email_body(emp["body"], "")
                
            user=api.create_user(emp['Subject'], api.beautify_explanation(emp['explanation']),
                                    emp["Email"], email_body)
            targets.append(user)

    group_name = f"proximus_group-{this_day}"
    api.create_usergroups(targets, group_name)
    
    #template=api.create_template(emp['FirstName'],emp['LastName'],emp["Subject"],emp["body"])
    try:
        with open("assets/base_html_page.html", "r") as file:
            html_content = file.read()
            landing_page_name = f"proximus_landing_page-{this_day}"
                   
    except Exception as e:
            print(f"Error loading base html page: {e}")

    api.create_landing_page(landing_page_name, html_content)
    try:
        with open("assets/gophish_email_template.html", "r") as file:
            html_content = file.read()
            template_name = f"proximus_email_template-{this_day}"       
    except Exception as e:
            print(f"Error loading base html page: {e}")

    api.create_email_template(template_name, "{{.FirstName}}", html_content)

    campaign=api.create_campaign(group_name, landing_page_name, )
    print(campaign)

main()