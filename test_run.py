from dotenv import load_dotenv
import os
from gophish_constructor import GophishWrapper

load_dotenv()

api_url = os.getenv('GOPHISH_API_URL')
api_key = os.getenv('GOPHISH_API_KEY')

gophish = GophishWrapper(api_url, api_key)

# Step 1: Create SMTP Profile
smtp_response = gophish.create_smtp_profile(
    name="Gmail SMTP Profile",
    host="smtp.gmail.com",
    port=587,
    username="angus.mccloud@gmail.com",  # Replace with your Gmail address
    password=os.getenv('GMAIL_APP_PASSWORD'),  # Store Gmail app password in .env for security
    from_address="angus.mccloud@gmail.com",  # Same as username
    tls="tls"
)

if smtp_response:
    smtp_profile_id = smtp_response['id']

    # Step 2: Create the Phishing Template
    html = """
    <html>
      <body>
        <h1>User Discretion Is Adivced!</h1>
        <p>Your booty has been targeted with PsyTrance! <a href="https://www.youtube.com/watch?v=t9VyrSxA2Nk">Click here</a> to start tripping balls (psychelics required).</p>
      </body>
    </html>
    """
    text = "SYour booty has been targeted with PsyTrance!. Visit https://www.youtube.com/watch?v=t9VyrSxA2Nk to start tripping balls (psychelics required!)."

    template_response = gophish.create_template("Phishing Template", html, text)

    if template_response:
        template_id = template_response['id']

        # Step 3: Create a Target Group
        recipients = ["kelligriffin49@gmail.com"]
        group_name = "Test Group"
        group_response = gophish.create_target_group(group_name, recipients)

        if group_response:
            group_id = group_response['id']

            # Step 4: Create Campaign with SMTP Profile
            campaign_name = "Troll Kelli"
            phishing_url = "https://www.youtube.com/watch?v=t9VyrSxA2Nk"
            from_address = None
            email_subject = "Urgent: Security Alert"

            campaign_response = gophish.create_campaign(
                campaign_name, template_id, phishing_url, from_address, email_subject, smtp_profile_id
            )

            if campaign_response:
                campaign_id = campaign_response['id']

                # Step 5: Get Campaign Results
                campaign_results = gophish.get_campaign_results(campaign_id)
                if campaign_results:
                    print(campaign_results)

                # Step 6: Get Campaign Report
                campaign_report = gophish.get_campaign_report(campaign_id)
                if campaign_report:
                    print(campaign_report)
            else:
                print("Failed to create the campaign.")
        else:
            print("Failed to create the target group.")
    else:
        print("Failed to create the template.")
else:
    print("Failed to create SMTP profile.")

