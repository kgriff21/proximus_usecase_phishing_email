import json
import os
from dotenv import load_dotenv
from gophish_constructor import GophishWrapper

load_dotenv()

api_url = os.getenv('GOPHISH_API_URL')
api_key = os.getenv('GOPHISH_API_KEY')


def check_env_variables():
    required_env_vars = ['GOPHISH_API_URL', 'GOPHISH_API_KEY', 'GMAIL_USERNAME', 'GMAIL_APP_PASSWORD']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]

    if missing_vars:
        print(f"Missing environment variables: {', '.join(missing_vars)}")
        return False
    return True

if not check_env_variables():
    exit(1)

gophish = GophishWrapper(api_url, api_key)

def create_smtp_profile():
    try:
        smtp_profiles = gophish.get_smtp_profiles()
        if smtp_profiles and isinstance(smtp_profiles, list):
            return smtp_profiles[0]['id']
        
        smtp_response = gophish.create_smtp_profile(
            name="Gmail SMTP Profile",
            host="smtp.gmail.com",
            port=587,
            username=os.getenv('GMAIL_USERNAME'),
            password=os.getenv('GMAIL_APP_PASSWORD'),
            from_address=os.getenv('GMAIL_USERNAME'),
            tls=False,
        )
        if smtp_response:
            return smtp_response['id']
        else:
            print("Failed to create SMTP profile.")
            return None
    except Exception as e:
        print(f"Error creating SMTP profile: {e}")
        return None

def create_template(first_name, last_name, subject, body):
    try:
        template_response = gophish.create_template(
            name=f"{first_name} {last_name} Template", 
            subject=subject, 
            html=body, 
            text=body  # If you want to provide both HTML and Text versions
        )
        if template_response:
            return template_response['id']
        else:
            print(f"Failed to create template for {first_name} {last_name}")
            return None
    except Exception as e:
        print(f"Error creating template: {e}")
        return None

def create_target_group(group_name, recipients):
    try:
        group_response = gophish.create_target_group(group_name, recipients)
        if group_response:
            return group_response['id']
        else:
            print(f"Failed to create target group {group_name}.")
            return None
    except Exception as e:
        print(f"Error creating target group: {e}")
        return None

def create_campaign(campaign_name, template_id, phishing_url, smtp_profile_id, from_address=None):
    try:
        campaign_response = gophish.create_campaign(
            campaign_name, template_id, phishing_url, from_address, smtp_profile_id
        )
        if campaign_response:
            return campaign_response['id']
        else:
            print(f"Failed to create campaign {campaign_name}.")
            return None
    except Exception as e:
        print(f"Error creating campaign: {e}")
        return None

def process_employee(emp):
    try:
        first_name = emp['FirstName']
        last_name = emp['LastName']
        email = emp['Email']
        subject = emp['Subject']
        body = emp['body']

        print(f"Processing employee: {first_name} {last_name} ({email})")

        # Create phishing template
        template_id = create_template(first_name, last_name, subject, body)
        if not template_id:
            print(f"Template creation failed for {first_name} {last_name}. Skipping.")
            return

        # Create target group
        group_name = f"{first_name} {last_name} Group"
        group_id = create_target_group(group_name, [email])
        if not group_id:
            print(f"Target group creation failed for {first_name} {last_name}. Skipping.")
            return

        phishing_url = "!PLACEHOLDER!"  # Replace with actual phishing URL when ready
        campaign_name = f"{first_name} {last_name} Campaign"

        # Create SMTP profile
        smtp_profile_id = create_smtp_profile()
        if not smtp_profile_id:
            print("SMTP profile creation failed. Skipping campaign creation.")
            return

        # Create campaign
        campaign_id = create_campaign(campaign_name, template_id, phishing_url, smtp_profile_id)
        if campaign_id:
            print(f"Campaign {campaign_name} created successfully with ID {campaign_id}.")
        else:
            print(f"Campaign creation failed for {campaign_name}.")
    except KeyError as e:
        print(f"Missing key in employee data: {e}")
    except Exception as e:
        print(f"Error processing employee {emp.get('FirstName', '')} {emp.get('LastName', '')}: {e}")

def main():
    try:
        # Load employee data from the file
        with open('emails.json', 'r') as f:
            employees = json.load(f)
        
        # Validate if employees data is a list
        if not isinstance(employees, list):
            raise ValueError("Expected a list of employees in emails.json.")
        
        # Process each employee
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


