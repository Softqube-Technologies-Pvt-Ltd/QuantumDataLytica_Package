# MyConfig.py
import base64

from cryptography.fernet import Fernet


def get_bucket_name():
    param = b'gAAAAABnAY5pVC3iqMsOATBzPGGnczUGH7jxWFD0dqcmFg551TgwY2_T2inCdBz2DExQvbfDHoJ5qfpi7VE3GCGv-83S5wGNDA4hJv22xOwZEo2aBJYNY0U='
    my_value = b'OG12aXpEQ2ZsNm1QT3Q0WVpJa3U5c1hnVjA1T2p3dy1OYzhZOEtaaTlEUT0='
    key = base64.urlsafe_b64decode(my_value)

    """Decrypts a message with a given key."""
    f = Fernet(key)
    decrypted_message = f.decrypt(param).decode()
    tag, value = decrypted_message.split(":", 1)
    return value

def get_access_key_id():
    param = b'gAAAAABnAY5pyNW-Vn9fdXF_EHUquAk05VKnWBRwjYmjZg4_WEXLjjQGgsdibxwWLA-dHJRRKX8Ta37BaszJmrQ280_3JKCe8amjnAu0kVfPLuSAIzRx_YM='
    my_value = b'OG12aXpEQ2ZsNm1QT3Q0WVpJa3U5c1hnVjA1T2p3dy1OYzhZOEtaaTlEUT0='
    key = base64.urlsafe_b64decode(my_value)

    """Decrypts a message with a given key."""
    f = Fernet(key)
    decrypted_message = f.decrypt(param).decode()
    tag, value = decrypted_message.split(":", 1)
    return value

def get_secret_access_key():
    param = b'gAAAAABnAY5pIPJwVKnRSLxbddYpgKRSq4t0ystWA656KP5QbdQieqXJoPSdHILm-_3MJPIJjXn2-iht_7k1DvLfWshaSyaF1qDUFvIl3Kmw5rqX-z6_YNMHgEgUcfBqkABdgM_z8YyT'
    my_value = b'OG12aXpEQ2ZsNm1QT3Q0WVpJa3U5c1hnVjA1T2p3dy1OYzhZOEtaaTlEUT0='
    key = base64.urlsafe_b64decode(my_value)

    """Decrypts a message with a given key."""
    f = Fernet(key)
    decrypted_message = f.decrypt(param).decode()
    tag, value = decrypted_message.split(":", 1)
    return value

def get_log_api_host():
    param = b'gAAAAABnAY5phkZgN2_etuycO8nACD4lXpWDdn1QGj9Y804d9BIiUKtYheJceZkDrYYJAB9v5E5kkp8HjA3_C_0cuzMkgHpnmgB_mnA0LzQQ4ftYYqf_KNKPNpDEZzY92bB8utIXliPE_fzup3ysaN6c87VKEIOpyA=='
    my_value = b'OG12aXpEQ2ZsNm1QT3Q0WVpJa3U5c1hnVjA1T2p3dy1OYzhZOEtaaTlEUT0='
    key = base64.urlsafe_b64decode(my_value)

    """Decrypts a message with a given key."""
    f = Fernet(key)
    decrypted_message = f.decrypt(param).decode()
    tag, value = decrypted_message.split(":", 1)
    return value