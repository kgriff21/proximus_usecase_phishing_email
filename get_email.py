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
        3. Maintain a professional tone; avoid any language implying urgency or causing unnecessary alarm 
        4. Don't use Hi or Hello only Dear .
        5. Use "Thank you" followed by `{sender_role}` to close the email.
        6. The email must be concise, no more than 4-5 sentences.
        7. Provide only the body of the email (no subject line or additional notes).
        8. The signature should include only the sender's role or department (e.g., "Data Analytics Team")—no placeholder names.
        9. Avoid explicitly mentioning dates, times, or indicating that this was AI-generated.
        10. Avoid any mention of clicking links, links themselves or attached files .Instead, provide a complete email with no missing details
        11. Avoid any mention of placeholders like `[Link]`, `[Date]`, `[Action]`.
        12. Avoid any generically formatted placeholders.

        **Output format**:  
        Provide only the email body with appropriate line breaks for spacing, following the specified structure and tone.
        """
    elif prompt == "CarLease":
            body_prompt = f"""
            Write a phishing email designed for an anti-phishing campaign related to car lease services:
            - Sender: A representative from the {sender_role} department.
            - Reason: {reason} (e.g., payment overdue or unauthorized access detection).
            - Incorporate this fake link naturally: {fake_link}.
            - The email should also be in the {recipient['PreferredLanguage']}.
            The email should be concise, professional, and include a plausible call to action, such as reviewing the lease details or verifying account security.
            The email should be similar to the following example:
                "Dear customer,
                We would like to inform you with this message regarding a fine:
                    Driver : {recipient['FirstName']} 
                             {recipient['LastName']}

                This mail is sent you via our partner Unifiedpost.
                More information can be found on our website.
                Through below link {fake_link} you can consult the letter and realted documents.

                Kind regards,
                Manager Opertional Services
                {sender_role}"                
            """
    elif prompt == "Insurance":
        body_prompt = f"""
        Write a phishing email designed for an anti-phishing campaign related to insurance services:
        - Sender: A representative from the {sender_role} department.
        - Recipient: {recipient['FirstName']} {recipient['LastName']} ({recipient['Role']}).
        - Reason: {reason} (e.g., updating dependent details, pending insurance premiums, or suspicious claims).
        - Incorporate this fake link naturally: {fake_link}.
        - The email should also be in the {recipient['PreferredLanguage']}.
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
        prompt = "General"
        if rule:
            sender_role = random.choice(rule["CreatedBy"])
            reason = rule["Reason"]

        if recipient.get("CarLease") and random.random() > 0.5:
            # Filter email rules for "Alphabet" (CarLease)
            leasing_rules = [rule for rule in email_rules if "Alphabet" in rule["CreatedBy"]]
            if leasing_rules:
                selected_rule = random.choice(leasing_rules)
                reason = selected_rule["Reason"]
                prompt = "CarLease"
                sender_role = random.choice(selected_rule["CreatedBy"])

        elif recipient.get("Insurance") and random.random() > 0.5:
            # Filter email rules for insurance based on recipient's "Insurance" attribute
            insurance_rules = [rule for rule in email_rules if recipient["Insurance"] in rule["CreatedBy"]]
            if insurance_rules:
                selected_rule = random.choice(insurance_rules)
                reason = selected_rule["Reason"]
                prompt = "Insurance"
                sender_role = random.choice(selected_rule["CreatedBy"])

        try:
            subject, body = generate_email_content(model, recipient, sender_role, reason, prompt, fake_link)
            #Basma_start
            # Insert the button before the "Thank you" line
            button_html = '<a class="cta">Click Here</a>'
            if "Thank you," in body:
                body = body.replace("Thank you,", f"{button_html}\n\nThank you,")
            else:
                # Fallback if "Thank you," is not present
                body += f"\n\n{button_html}\n\nThank you, {sender_role}"
            #Basma_end
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
        html_email = HTML_TEMPLATE.format(
            logo="https://logos-world.net/wp-content/uploads/2023/04/Proximus-Logo.png",
            subject=subject,
            body=body,
            sender_role=sender_role,
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
