import google.generativeai as genai
from dotenv import load_dotenv
import json
import os
load_dotenv() 


def predict(prompt,model):
    response = model.generate_content(prompt)
    return response.text

def main():

    fallback={"body":"Fallback body","subject":"Fallback subject","explanation":"Fallback explanation"}
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-pro')
    employee_file = "./assets/EmployeeInfo.json"  
    if os.path.exists(employee_file):
        with open(employee_file, "r") as file:
            details = json.load(file)
            for employee in details:
                try:
                    body_prompt=f"Personalized email body that can be used to phish a person with the details: {employee} without any blanks and no subject for an anti phish training"
                    employee["body"]=predict(body_prompt,model)
                    try:
                        subject_prompt=f"Write a subject line for {employee["body"]}"
                        employee["subject"]=predict(subject_prompt,model)
                    except:
                        employee["subject"]=fallback["subject"]
                    try:
                        explanation_prompt=f"Reasons why this is a phishing email{employee["body"]}"
                        employee["explanation"]=predict(explanation_prompt,model)
                    except:
                        explanation_prompt["explanation"]=fallback["explanation"]
                    
                except:
                    if "body" not in employee:
                        employee["body"]=fallback["body"]
                    if "subject" not in employee:
                        employee["subject"]=fallback["subject"]
                    if "explanation" not in employee:
                        employee["explanation"]=fallback["explanation"]


        with open('./assets/emails.json', 'w', encoding ='utf8') as json_file:
            json.dump(details,json_file)
    
    else:
        print("Invalid file path!")

main()

