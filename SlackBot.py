import os, time, slackclient
import random
from datetime import datetime


# delay in seconds before checking for new events 
SOCKET_DELAY = 3

# slackbot environment variables
SLACK_NAME = os.environ.get('SLACK_NAME') 
SLACK_TOKEN = os.environ.get('SLACK_TOKEN') 
SLACK_ID = os.environ.get('SLACK_ID')

# spajanje na slack api
slack_client = slackclient.SlackClient(SLACK_TOKEN)
   
# inicijalno deklariranje praznog array-a u koji poslje postavljamo usere koji su napisali poruku
users=[]

#odgovara samo na poruke u channelu koji smo stavili i ne odgovara SLACK botovima (subtype is None) i razlicito od naseg bot-a da ne salje sam sebi poruke (user!=SLACK_ID)
#channel=='######' (testbot channel)
def spec_channel(event):
    """Bot odgovara samo ako je u navedenim channelima i ako je tip poruka"""
    type = event.get('type')
    channel=event.get('channel')
    user = event.get('user')
    subtype= event.get('subtype') 
    if type and type == 'message' and (channel=='######' or channel=='######')  and user!=SLACK_ID and subtype is None : 
        return True

# kreiranje poruke (post) na slacku, spajanje na api za kananle koji su postavljenji
def post_message(message, channel,user):       
#    ako user prvi puta salje poruku odgovori mu i dodaj user id u array (provjera da istom useru ne saljemo isti odgovoru u istom danu vise puta)

    if user in users:
        return None
    else:
        users.extend([user]) 
        slack_client.api_call('chat.postMessage', channel=channel,
                      text=message, as_user=True)           
        print(users)
    
#output poruka koju zelimo ispisati na slacku
def say_mssg(user_mention):
    """Team Db message"""
#    random.choice ukoliko zelimo imati vise odgovora pa da random izbacuje
    response_template = random.choice(["{mention} Outside office hours for urgent matters please call...."])
    return response_template.format(mention=user_mention)

#  kada poslati poruku (vikend i poslje radnih sati radnim danima)
#  zovemo funkciju za post poruke na slack
def handle_message(message, user, channel, day_bot,hour_bot, min_bot):
    if  day_bot in ['Saturday','Sunday'] or (hour_bot < 8 or hour_bot > 16):
        user_mention = '<@{user}>'.format(user=user)
        post_message(message=say_mssg(user_mention), channel=channel,user=user)
    else:
        return None

# funkcija koja pokrece spajanje na slack api i pinga svake sekunde slack server (prati sve akcije, pisanje, aktivnost...)
def run():
    if slack_client.rtm_connect():
        print('Machine is ON...')
        while True:
            event_list = slack_client.rtm_read()         
            #  vrijeme poruke radi provjere kada slati odgovor i kada napraviti reset users arraya  
            now = datetime.now()
            day_bot= now.strftime("%A") #dan
            hour_bot= int(now.strftime('%H'))+1 #sat UTC + 2 po ljetnom vremenu, po zimskom smanjiti na  +1
            min_bot= int(now.strftime('%M')) #minute
            # reset arraya u ponoc , tu minutu brisemo sve usere koji su poslali za poruku tako da za novi dan opet im saljemo odgovore
            if hour_bot==24 and min_bot==0:
                del users[:]
            # ako imamo message od usera, pozovi funkciju handle_message koji provjerava dan i vrijeme i poziva funkciju za post poruke na slack
            if len(event_list) > 0:
                for event in event_list:     
                    if spec_channel(event):
                        handle_message(message=event.get('text'), user=event.get('user'), channel=event.get('channel'), hour_bot=hour_bot,min_bot=min_bot,day_bot=day_bot)                       
            time.sleep(SOCKET_DELAY)
    else:
        print('[!] Connection to Slack failed.')

    
if __name__=='__main__':
    run()