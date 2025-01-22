from gophish import Gophish
import sys
import os
import json
from gophish.models import *
sys.path.append(r'./')

from landingPages.configReader import JsonReader
from bs4 import BeautifulSoup

class LandingPages:

    def __init__(self):
        self.base_html = "assets/base_html_page.html"
        self.modified_html = "assets/modified_html_page.html"


    def init_gophish_api(self):
        config  = JsonReader("config.json")

        api_key = config.get_value_from_config("gophish_api_key")
        if api_key is None:
            print(f'error in getting api_key for gophish')
            return None
        
        gophish_url = config.get_value_from_config("gophish_url")
        if gophish_url is None:
            print(f'error in getting gophish_url for gophish')
            return None
        
        api = Gophish(api_key, host=gophish_url, verify=False)
        return api

    def create_landing_page(self, api, name, html_content):
        try:
            # Define the landing page object
            page = Page(
                name=name,               # Name of the landing page
                html=html_content,       # HTML content for the landing page
                capture_credentials=False,  # Enable credential capturing
                capture_passwords=False,    # Enable password capturing
                redirect_url="https://example.com"  # Optional redirect after form submission
            )
            #check if page exist with the same name.
            pages = api.pages.get()
            for item in pages:
                if item.name == page.name:
                    api.pages.delete(item.id)
            # Use the API to create the page
            created_page = api.pages.post(page)
            print(f"Landing page created successfully: ID {created_page.id}")
            return created_page

        except Exception as e:
            print(f"Error creating landing page: {e}")

    def get_user_phishing_explanation(self, userId):
        email  = JsonReader("./assets/emails.json")

        explanation = email.get_explanation_from_email(userId)
        return explanation
        #if explanation is None:
        #    print(f'error in getting api_key for gophish')
        #    exit()

    def update_landing_page(self, explanation):
        #Load the base html for landing page
        try:
            with open(self.base_html, "r") as file:
                html_content = file.read()
        except Exception as e:
            print(f"Error loading base html page: {e}")

        # Parse the HTML content
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find the explanation section
        explanation_div = soup.find('div', class_='explanation')

        
        lines = explanation.split('\n')

        # Remove the leading '*' and any extra whitespace
        points = [line.lstrip('*').strip() for line in lines]
        # Convert points to a beautiful HTML list
        new_explanation_html = "<p><strong>Explanation:</strong></p>\n<ul>\n"
        for point in points:
            new_explanation_html += f"    <li>{point}</li>\n"
        new_explanation_html += "</ul>"
        
        # Modify the explanation content
        explanation_div.clear()  # Clear the current content
        explanation_div.append(BeautifulSoup(new_explanation_html, 'html.parser'))  # Add new content

        # Save the updated HTML back to the file
        #with open(self.modified_html, 'w', encoding='utf-8') as file:
        #    file.write(str(soup))
        
        print("HTML updated successfully!")
        return str(soup)


    def create_landing_page_for_user(self, api, userId):

        explanation = self.get_user_phishing_explanation(userId)
        
        if explanation is None:
            print(f'error in in getting explanation')
            exit()

        html_content = self.update_landing_page(explanation)
        self.create_landing_page(api, userId, html_content)