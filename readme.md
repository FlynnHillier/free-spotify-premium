# Description
This project utilises undetected chromedriver to automatically claim usable free spotify premium accounts.

#### demo
https://youtu.be/9Ut2RB4x21c

## Questions
#### How does it work?
This works by utilsing the 3 month free spotify premium that spotify periodically offers to new users. By generating new accounts, this promotion is capable of being claimed. Then by using the official spotify developer API, playlists from previous accounts can be copied onto the newly generated accounts, making them instantly usable.

#### why are my card details required?
A valid set of card details are required to sign up to spotify premium, even their free premium-promotions. While this is the case, *your card is* __*not*__ *charged*. Feel free to look through the code, it is more than reasonable to be cautious entering such details into foreign code.

#### how many cards do i need?
Spotify only allows for users to claim a promotion *once per set of card details*. This means if you wish to create multiple accounts, a proportionate amount of extra card details are required. I recommend utiling the virtual-bank 'revolut' which offers up to 20 virtual cards which can be created/deleted free of charge and very-often. By creating a card, then deleting it after use - an unlimited amount of card details is accessible. (Note, if using revolut, the 'disposable' virtual card will not be accepted by spotify)


# Setup

## dependencies
Install the required dependencies by running the command:

`pip install -r requirements`


## spotify developer
To generate the tokens required to access spotify's public API, use [this link](https://developer.spotify.com/dashboard/create) to create an application.


## enviroment variables
Create a file named `.env` in the top level directory. Populate it with the following keys.
- SPOTIFY_CLIENT_ID
- SPOTIFY_CLIENT_SECRET
- SPOTIFY_REDIRECT_URI 
- SPOTIFY_USERNAME <\optional> 

## main.py
To use the functionality provided in main.py, fill in the variables at the top of the script.

Provide variables at top of script in `main.py`

- **rip_playlists_target_id**\
the id of the spotify user from which all said user's playlists will be copied onto the new user's account.
- **premium_promotion_url**\
the url of the current free premium spotify promotion

- **developer_cookies_fp**\
a filepath at which cookies will be stored for the spotify session of the account under which the spotify developer dashboard is set up.

- **dev_email**\
the email of the spotify account under which the developer dashboard is setup. (the account for which you did [this step](#spotify-developer))

- **dev_pass**\
the password of the spotify account under which the developer dashboard is setup. (the account for which you did [this step](#spotify-developer))

- **card details**\
the card detail's variables are self-explanitory. See [here](#why-are-my-card-details-required) for why they're needed.



# Usage
run main.py and follow the instructions as they're provided.

It is worth mentioning a few steps require manual interaction. Most notably, it is likely spotify will request additional confirmation on your card, which you must confirm on whatever device you bank on.
