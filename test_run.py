from dotenv import load_dotenv
import os
from gophish_constructor import GophishWrapper

load_dotenv()

api_url = os.getenv('GOPHISH_API_URL')
api_key = os.getenv('GOPHISH_API_KEY')

gophish = GophishWrapper(api_url, api_key)

html = """
<html>
  <body>
    <h1>Security Alert!</h1>
    <p>Your account has been compromised! <a href="https://www.youtube.com/watch?v=t9VyrSxA2Nk">Click here</a> to reset your password immediately.</p>
  </body>
</html>
"""
text = "Security Alert! Your account has been compromised. Visit https://www.youtube.com/watch?v=t9VyrSxA2Nk to reset your password."

template_response = gophish.create_template("Phishing Template", html, text)

if template_response:
    template_id = template_response['id']

    recipients = ["user1@example.com", "user2@example.com", "user3@example.com"]
    group_name = "Test Group"

    group_response = gophish.create_target_group(group_name, recipients)
    
    if group_response:
        group_id = group_response['id']

        campaign_name = "troll kelli"
        phishing_url = "https://www.youtube.com/watch?v=t9VyrSxA2Nk"
        from_address = "angus.mccloud@gmail.com"
        email_subject = "Urgent: Security Alert"

        campaign_response = gophish.create_campaign(campaign_name, template_id, phishing_url, from_address, email_subject, group_id)

        if campaign_response:
            campaign_id = campaign_response['id']

            campaign_results = gophish.get_campaign_results(campaign_id)
            if campaign_results:
                print(campaign_results)

            campaign_report = gophish.get_campaign_report(campaign_id)
            if campaign_report:
                print(campaign_report)
        else:
            print("Failed to create the campaign.")
    else:
        print("Failed to create the target group.")
else:
    print("Failed to create the template.")
