from flask import Flask
from flask_mail import  Mail, Message

###Mail stuff###
app = Flask(__name__)
mail = Mail (app)

#Mail config
#UPDATE when we have our own address and mail server
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'modularyo@gmail.com'
app.config['MAIL_PASSWORD'] = 'Dhub6969'
#Set to allow less secure apps to access via https://myaccount.google.com/lesssecureapps?pli=1 
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['DEBUG'] = True
#app.config['MAIL_DEBUG'] = True #commented out because of DEBUG already set to True, this inherits the value
app.config['MAIL_MAX_EMAILS'] = 5 #so we don't accidnetly send 10,000,000 emails
app.config['MAIL_DEFAULT_SENDER'] = ('Specify and Update Here', 'modularyo@gmail.com')  #tuple #default "FROM" if not specified
#app.config['MAIL_SUPRRESS_SEND'] = False #change depending on what testing we're doing
mail = Mail (app)

# message object mapped to a particular URL ‘/’ 
@app.route("/") 
def index(): 
    msg = Message( 
                'Hello', 
                #sender ='modularyo@gmail.com', #We can remove this since defined a default sender.
                #Specified default sender already -- not needed
               
                ########     UPDATE      ########
                recipients = ['bobafetch@yopmail.com'] 
                ########     UPDATE      ########
            ) 
    msg.body = 'Hello Flask message sent from Flask-Mail'
    #Can also use HTML instead.
    mail.send(msg) 
    #needs more variables for more people. Also wont send more than configed for MAIL_MAX_EMAILS
    return 'Sent'
   
if __name__ == '__main__': 
    app.run(debug = True) 