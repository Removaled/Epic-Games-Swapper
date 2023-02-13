from colorama import Fore, init
from time import sleep, time
from os import system, name, _exit
from threading import Thread
from discord_webhook import DiscordWebhook, DiscordEmbed

import requests
import pycurl
import colorama

init()

swapper = ''
webhook = 'https://discord.com/api/webhooks/'

class FN(object):
    def __init__(self):

        self._user_being_swapped = None
        self._swapping_user_to = None
        self._current_claim_user = None

        self._release_auth_token = None
        self._claim_auth_token = None
        
        self._release_accountId = None
        self._claim_accountId = None

        self._time_release = None
        self._time_claim = None
        self._swap_time = None

        self._claimed = False
        self._done = False
        self._released = False
        

        self._missed = False
        self.retry_att = 0

    def get_auth(self, webcode):
        headers = {"Authorization": "Basic MzQ0NmNkNzI2OTRjNGE0NDg1ZDgxYjc3YWRiYjIxNDE6OTIwOWQ0YTVlMjVhNDU3ZmI5YjA3NDg5ZDMxM2I0MWE="}
        data = {"grant_type": "authorization_code", "code": webcode}
        r = requests.post("https://account-public-service-prod03.ol.epicgames.com/account/api/oauth/token", data=data, headers=headers).json()


        headers = {"Authorization": "Bearer " + r['access_token']}
        r = requests.get("https://account-public-service-prod03.ol.epicgames.com/account/api/oauth/exchange", headers=headers).json()

        headers = {
            "Authorization": "Basic ZWZlM2NiYjkzODgwNGM3NGIyMGUxMDlkMGVmYzE1NDg6NmUzMWJkYmFlNmE0NGYyNTg0NzQ3MzNkYjc0ZjM5YmE=", 
            "User-Agent":"EOS-SDK/1.8.0-14249203 (Windows/6.2.9200.1.768.64bit) Rocket League/201210.63594.304380"
        }
        data = {"grant_type": "exchange_code", "exchange_code": r['code']}
        r = requests.post("https://account-public-service-prod03.ol.epicgames.com/account/api/oauth/token", headers=headers, data=data).json()

        return (r["access_token"],r["account_id"],r["displayName"])

    def check_swappable(self,access_token,accountId,username):
        headers = {'Authorization':f'Bearer {access_token}','Content-Type':'application/json','Connection':'keep-alive',}
        data = bytes('{"displayName":"'+ username +'"}', encoding='utf-8')

        r = requests.put(f'https://account-public-service-prod03.ol.epicgames.com/account/api/public/account/{accountId}',headers=headers,data=data)
    
        if b'"canUpdateDisplayName":true,' in r.content:
            return True

    def http_apply(self, curl):
        curl.setopt(pycurl.URL,f'https://account-public-service-prod03.ol.epicgames.com/account/api/public/account/{self._claim_accountId}')
        curl.setopt(pycurl.SSL_VERIFYPEER, 0)
        curl.setopt(pycurl.CUSTOMREQUEST,'PUT')
        curl.setopt(pycurl.HTTPHEADER,[f'Authorization: Bearer {self._claim_auth_token}','Content-Type: application/json','Connection: keep-alive'])
        curl.setopt(pycurl.POSTFIELDS,bytes('{"displayName":"'+ self._user_being_swapped +'"}', encoding='utf-8'))

        return curl.perform_rs()

    def http_release(self, curl):
        curl.setopt(pycurl.URL,f'https://account-public-service-prod03.ol.epicgames.com/account/api/public/account/{self._release_accountId}')
        curl.setopt(pycurl.SSL_VERIFYPEER, 0)
        curl.setopt(pycurl.CUSTOMREQUEST,'PUT')
        curl.setopt(pycurl.HTTPHEADER,[f'Authorization: Bearer {self._release_auth_token}','Content-Type: application/json','Connection: keep-alive'])
        curl.setopt(pycurl.POSTFIELDS,bytes('{"displayName":"'+ self._swapping_user_to +'"}', encoding='utf-8'))

        return curl.perform_rs()

            
    def release(self, delay):
            sleep(delay)

            if'"canUpdateDisplayName":false' in self.http_release(pycurl.Curl()): 
                self._time_release = time()
                self._released = True
                print(f"\n[{Fore.MAGENTA}?{Fore.RESET}] @{self._user_being_swapped} has been released!") 

            else: print(f"Couldnt release @{self._user_being_swapped} | {time()}")

    def swap(self, delay):
        sleep(delay)
        try:

            if '"canUpdateDisplayName":false' in self.http_apply(pycurl.Curl()): 
                self._time_claim = time()
                self._claimed = True

            else:
                self.retry_att += 1

                if self.retry_att == 4:
                    self._missed = True

        except: pass

    def initiate_swap(self):
        times = [0.119, 0.118, 0.098, 0.076, 0.056, 0.030]
            
        threads = []
        for x in times:
            threads.append(Thread(target=self.swap, args=(x,))) 
                
        for x in threads:
            x.start()
            
        Thread(target = self.release, args=(0,)).start()


