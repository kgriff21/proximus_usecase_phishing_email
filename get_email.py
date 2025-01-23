import json
import os
import random
from dotenv import load_dotenv
import google.generativeai as genai
import time

# Load environment variables
load_dotenv()


def generate_content1(prompt,model):
    response = model.generate_content(prompt)
    if not response.parts:
        # Add a delay to ensure the model isn't overloaded
        # To avoid  Error generate_content(): 429 Resource has been exhausted 
        # (e.g. check quota).
        print("Error: No valid parts in the response.")
        time.sleep(1)
        return generate_content(prompt,model)

    text = response.parts[0].text if response.parts else ""
    return text.strip()

def generate_content(prompt, model, max_tokens=300):
  retry_count = 0
  while True:
    response = model.generate_content(prompt)
    text = response.text.strip() if response.text else ""
    if len(text.split()) <= max_tokens:
      return text
    else:
      print(f"Text length ({len(text.split())}) exceeds limit ({max_tokens})")
      retry_count += 1
      delay = min(2**retry_count, 60)  # Maximum delay of 60 seconds
      print(f"Retrying after {delay} seconds...")
      time.sleep(delay)
      # Retry only when the text length exceeds the limit
      continue 

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

url = r"{{.URL}}"
def get_body_prompt(prompt,recipient, sender_role, reason, fake_link ):
    """Return body prompt based on prompt type"""
    if(prompt == "General"):  
        anti_phish_campaign = "Simulate a phishing email for anti-phishing training."  
    elif(prompt == "Insurance"):    
         anti_phish_campaign = " Simulate a phishing email for anti-phishing training related to hospitalization insurance services:"
    elif(prompt == "CarLease"):  
        anti_phish_campaign= "Simulate a phishing email for anti-phishing training related to car lease services:" 
        
    body_prompt = f"""
        - {anti_phish_campaign} .
        - Sender: {sender_role} department, {sender_role} if name of person don't include department.
        - Recipient: {recipient['FirstName']} {recipient['LastName']}.
        - Reason: {reason} (e.g., update details, insurance).
        - Body only: 6-8 sentences.
        - Include link: <a href='{url}' class="hyperlink">click here</a> or <a href='{url}' class="cta">click here</a>.
        - Language: {recipient['PreferredLanguage']}.
        - Avoid providing subject, only body mail.
        - Avoid: Dates, times, phone numbers, placeholders, attachments.
        - Call to action: Review details/confirm updates.
        - Output: Email body with line breaks."
        Key Optimizations:
        - Removed redundant phrases: "professional context," "realistic simulation for better reflect real-world threats," "concise, brief" (implied by sentence count).
        - Shortened phrases: "updating dependent details" to "update details," "pending insurance premiums" to "insurance."
        - Removed unnecessary words: "Provide only the body of the email" (already implied by "Body only").
        - Simplified language: "Incorporate a simulated phishing link naturally" to "Include link."
        - Condensed disclaimer: The disclaimer can be significantly shortened or removed entirely if it's provided separately from the prompt.
        This optimized prompt is significantly shorter while maintaining the core requirements and clarity.
        Remember:
            Adjust the level of detail based on the specific needs and token limits of the language model you are using.
            
    """
    return body_prompt

def generate_email_content(model, recipient, sender_role, reason, prompt, fake_link):
    """Generate the email body and subject line using the Generative AI model."""

    body_prompt = get_body_prompt(prompt,recipient, sender_role, reason, fake_link )
    email_body = generate_content(body_prompt, model)
  
    # Generate email subject line
    subject_prompt = f"""Write a compelling, realistic brief email subject for the following email:\n{email_body}.
    - Do not include any specific dates or times. 
    - Do not include any placeholders
    - Do not express urgency or create a sense of alarm
    - Language: {recipient['PreferredLanguage']}."""

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


        # Define the weights for each category
        weights = {
            "General": 0.5,      # 50%
            "CarLease": 0.2,     # 20%
            "Insurance": 0.3     # 30%
        }

        # Determine applicable categories and their weights
        applicable_categories = []
        applicable_weights = []
       
        applicable_categories.append("General")
        applicable_weights.append(weights["General"])
        if recipient.get("CarLease"):
            applicable_categories.append("CarLease")
            applicable_weights.append(weights["CarLease"])
        if recipient.get("Insurance"):
            applicable_categories.append("Insurance")
            applicable_weights.append(weights["Insurance"])

        # Normalize weights to ensure they sum to 1
        total_weight = sum(applicable_weights)
        normalized_weights = [w / total_weight for w in applicable_weights]

        # Select a category based on the normalized weights
        selected_category = random.choices(applicable_categories, weights=normalized_weights, k=1)[0]

        print(selected_category)

        # Apply rules for the selected category
        if selected_category == "General":
            if rule:
                sender_role = random.choice(rule["CreatedBy"])
                reason = rule["Reason"]         
       
        elif selected_category == "CarLease":
            # Filter rules for "CarLease"
            carlease_rules = [
                rule for rule in email_rules if "Alphabet" in rule["CreatedBy"]
            ]
            if carlease_rules:
                selected_rule = random.choice(carlease_rules)
                reason = selected_rule["Reason"]
                prompt = "CarLease"
                logo = config.get("ALPHABET_LOGO")
                sender_role = random.choice(selected_rule["CreatedBy"])

        elif selected_category == "Insurance":
            # Filter rules for "Insurance"
            insurance_rules = [
                rule for rule in email_rules
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
                time.sleep(1) 
                explanation_prompt=f"""Reasons why this is a phishing email {body}"""
                explanation = generate_content(explanation_prompt,model)
            except:
                explanation = fallback[0]["explanation"]

            border_color = "#663399" 
            if(logo == config.get("DKV_LOGO")):
                border_color = "#095751" 
            html_email = HTML_TEMPLATE.format(
                logo= logo,
                subject=subject,
                body=body,
                sender_role=sender_role,
                border_color=border_color
            ).strip() 
        
        except:          
            html_email = fallback[0]["body"]        
            subject= fallback[0]["subject"]        
            explanation = fallback[0]["explanation"]
 
    
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
    fake_link = ""
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
