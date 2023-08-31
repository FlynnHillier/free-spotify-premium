import os

from premium_flow import premium_account_gen_flow
from playlists import rip_all_playlists
from SpotifyDeveloperSession import SpotifyDeveloperSession

from spotipy.oauth2 import SpotifyOAuth
from spotipy import Spotify
from pathlib import Path

premium_promotion_url = "https://www.spotify.com/purchase/offer/2023-midyear-v2-trial-3m" #augaust 2023

rip_playlists_from_user_target_id = ""

developer_cookies_fp = "admin.pkl"

dev_email = os.getenv("DEV_EMAIL")
dev_pass = os.getenv("DEV_PASS")

card_number = os.getenv("CARD_NUMBER")  # xxxxxxxxxxxxxxxx
card_exp_month = os.getenv("CARD_EXP_MONTH") # xx
card_exp_year = os.getenv("CARD_EXP_YEAR") # xx
card_cvv = os.getenv("CARD_CVV") # xxx


def main():

    ## initialise developer session

    if Path(developer_cookies_fp).exists():
        #load with cookies
        dev_sess = SpotifyDeveloperSession(cookies_fp=developer_cookies_fp)
    else:
        #load without cookies
        dev_sess = SpotifyDeveloperSession()


    if not dev_sess.spotify_is_logged_in():
        #log developer in
        dev_login_success = dev_sess.spotify_log_in(dev_email,dev_pass)

        if not dev_login_success:
            print("failed to log in developer account")
            return False
        else:
            print(f"logged in developer account: {dev_email}")
    
    #resave developer cookies
    dev_sess.save_cookies(developer_cookies_fp)

    new_user_email,new_user_pass,new_user_username,is_premium_activated,is_premium_cancelled = premium_account_gen_flow(
        premium_promotion_url=premium_promotion_url,
        card_number=card_number,
        card_exp_month=card_exp_month,
        card_exp_year=card_exp_year,
        card_cvv=card_cvv
    )

    if new_user_email == "" or not is_premium_activated:
        return False

    if is_premium_activated and not is_premium_cancelled:
        print("\n!!MANUALLY CANCEL SUBSCRIPTION, premium activated but not cancelled!!")
        print(f"email: {new_user_email}")
        print(f"password: {new_user_pass}\n")
        return False
    

    dev_sess.delete_all_dashboard_users()
    dev_sess.add_dashboard_user(new_user_email)

    print(f"added {new_user_email} to application dashboard.")


    print("\nmanually authenticate with user credentials:")
    print(f"email: {new_user_email}")
    print(f"password: {new_user_pass}\n")

    while True:
        inp = input("manually open *guest chrome browser*, ensure it is *last selected chrome browser* before continuining. May copy playlists to incorrect account if not done. \n(type 'next' to continue)\n> ")
        if inp.lower() == "next":
            break


    print("awaiting manual oAuth authentication")
    OAUTH = SpotifyOAuth(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
        open_browser=True,
        scope="playlist-modify-private,playlist-read-private,playlist-modify-public,user-library-modify,user-library-read",
        username=new_user_username,
    )

    spotipy_client = Spotify(
        client_credentials_manager=OAUTH
    )

    rip_playlist_count = rip_all_playlists(target_user_id=rip_playlists_from_user_target_id,spotipy_client=spotipy_client)

    print(f"successfully ripped {rip_playlist_count} playlist(s) from user '{rip_playlists_from_user_target_id}' to {new_user_email}")

    print(f"\nlogin at:")
    print(f"email: {new_user_email}")
    print(f"password: {new_user_pass}\n")

    return True


if __name__ == "__main__":
    main()
    input("press enter to blow up")







