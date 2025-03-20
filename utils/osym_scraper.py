import requests
from bs4 import BeautifulSoup
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

def fetch_osym_data(tc_no, osym_no):
    """
    ÖSYM'nin sonuç sayfasından kullanıcının sınav bilgilerini çeker.
    
    Args:
        tc_no (str): TC Kimlik numarası
        osym_no (str): ÖSYM aday numarası
        
    Returns:
        dict: Kullanıcının sınav bilgileri
    """
    try:
        # Selenium WebDriver'ı başlat (Chrome)
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Tarayıcıyı görünmez modda çalıştır
        driver = webdriver.Chrome(options=options)
        
        # ÖSYM sonuç sayfasına git
        driver.get("https://sonuc.osym.gov.tr/")
        
        # TC ve ÖSYM numaralarını gir
        tc_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "tc"))
        )
        tc_input.send_keys(tc_no)
        
        osym_input = driver.find_element(By.ID, "sifre")
        osym_input.send_keys(osym_no)
        
        # Giriş yap butonuna tıkla
        submit_button = driver.find_element(By.ID, "giris")
        submit_button.click()
        
        # Sonuçların yüklenmesini bekle
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "sonuc-tablosu"))
        )
        
        # Sonuçları çek
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        results_table = soup.find('table', class_='sonuc-tablosu')
        
        # Sonuçları işle
        results = {
            'year': None,
            'score_say': None,
            'score_ea': None,
            'score_soz': None,
            'score_dil': None,
            'rank_say': None,
            'rank_ea': None,
            'rank_soz': None,
            'rank_dil': None
        }
        
        if results_table:
            rows = results_table.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 2:
                    label = cols[0].text.strip().lower()
                    value = cols[1].text.strip()
                    
                    if 'sayısal' in label:
                        results['score_say'] = float(value.split()[0])
                        results['rank_say'] = int(value.split()[-1].replace(',', ''))
                    elif 'eşit ağırlık' in label:
                        results['score_ea'] = float(value.split()[0])
                        results['rank_ea'] = int(value.split()[-1].replace(',', ''))
                    elif 'sözel' in label:
                        results['score_soz'] = float(value.split()[0])
                        results['rank_soz'] = int(value.split()[-1].replace(',', ''))
                    elif 'dil' in label:
                        results['score_dil'] = float(value.split()[0])
                        results['rank_dil'] = int(value.split()[-1].replace(',', ''))
                    elif 'sınav yılı' in label:
                        results['year'] = int(value)
        
        driver.quit()
        return results
        
    except Exception as e:
        if 'driver' in locals():
            driver.quit()
        raise Exception(f"ÖSYM verisi çekilirken bir hata oluştu: {str(e)}")

def validate_osym_credentials(tc_no, osym_no):
    """
    TC ve ÖSYM numaralarının geçerliliğini kontrol eder.
    
    Args:
        tc_no (str): TC Kimlik numarası
        osym_no (str): ÖSYM aday numarası
        
    Returns:
        bool: Bilgiler geçerli ise True, değilse False
    """
    if not tc_no.isdigit() or len(tc_no) != 11:
        return False
        
    if not osym_no.isdigit() or len(osym_no) < 8:
        return False
        
    return True 