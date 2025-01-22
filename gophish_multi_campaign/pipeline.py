import sys
sys.path.append(r'./')

#from gophish_multi_campaign import get_email
from gophish_multi_campaign import get_email
import scrape_execs
from gophish_multi_campaign import multi_campaign_api

#Scrape executives from the Proximus leaders page
scrape_execs.main()

#Generate emails for the users input in EmployeeInfo.json
get_email.main()

#Launch Gophish to send emails to the employee
multi_campaign_api.main()
