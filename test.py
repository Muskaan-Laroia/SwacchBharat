import sendgrid
from sendgrid.helpers.mail import *

sendgrid_key="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"
sg = sendgrid.SendGridAPIClient(apikey=(sendgrid_key))
from_email = Email("muskaanlaroia@gmail.com")
to_email = Email("khannapalak@gmail.com")
subject = "hiiiiiii"
content = Content("text/plain", "Swacch Bharat team welcomes you!\n We hope you like sharing the images of your surroundings to help us build a cleaner india /n")
mail = Mail(from_email, subject, to_email, content)
response = sg.client.mail.send.post(request_body=mail.get())
print(response.status_code)
print(response.body)
print(response.headers)
