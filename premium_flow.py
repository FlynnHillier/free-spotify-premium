from SpotifySession import SpotifySession
from typing import Tuple
from time import sleep



premium_promotion_url = "https://www.spotify.com/purchase/offer/2023-midyear-v2-trial-3m"


def premium_account_gen_flow(
    card_number:str, #xxxxxxxxxxxxxxxx (16)
    card_exp_month:str, #xx
    card_exp_year:str, #xx
    card_cvv:str, #xxx
    email:str | None = None,
    password:str | None = None,
) -> Tuple[str,str,bool,bool]:
    session = SpotifySession(cookies_fp=None)

    signup_success,email,password = session.spotify_signup(
        email=email,
        password=password,
    )

    if not signup_success:
        print("failed signing up.")
        return ("","",False,False)
    else:
        print("successfully signed up.")
        print(f"email: {email}")
        print(f"password: {password}")
    
    premium_activation_success = session.spotify_premium_plan_signup(
        plan_url=premium_promotion_url,
        cardnumber=card_number,
        exp_month=card_exp_month,
        exp_year=card_exp_year,
        cvv=card_cvv,
    )

    if not premium_activation_success:
        print("failed activating premium.")
        return (email,password,False,False)
    else:
        print("activated premium.")

    
    premium_deactivation_success = session.spotify_cancel_premium_plan()

    if not premium_deactivation_success:
        print("failed to deactivate premium.")
        return (email,password,True,False)
    else:
        print("deactivated premium.")

    
    sleep(5)

    session.driver.quit()

    return (email,password,True,True)