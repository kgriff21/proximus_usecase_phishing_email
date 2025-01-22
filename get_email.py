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


def get_body_prompt(prompt,recipient, sender_role, reason, fake_link ):
    """Return body prompt based on prompt type"""
   
    if(prompt == "General"):        
        body_prompt = f"""
        **Parameters:**
        - **Sender**: A person from the `{sender_role}` department.
        - **Recipient**: `{recipient['FirstName']}`.
        - **Purpose of the email**: `{reason}`.
        - **Language**: The email should be written in `{recipient['PreferredLanguage']}`.

        **Guidelines**:
        1. Keep the email brief, professional, and realistic.
        2. Follow this structure and tone:
            Dear [Name],
            We have rolled out new features on the analytics dashboard to enhance data analysis efficiency. Please review these updates and confirm functionality.
            Thank you,
            Data Analytics Team
        3. Maintain a professional tone; avoid any language implying urgency or causing unnecessary alarm.
        4. Use "Dear" to address the recipient, avoiding "Hi" or "Hello."
        5. **Incorporate this fake link naturally and ensure it appears in the email**:
            - As real HTML link text: `<a class="hyperlink">click here</a>`.
            - OR as an HTML button: `<a class="cta">click here</a>`.
            The link must be used in a meaningful and contextually appropriate sentence.
        6. Use "Thank you" followed by `{sender_role}` to close the email.
        7. The email must be concise, no more than 8 sentences.
        8. Provide only the body of the email (no subject line or additional notes).
        9. The signature should include only the sender's role or department (e.g., "Data Analytics Team")—no placeholder names.
        10. Avoid explicitly mentioning dates, times, or indicating that this was AI-generated.
        11. Avoid any mention of placeholders like `[Date]`.
        12. **Ensure the link is part of a sentence and does not stand alone**. For example:
            - "You can <a class="hyperlink">click here</a> to access the updates."
        13. Avoid any generically formatted placeholders.

        **Output format**:  
        Provide only the email body with appropriate line breaks for spacing, following the specified structure and tone.
        """
    elif prompt == "CarLease":
        body_prompt = f"""
        Write a phishing email designed for an anti-phishing campaign related to car lease services.

        **Parameters:**
            Sender: A representative from the {sender_role} department.
            Reason: {reason} (e.g., payment overdue or unauthorized access detection).     
            Language: The email should be written in {recipient['PreferredLanguage']}.
        
        **Guidelines**:
            1. The email must be concise, professional, and realistic.
            2. Maintain a polite and professional tone throughout the email.
            3. Include a plausible call to action, such as:
                - Reviewing lease details.
                - Verifying account security.
                - Addressing overdue payments.
            4. Incorporate this fake link naturally: {fake_link} and show it as following:
                - real html link text <a class="hyperlink">click here</a>'.
                - or html button html <a class="cta">click here</a>'.
                The link must be used in a meaningful and contextually appropriate sentence.
            5. Personalize the email with the recipient’s information:
                - First name: {recipient['FirstName']}
                - Last name: {recipient['LastName']}
            6. Ensure the email mimics a legitimate communication from a car lease service.
            7. Avoid unnecessary urgency or threatening language to maintain credibility.
            8. Avoid placeholders such as `[Your Name]`, `[Date]`, `[Action]`, or any similar placeholders.
            9. Do not include generic statements like "Sincerely, [Your Name]" or "My name is [Your Name]."
            10. Avoid any mentions of dates, times, or phone numbers.
            11. Provide a closing statement that only includes the sender's role or department (e.g., "Car Lease Services Team") in the signature.
            12. Provide only the body of the email (no subject line or additional notes).
            """

    elif prompt == "Insurance":
        body_prompt = f"""
        Write a phishing email designed for an anti-phishing campaign related to hospitalization insurance services:
        - Sender: A representative from the {sender_role} department.
        - Recipient: {recipient['FirstName']} {recipient['LastName']} ({recipient['Role']}).
        - Reason: {reason} (e.g., updating dependent details, pending insurance premiums, or suspicious claims).
        - Provide only the body of the email (no subject line or additional notes).
        - Incorporate this fake link naturally: {fake_link} and show it as following:
            - real html link text <a class="hyperlink">click here</a>'.
            - or html button html <a class="cta">click here</a>'.
        - The email should also be in the {recipient['PreferredLanguage']}.
        - Avoid any generically formatted placeholders such as [[sender_name]], [Company name], [Representative Name], [Your Name].
        - Avoid any mentions to dates or times, or phone number
        - Avoid placeholders such as `[Your Name]`, `[Date]`, `[Action]`, or any similar placeholders
        The email should be brief, professional, and include a logical call to action, such as reviewing the insurance details or confirming coverage updates.
        """
    else:
        body_prompt = "Invalid prompt type provided."
    
    return body_prompt

