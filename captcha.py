from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import ffmpeg
import speech_recognition as sr
import os
import tempfile
import time

chrome_options = webdriver.ChromeOptions()
#chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.page_load_strategy = 'eager'

driver = webdriver.Chrome(options=chrome_options)

try:
    driver.get("https://www.google.com/recaptcha/api2/demo")
    
    WebDriverWait(driver, 5).until(
        EC.frame_to_be_available_and_switch_to_it(
            (By.CSS_SELECTOR, "iframe[src*='recaptcha/api2/anchor']")
        )
    )
    
    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.ID, "recaptcha-anchor"))
    ).click()
    
    driver.switch_to.default_content()
    
    WebDriverWait(driver, 5).until(
        EC.frame_to_be_available_and_switch_to_it(
            (By.CSS_SELECTOR, "iframe[src*='recaptcha/api2/bframe']")
        )
    )
    
    WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.ID, "recaptcha-audio-button"))
    ).click()
    
    audio_src = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.ID, "audio-source"))
    ).get_attribute("src")

    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_mp3:
        tmp_mp3.write(requests.get(audio_src, timeout=10).content)
        tmp_mp3_path = tmp_mp3.name
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_wav:
        (
            ffmpeg
            .input(tmp_mp3_path)
            .output(tmp_wav.name, format='wav', ar=16000)
            .run(quiet=True, overwrite_output=True)
        )
        wav_path = tmp_wav.name
    
    r = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio = r.record(source)

    os.unlink(tmp_mp3_path)
    os.unlink(wav_path)
    
    text = r.recognize_google(audio, language='en-US')
    
    driver.find_element(By.ID, "audio-response").send_keys(text)
    driver.find_element(By.ID, "recaptcha-verify-button").click()
    time.sleep(3)
except Exception as e:
    print(f"Error: {str(e)}")
finally:
    driver.quit()