def send_public_webhook(username,swap_time):
    try:
        swap_time_ms = f'{swap_time}ms'
        send_req = DiscordWebhook(url=webhook)
        embed = DiscordEmbed(title='New Swap!', description=f'**Username**: {username} \n**Time Taken**: {swap_time_ms}', color='23272A')
        embed.set_footer(text="So Fast Bro")
        embed.set_thumbnail(url='https://i.imgur.com/Gr1yyE5.png')
        send_req.add_embed(embed)
        send_req.execute()
    except:
        print('\nInvalid Webhook')
        _exit(0)

    return 


def Launch():
    try:
        Swapper = FN()
        print(f"[{Fore.MAGENTA}*{Fore.RESET}] owo Swapper\n")

        print(f"[{Fore.MAGENTA}*{Fore.RESET}] Webcode Link: https://www.epicgames.com/id/api/redirect?clientId=3446cd72694c4a4485d81b77adbb2141&responseType=code\n")

        current_user_webcode = input(f"[{Fore.YELLOW}>{Fore.RESET}] Web Code containing the handle you want swapped: ")
        log_swapper_release = Swapper.get_auth(current_user_webcode)

        Swapper._release_auth_token = log_swapper_release[0]
        Swapper._release_accountId = log_swapper_release[1]
        Swapper._user_being_swapped = log_swapper_release[2]

        if Swapper.check_swappable(log_swapper_release[0],log_swapper_release[1],log_swapper_release[2]) != True:
            print(f"\n[{Fore.RED}-{Fore.RESET}] Cannot Swap this User, Exiting program...")
            _exit(0)
        
        print(f"\n[{Fore.MAGENTA}+{Fore.RESET}] Target is swappable! Current Target: {log_swapper_release[2]}")

        claim_webcode = input(f"[{Fore.YELLOW}>{Fore.RESET}] Web Code to the account you want the target on: ")
        log_swapper_claim = Swapper.get_auth(claim_webcode)

        Swapper._claim_auth_token = log_swapper_claim[0]
        Swapper._claim_accountId = log_swapper_claim[1]
        Swapper._current_claim_user = log_swapper_claim[2]

        if Swapper.check_swappable(log_swapper_claim[0],log_swapper_claim[1],log_swapper_claim[2]) != True:
            print(f"\n[{Fore.RED}-{Fore.RESET}] Cannot Swap To this User, Exiting program...")
            _exit(0)

        Swapper._swapping_user_to = input(f"[{Fore.YELLOW}>{Fore.RESET}] What would you like to swap the target handle to: ")

        print(f"\n[{Fore.MAGENTA}!{Fore.RESET}] Moving onto confirmation...")
        sleep(2)

        system('cls' if name == 'nt' else 'clear')
        init()

        print(f"[{Fore.MAGENTA}*{Fore.RESET}] owo Swapper\n")

        print(f"[{Fore.YELLOW}!{Fore.RESET}] Username Being Swapped: {Fore.MAGENTA}@{Swapper._user_being_swapped}{Fore.RESET}")
        print(f"[{Fore.YELLOW}!{Fore.RESET}] Current Handle on Claim Account: {Fore.MAGENTA}@{Swapper._current_claim_user}{Fore.RESET}")
        print(f"[{Fore.YELLOW}!{Fore.RESET}] Swapping Username To: {Fore.MAGENTA}@{Swapper._swapping_user_to}{Fore.RESET}")

        input(f"\n[{Fore.YELLOW}>{Fore.RESET}] Press Enter To Swap {Fore.MAGENTA}@{Swapper._user_being_swapped}{Fore.RESET}")

        Swapper.initiate_swap()

        while not Swapper._done:
            if Swapper._claimed:
                Swapper._swap_time = int(Swapper._time_claim * 1000 - Swapper._time_release * 1000)
                print(f"[{Fore.GREEN}+{Fore.RESET}] Claimed @{Swapper._user_being_swapped}")
                print(f"[{Fore.GREEN}+{Fore.RESET}] Succesfully Swapped {Fore.MAGENTA}@{Swapper._user_being_swapped}{Fore.RESET} in {Fore.MAGENTA}{Swapper._swap_time}ms{Fore.RESET}")
                send_public_webhook(Swapper._user_being_swapped,str(Swapper._swap_time))
                Swapper._done = True

            elif Swapper._missed:
                print(f"[{Fore.GREEN}-{Fore.RESET}] Missed @{Swapper._user_being_swapped}")
                Swapper._done = True

    except KeyboardInterrupt:
        print('\nExited')

Launch()