def generate_email_content(model, recipient, sender_role, reason, prompt, fake_link):
    """Generate the email body and subject line using the Generative AI model."""
  
    body_prompt = get_body_prompt(prompt,recipient, sender_role, reason, fake_link )
    email_body = generate_content(body_prompt, model)
  
    # Generate email subject line
    subject_prompt = f"Write a compelling, realistic brief email subject for the following email:\n{email_body}. Do not include any specific dates or times."
    email_subject = generate_content(subject_prompt, model)

    return email_subject, email_body

def generate_emails(model, recipients, role_to_rule_map, fake_link, HTML_TEMPLATE,fallback,email_rules, config):
    """Generate phishing emails for all recipients."""
    emails = []
   
    for recipient in recipients:
        rule = role_to_rule_map.get(recipient["Role"], None)

        # Default values if no specific rule matches
        sender_role = "General Department"
        reason = "General Security Notice"
        prompt = "General"
        logo = config.get("PROXIMUS_LOGO")
        if rule:
            sender_role = random.choice(rule["CreatedBy"])
            reason = rule["Reason"]

        if (recipient.get("CarLease") and random.random() > 0.5) or (recipient.get("CarLease") and "Alphabet" in sender_role):
            # Filter email rules for "Alphabet" (CarLease)
            leasing_rules = [rule for rule in email_rules if "Alphabet" in rule["CreatedBy"]]
            if leasing_rules:
                selected_rule = random.choice(leasing_rules)
                reason = selected_rule["Reason"]
                prompt = "CarLease"
                logo = config.get("ALPHABET_LOGO")
                sender_role = random.choice(selected_rule["CreatedBy"])

        elif (recipient.get("Insurance") and random.random() > 0.5)  or (recipient.get("Insurance")  in sender_role):
            # Filter email rules for insurance based on recipient's "Insurance" attribute
            insurance_rules = [rule for rule in email_rules
                                if any(recipient["Insurance"] in creator for creator in rule["CreatedBy"])
                ]
            if insurance_rules:
                selected_rule = random.choice(insurance_rules)
                reason = selected_rule["Reason"]
                prompt = "Insurance"
                logo = config.get("DKV_LOGO")
                sender_role = random.choice(selected_rule["CreatedBy"])

        try:
            subject, body = generate_email_content(model, recipient, sender_role, reason, prompt, fake_link)
         
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

        border_color = "#663399" 
        if(logo == config.get("DKV_LOGO")):
            border_color = "#095751"  
   
           # Fill the HTML template #Basma
        html_email = HTML_TEMPLATE.format(
            logo= logo,
            subject=subject,
            body=body,
            sender_role=sender_role,
            border_color=border_color
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

def main(employee_file = "./assets/EmployeeInfo.json", output_file = "./assets/emails.json"):
    """Main function to generate phishing emails."""
    # File paths
    rules_file = "./assets/email_rules.json"
    fallback_file = "./assets/fallback.json"
    fake_link = ""  # Replace with your fake link
    html_template_file =  "assets/email_html_template.html"
    config_file = "config.json"
    

    try:
        # Load data
        recipients = load_json(employee_file)
        email_rules = load_json(rules_file)
        fallback = load_json(fallback_file)
        config = load_json(config_file)

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
        emails = generate_emails(model, recipients, role_to_rule_map, fake_link,email_html_template,fallback,email_rules, config)

        # Example: Save emails to HTML files --- to be deleted
        for idx, email in enumerate(emails):
            with open(f"email_{idx + 1}.html", "w", encoding="utf-8") as file:
                file.write(email["body"])
            break

        # Save emails to file
        save_emails_to_file(emails, output_file)


        #Basma  --- to be deleted
        # Load the JSON file
        with open(output_file, 'r', encoding='utf-8') as file:
            emails = json.load(file)

        # Extract the body of the first email and save it as an HTML file
        for i, email in enumerate(emails):
            html_content = email['body']
            file_name = f"email_Basma{i+1}.html"  # Save each email as a separate file
            with open(file_name, 'w', encoding='utf-8') as html_file:
                html_file.write(html_content)
            print(f"Saved email {i+1} as {file_name}")
        #Basma End

        

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
