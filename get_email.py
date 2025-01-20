import json
import os
import random
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()


def generate_content(prompt,model):
    response = model.generate_content(prompt)
    return response.text.strip()

def configure_genai():
    """Configure the Generative AI API."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError("GEMINI_API_KEY is not set in the environment variables.")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-pro")

def load_json(file_path):
    """Load JSON data from a file."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    except json.JSONDecodeError:
        raise ValueError(f"The file {file_path} is not a valid JSON file.")

def create_role_to_rule_map(email_rules):
    """Create a mapping from roles to email rules."""
    role_map = {}
    for rule in email_rules:
        for role in rule["Roles"]:
            role_map[role] = {
                "Reason": rule["Reason"],
                "CreatedBy": rule["CreatedBy"]
            }
    return role_map


def generate_email_content(model, recipient, sender_role, reason, fake_link):
    """Generate the email body and subject line using the Generative AI model."""
    # Generate email body
    body_prompt = f"""
    Write a professional phishing email for an anti-phishing campaign (professional context):
    - Sender: A person from the {sender_role} department.
    - Recipient: {recipient['FirstName']} {recipient['LastName']} ({recipient['Role']}).
    - Reason: {reason}.
    - Include this fake link naturally: {fake_link}.
    - The email should also be in the {recipient['PreferredLanguage']}.
    Keep it brief, professional, realistic, and ensure the link is prominent but natural.
    The email should be brief, similar in length to the following example:
            "Hello [Name],
            We have rolled out new features on the analytics dashboard to enhance data analysis efficiency. Please review these updates and confirm functionality by accessing the following link:
            [Review Dashboard Features Here]
            Thank you,
            Data Analytics Team"
            Maintain a professional tone, avoid urgency, and ensure the link is prominent but natural.
            Only provide the body of the email, no subject. In the signature, do not say [YOUR NAME], only who created the email.
            Do not specify and specific date or times.
            Do not say "This was generated by ChatGPT" or any indication of that sort.
    """
    email_body = generate_content(body_prompt, model)
  
    # Generate email subject line
    subject_prompt = f"Write a compelling, realistic email subject line for the following email:\n{email_body}. Do not include any specific dates or times."
    email_subject = generate_content(subject_prompt, model)

    return email_subject, email_body

def generate_emails(model, recipients, role_to_rule_map, fake_link, HTML_TEMPLATE,fallback,email_rules):
    """Generate phishing emails for all recipients."""
    emails = []
   
    for recipient in recipients:
        rule = role_to_rule_map.get(recipient["Role"], None)

        # Default values if no specific rule matches
        sender_role = "General Department"
        reason = "General Security Notice"
        if rule:
            sender_role = random.choice(rule["CreatedBy"])
            reason = rule["Reason"]

        if recipient.get("CarLease") and random.random() > 0.5:
            # Filter email rules for "Leasing Department"
            leasing_rules = [rule for rule in email_rules if "Manger Operational Services" in rule["Roles"]]
            if leasing_rules:
                selected_rule = random.choice(leasing_rules)
                reason = selected_rule["Reason"]
                sender_role = random.choice(selected_rule["CreatedBy"])

        elif recipient.get("DependentCount", 0) > 0 and random.random() > 0.5:
            # Filter email rules for "DKV Insurance Management"
            insurance_rules = [rule for rule in email_rules if "DKV Insurance Management" in rule["Roles"]]
            if insurance_rules:
                selected_rule = random.choice(insurance_rules)
                reason = selected_rule["Reason"]
                sender_role = random.choice(selected_rule["CreatedBy"])

        try:
            subject, body = generate_email_content(model, recipient, sender_role, reason, fake_link)
            try:
                # Generate phishing explanation line
                explanation_prompt=f"Reasons why this is a phishing email {body}"
                explanation = generate_content(explanation_prompt,model)
            except:
                 explanation = fallback["explanation"]
        except:
            if not  body:
                body = fallback["body"]
            if not  subject:
                subject= fallback["subject"]
            if not  explanation:
               explanation = fallback["explanation"]
   
           # Fill the HTML template #Basma
        recipient_name = f"{recipient['FirstName']} {recipient['LastName']}"
        
        body = body.replace(fake_link, f'<a href="{fake_link}">{fake_link}</a>')
     

        html_email = HTML_TEMPLATE.format(
            logo="https://logos-world.net/wp-content/uploads/2023/04/Proximus-Logo.png",
            subject=subject,
            recipient_name=recipient_name,
            body=body,
            sender_role=sender_role, 
            link=fake_link
        )

        emails.append({            
            "FirstName": recipient['FirstName'],
            "LastName" : recipient['LastName'],
            "Email" : recipient['Email'],
            "Role": sender_role,            
            "body": html_email,
            "Subject": subject,
            "explanation": explanation
        })

    return emails

def save_emails_to_file(emails, output_file):
    """Save the generated emails to a JSON file."""
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(emails, file, indent=4, ensure_ascii=False)

    print(f"Generated emails have been saved to {output_file}")

def main():
    """Main function to generate phishing emails."""
    # File paths
    employee_file = "./assets/EmployeeInfo.json"
    rules_file = "./assets/email_rules.json"
    output_file = "./assets/emails.json"
    fallback_file = "./assets/fallback.json"
    fake_link = ""  # Replace with your fake link
    html_template_file =  "assets/email_html_template.html"

    try:
        # Load data
        recipients = load_json(employee_file)
        email_rules = load_json(rules_file)
        fallback = load_json(fallback_file)

        try:
            with open(html_template_file, "r") as file:
                email_html_template = file.read()
        except Exception as e:
            print(f"Error loading base html page: {e}")


        # Configure the Generative AI model
        model = configure_genai()

        # Create the role-to-rule map
        role_to_rule_map = create_role_to_rule_map(email_rules)

        # Generate phishing emails
        emails = generate_emails(model, recipients, role_to_rule_map, fake_link,email_html_template,fallback,email_rules)

        # Example: Save emails to HTML files --- to be deleted
        for idx, email in enumerate(emails):
            with open(f"email_{idx + 1}.html", "w", encoding="utf-8") as file:
                file.write(email["body"])
            break

        # Save emails to file
        save_emails_to_file(emails, output_file)

          # Load the JSON file
        with open(output_file, 'r', encoding='utf-8') as file:
            emails = json.load(file)


    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
