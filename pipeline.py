import get_email
import scrape_execs
import gophish_apiv2

#Scrape executives from the Proximus leaders page
scrape_execs.main()

#Generate emails for the users input in EmployeeInfo.json
get_email.main()

#Launch Gophish to send emails to the employee
gophish_apiv2.main()
