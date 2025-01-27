import json
import os
from dotenv import load_dotenv
from gophish_constructor import GophishWrapper
#from landingPages.landing_pages import LandingPages
from gophish.models import *
from bs4 import BeautifulSoup

load_dotenv()

api_key = os.getenv('GOPHISH_API_KEY')
gmail_username=os.getenv('GMAIL_USERNAME')

gophish = GophishWrapper(api_key)

def update_landing_page(explanation):
    #Load the base html for landing page
    try:
        with open("assets/base_html_page.html", "r") as file:
            html_content = file.read()
    except Exception as e:
        print(f"Error loading base html page: {e}")

    # Parse the HTML content
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the explanation section
    explanation_div = soup.find('div', class_='explanation')

    
    # Modify the explanation content
    explanation_div.clear()  # Clear the current content
    explanation_div.append(BeautifulSoup(explanation, 'html.parser'))  # Add new content

    # Save the updated HTML back to the file
    #with open(self.modified_html, 'w', encoding='utf-8') as file:
    #    file.write(str(soup))
    
    print("HTML updated successfully!")
    return str(soup)

def create_landing_page(landing_page_name, html_content):
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
        pages = gophish.api.pages.get()
        for item in pages:
            if item.name == page.name:
                gophish.api.pages.delete(item.id)
        # Use the API to create the page
        created_page = gophish.api.pages.post(page)
        print(f"Landing page created successfully: ID {created_page.id}")
        return created_page

    except Exception as e:
        print(f"Error creating landing page: {e}")


def beautify_explanation(explanation):
    lines = explanation.split('\n')

    # Remove the leading '*' and any extra whitespace
    points = [line.lstrip('*').strip() for line in lines]
        # Convert points to a beautiful HTML list
    new_explanation_html = ""
    tip_number = 1
    for point in points:
            #if "greeting" in point:
            #    continue
            new_explanation_html += f'<div class="col-md-4"><h1>Reason: #{tip_number}</h1>\n'
            '''
            point = point.lstrip('0123456789.- ')
            point = point.lstrip('**').strip()
            content = point.split('**')
          
            if len(content) == 1:
                    #new_explanation_html += f'<h2>Reason {tip}</h2>\n'
                    new_explanation_html += f'<p>{content[0]}</p>\n'

            elif len(content)==2:
                    new_explanation_html += f'<h2>{content[0]}</h2>\n'
                    new_explanation_html += f'<p>{content[1]}</p>\n'
            '''
            new_explanation_html += f'<p>{point}</p>\n'  
            new_explanation_html += f"</div>\n"
            tip_number +=1
    return new_explanation_html





def process_employee(emp):
    try:
        first_name = emp['FirstName']
        last_name = emp['LastName']
        email = emp["Email"]
        subject = emp['Subject']
        body = emp['body']

        print(f"Processing employee: {first_name} {last_name} ({email})")

        template = Template(name=f"{first_name} {last_name} Template", html=body, subject=subject)
        templates = gophish.api.templates.get()
        for item in templates:
            if item.name == template.name:
                gophish.api.templates.delete(item.id)
            
        template = gophish.api.templates.post(template)

        if not template:
            print(f"Template creation failed for {first_name} {last_name}. Skipping.")
            return

        group = Group(name=f"{first_name} {last_name} Group", targets=[User(first_name=first_name, last_name=last_name, email=email)])
        

        #Check if already a group exist with same name
        #If existing delete that and create the new
        groups = gophish.api.groups.get()
        for item in groups:
            if item.name == group.name:
                gophish.api.groups.delete(item.id)
        
        group = gophish.api.groups.post(group)
        if not group:
            print(f"Target group creation failed for {first_name} {last_name}. Skipping.")
            return

        name = emp['FirstName']+emp['LastName']
        html_content = update_landing_page(beautify_explanation(emp["explanation"]))
        page=create_landing_page(name, html_content)


        smtp_profile = SMTP(name="Gmail SMTP Profile", 
                            host="smtp.gmail.com", port=587, 
                            from_address=os.getenv('GMAIL_USERNAME'),
                            username=os.getenv('GMAIL_USERNAME'),
                            password=os.getenv('GMAIL_PASSWORD'),
                            interface_type="SMTP",
                            ignore_cert_errors=True)
        smtp_list=gophish.api.smtp.get()

        smtp_exists=False
        for smtp in smtp_list:
            if smtp.username==smtp.from_address:
                smtp_profile = SMTP( name=smtp.name,
                            ignore_cert_errors=True)
                smtp_exists=True
                break

        if smtp_exists == False:    
            smtp_profile = gophish.api.smtp.post(smtp_profile)

        if not smtp_profile:
            print(f"SMTP profile creation failed. Skipping campaign creation.")
            return
        
        url="http://127.0.0.1"

        campaign = Campaign(
            name=f"{first_name} {last_name} Campaign",
            groups=[group],
            page=page,
            template=template,
            smtp=smtp_profile,
            url=url
        )

        campaigns = gophish.api.campaigns.get()
        for item in campaigns:
            if item.name == campaign.name:
                gophish.api.campaigns.delete(item.id)

        campaign = gophish.api.campaigns.post(campaign)

        if campaign:
            print(f"Campaign {first_name} {last_name} created successfully with ID {campaign.id}.")
        else:
            print(f"Campaign creation failed for {first_name} {last_name}.")

    except KeyError as e:
        print(f"Missing key in employee data: {e}")
    except Exception as e:
        print(f"Error processing employee {emp.get('FirstName', '')} {emp.get('LastName', '')}: {e}")



def main(input_file= "./assets/emails.json"):
    try:
        with open(input_file, 'r') as f:
            employees = json.load(f)
        
        if not isinstance(employees, list):
            raise ValueError("Expected a list of employees in emails.json.")
        
        for emp in employees:
            process_employee(emp)

    except FileNotFoundError:
        print("The 'emails.json' file was not found.")
    except json.JSONDecodeError:
        print("Error decoding the 'emails.json' file.")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()