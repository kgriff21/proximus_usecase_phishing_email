import sys
sys.path.append(r'./')

from gophish_single_campaign import get_email
import scrape_execs
from gophish_single_campaign import single_campaign

#Scrape executives from the Proximus leaders page
scrape_execs.main()

#Generate emails for the users input in EmployeeInfo.json
get_email.main()

#Launch Gophish to send emails to the employee
single_campaign.main()
