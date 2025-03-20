import requests
import json
from datetime import datetime
import os
from typing import Dict, List, Optional
import logging
from bs4 import BeautifulSoup
import re
import time
import random
from fake_useragent import UserAgent
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Loglama ayarları
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class YOKAtlasFetcher:
    def __init__(self):
        self.base_url = "https://yokatlas.yok.gov.tr"
        self.cache_dir = "cache"
        self.cache_duration = 24 * 60 * 60  # 24 saat (saniye cinsinden)
        
        # User-Agent oluşturucu
        self.ua = UserAgent()
        
        # İstekler arası bekleme süresi (saniye)
        self.min_delay = 2
        self.max_delay = 5
        
        # Son istek zamanı
        self.last_request_time = 0
        
        # Cache dizinini oluştur
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            
        # Selenium WebDriver'ı başlat
        self.driver = None
        self._initialize_driver()

    def _initialize_driver(self):
        """Selenium WebDriver'ı başlatır"""
        try:
            chrome_options = Options()
            chrome_options.add_argument('--headless')  # Görünmez mod
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument(f'user-agent={self.ua.random}')
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.info("Chrome WebDriver başlatıldı")
            
        except Exception as e:
            logger.error(f"WebDriver başlatılırken hata: {str(e)}")
            raise

    def _quit_driver(self):
        """Selenium WebDriver'ı kapatır"""
        if self.driver:
            self.driver.quit()
            logger.info("Chrome WebDriver kapatıldı")

    def _get_cache_path(self, cache_type: str) -> str:
        """Cache dosya yolunu döndürür"""
        return os.path.join(self.cache_dir, f"{cache_type}.json")

    def _is_cache_valid(self, cache_path: str) -> bool:
        """Cache'in geçerli olup olmadığını kontrol eder"""
        if not os.path.exists(cache_path):
            return False
        
        cache_time = os.path.getmtime(cache_path)
        current_time = datetime.now().timestamp()
        
        return (current_time - cache_time) < self.cache_duration

    def _save_to_cache(self, data: dict, cache_type: str):
        """Veriyi cache'e kaydeder"""
        cache_path = self._get_cache_path(cache_type)
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _load_from_cache(self, cache_type: str) -> Optional[dict]:
        """Cache'den veri yükler"""
        cache_path = self._get_cache_path(cache_type)
        if self._is_cache_valid(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def fetch_universities(self) -> List[Dict]:
        """YÖK Atlas'tan üniversite listesini çeker"""
        # Önce cache'i kontrol et
        cached_data = self._load_from_cache('universities')
        if cached_data:
            return cached_data

        try:
            # Ana sayfaya git
            self.driver.get(f"{self.base_url}/lisans-anasayfa.php")
            logger.debug("Ana sayfa yüklendi")
            
            # Üniversite formunu bul
            university_form = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "universityForm"))
            )
            
            if not university_form:
                logger.warning("Üniversite formu bulunamadı")
                return []
            
            # Üniversite linklerini bul
            university_links = self.driver.find_elements(By.CSS_SELECTOR, "a[href*='univ.php?u=']")
            
            if not university_links:
                logger.warning("Üniversite listesi boş veya bulunamadı")
                return []
            
            universities = []
            for link in university_links:
                try:
                    href = link.get_attribute('href')
                    university_id = re.search(r'univ\.php\?u=(\d+)', href).group(1)
                    university_name = link.text.strip()
                    
                    if university_id and university_name:
                        uni_type = self._determine_university_type(university_name)
                        uni_location = self._extract_location(university_name)
                        
                        universities.append({
                            'yok_id': university_id,
                            'name': university_name,
                            'location': uni_location,
                            'type': uni_type,
                            'website': f"https://www.{university_name.lower().replace(' ', '')}.edu.tr"
                        })
                except Exception as e:
                    logger.error(f"Üniversite bilgisi çıkarılırken hata: {str(e)}")
                    continue
            
            if universities:
                # Cache'e kaydet
                self._save_to_cache(universities, 'universities')
                logger.info(f"{len(universities)} üniversite başarıyla çekildi")
            else:
                logger.warning("Üniversite listesi boş")
            
            return universities
            
        except Exception as e:
            logger.error(f"Üniversite verileri çekilirken hata oluştu: {str(e)}")
            return []

    def fetch_departments(self, university_id: str) -> List[Dict]:
        """Belirli bir üniversitenin bölümlerini çeker"""
        cache_key = f'departments_{university_id}'
        
        # Önce cache'i kontrol et
        cached_data = self._load_from_cache(cache_key)
        if cached_data:
            return cached_data

        try:
            # Üniversite sayfasına git
            self.driver.get(f"{self.base_url}/lisans-univ.php?u={university_id}")
            logger.debug(f"Üniversite sayfası yüklendi: {university_id}")
            
            # Bölüm listesini bul
            department_list = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "program-list"))
            )
            
            if not department_list:
                logger.warning(f"Üniversite {university_id} için bölüm listesi bulunamadı")
                return []
            
            # Bölüm linklerini bul
            department_links = department_list.find_elements(By.CSS_SELECTOR, "a[href*='content/lisans-dynamic/']")
            
            departments = []
            for link in department_links:
                try:
                    href = link.get_attribute('href')
                    department_id = re.search(r'lisans-dynamic/(\d+)\.php', href).group(1)
                    department_name = link.text.strip()
                    
                    if department_id and department_name:
                        # Bölüm detaylarını çek
                        dept_details = self.fetch_department_scores(department_id)
                        if dept_details:
                            departments.append({
                                'yok_id': department_id,
                                'name': department_name,
                                'faculty': dept_details.get('faculty', ''),
                                'score_type': dept_details.get('score_type', ''),
                                'quota': dept_details.get('quota', 0),
                                'base_score': dept_details.get('base_score', 0),
                                'ceiling_score': dept_details.get('ceiling_score', 0)
                            })
                except Exception as e:
                    logger.error(f"Bölüm bilgisi çıkarılırken hata: {str(e)}")
                    continue
            
            if departments:
                # Cache'e kaydet
                self._save_to_cache(departments, cache_key)
                logger.info(f"{len(departments)} bölüm başarıyla çekildi")
            else:
                logger.warning(f"Üniversite {university_id} için bölüm listesi boş")
            
            return departments
            
        except Exception as e:
            logger.error(f"Bölüm verileri çekilirken hata oluştu: {str(e)}")
            return []

    def fetch_department_scores(self, department_id: str) -> Optional[Dict]:
        """Bölüm puan bilgilerini çeker"""
        cache_key = f'scores_{department_id}'
        
        # Önce cache'i kontrol et
        cached_data = self._load_from_cache(cache_key)
        if cached_data:
            return cached_data

        try:
            # Bölüm sayfasına git
            self.driver.get(f"{self.base_url}/content/lisans-dynamic/{department_id}.php")
            logger.debug(f"Bölüm sayfası yüklendi: {department_id}")
            
            # Puan bilgilerini bul
            score_table = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "score-table"))
            )
            
            if not score_table:
                logger.warning(f"Bölüm {department_id} için puan bilgileri bulunamadı")
                return None
            
            # Puan bilgilerini çıkar
            scores = {
                'quota': int(score_table.find_element(By.CSS_SELECTOR, "td[data-label='Kontenjan']").text),
                'base_score': float(score_table.find_element(By.CSS_SELECTOR, "td[data-label='Taban Puan']").text),
                'ceiling_score': float(score_table.find_element(By.CSS_SELECTOR, "td[data-label='Tavan Puan']").text),
                'faculty': score_table.find_element(By.CSS_SELECTOR, "td[data-label='Fakülte']").text,
                'score_type': score_table.find_element(By.CSS_SELECTOR, "td[data-label='Puan Türü']").text
            }
            
            # Cache'e kaydet
            self._save_to_cache(scores, cache_key)
            logger.info("Puan bilgileri başarıyla çekildi")
            
            return scores
            
        except Exception as e:
            logger.error(f"Puan bilgileri çekilirken hata oluştu: {str(e)}")
            return None

    def _determine_university_type(self, name: str) -> str:
        """Üniversite türünü belirler"""
        name = name.lower()
        if 'vakıf' in name:
            return 'Vakıf'
        elif 'özel' in name:
            return 'Özel'
        elif 'kktc' in name:
            return 'KKTC'
        elif any(x in name for x in ['yabancı', 'international']):
            return 'Yabancı'
        else:
            return 'Devlet'

    def _extract_location(self, name: str) -> str:
        """Üniversite konumunu çıkarır"""
        # Basit bir konum çıkarma mantığı
        locations = ['istanbul', 'ankara', 'izmir', 'bursa', 'antalya', 'adana', 'konya', 'kayseri', 'samsun', 'trabzon']
        name_lower = name.lower()
        for loc in locations:
            if loc in name_lower:
                return loc.capitalize()
        return 'Diğer'

    def fetch_all_data(self) -> Dict:
        """Tüm verileri çeker ve birleştirir."""
        try:
            universities = self.fetch_universities()
            all_data = {
                'universities': universities,
                'departments': {},
                'scores': {}
            }
            
            for university in universities:
                university_id = university.get('yok_id')
                if university_id:
                    departments = self.fetch_departments(university_id)
                    all_data['departments'][university_id] = departments
                    
                    for department in departments:
                        department_id = department.get('yok_id')
                        if department_id:
                            scores = self.fetch_department_scores(department_id)
                            all_data['scores'][department_id] = scores
            
            return all_data
            
        finally:
            # WebDriver'ı kapat
            self._quit_driver()

class OSYMFetcher:
    """ÖSYM Tercih Kılavuzu'ndan veri çekme sınıfı"""
    
    def __init__(self):
        """Veri çekici sınıfını başlatır"""
        self.base_url = "https://dokuman.osym.gov.tr"
        self.cache_dir = "cache"
        self.cache_duration = 24 * 60 * 60  # 24 saat
        
        # Cache dizinini oluştur
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            
        self.ua = UserAgent()
    
    def _get_cache_path(self, cache_type: str) -> str:
        """Cache dosya yolunu döndürür"""
        return os.path.join(self.cache_dir, f"{cache_type}.json")
    
    def _is_cache_valid(self, cache_path: str) -> bool:
        """Cache'in geçerli olup olmadığını kontrol eder"""
        if not os.path.exists(cache_path):
            return False
            
        # Cache dosyasının yaşını kontrol et
        cache_time = os.path.getmtime(cache_path)
        current_time = datetime.now().timestamp()
        
        return (current_time - cache_time) < self.cache_duration
    
    def _save_to_cache(self, data: Dict, cache_type: str) -> None:
        """Veriyi cache'e kaydeder"""
        cache_path = self._get_cache_path(cache_type)
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def _load_from_cache(self, cache_type: str) -> Optional[Dict]:
        """Cache'den veri yükler"""
        cache_path = self._get_cache_path(cache_type)
        if self._is_cache_valid(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    def _make_request(self, url: str, headers: Optional[Dict] = None) -> Dict:
        """HTTP isteği yapar"""
        if headers is None:
            headers = {
                'User-Agent': self.ua.random,
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': self.base_url,
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'same-origin'
            }
            
        logger.debug(f"İstek yapılıyor: {url}")
        logger.debug(f"Headers: {headers}")
        
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                response = requests.get(
                    url,
                    headers=headers,
                    timeout=30,
                    verify=False  # SSL doğrulamasını devre dışı bırak
                )
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                retry_count += 1
                logger.error(f"İstek hatası: {str(e)}")
                if retry_count == max_retries:
                    logger.error(f"Maksimum yeniden deneme sayısına ulaşıldı: {max_retries}")
                    raise
                continue
    
    def fetch_universities(self) -> List[Dict]:
        """Üniversite listesini çeker"""
        # Cache'den kontrol et
        cached_data = self._load_from_cache('universities')
        if cached_data:
            return cached_data
            
        # ÖSYM Tercih Kılavuzu'ndan üniversite listesini çek
        url = f"{self.base_url}/tercih/tercih_2024.xlsx"
        
        try:
            # Excel dosyasını indir
            response = requests.get(url, verify=False)
            response.raise_for_status()
            
            # İndirilen dosyanın içeriğini kontrol et
            logger.debug(f"İndirilen dosya boyutu: {len(response.content)} bytes")
            logger.debug(f"İndirilen dosya içeriği: {response.content[:200]}")
            
            # Excel'i DataFrame'e çevir
            df = pd.read_excel(response.content, engine='openpyxl')
            
            # DataFrame'i JSON formatına çevir
            universities = []
            for _, row in df.iterrows():
                university = {
                    'id': str(row['KODU']),
                    'name': row['ÜNİVERSİTE ADI'],
                    'city': row['ŞEHİR'],
                    'type': row['ÜNİVERSİTE TÜRÜ'],
                    'website': row['WEB ADRESİ'] if 'WEB ADRESİ' in row else None
                }
                universities.append(university)
            
            # Cache'e kaydet
            self._save_to_cache(universities, 'universities')
            return universities
            
        except Exception as e:
            logger.error(f"Üniversite listesi çekilirken hata: {str(e)}")
            raise
    
    def fetch_departments(self, university_id: str) -> List[Dict]:
        """Üniversiteye ait bölümleri çeker"""
        # Cache'den kontrol et
        cache_key = f'departments_{university_id}'
        cached_data = self._load_from_cache(cache_key)
        if cached_data:
            return cached_data
            
        # ÖSYM Tercih Kılavuzu'ndan bölüm listesini çek
        url = f"{self.base_url}/tercih/tercih_2024.xlsx"
        
        try:
            # Excel dosyasını indir
            response = requests.get(url, verify=False)
            response.raise_for_status()
            
            # İndirilen dosyanın içeriğini kontrol et
            logger.debug(f"İndirilen dosya boyutu: {len(response.content)} bytes")
            logger.debug(f"İndirilen dosya içeriği: {response.content[:200]}")
            
            # Excel'i DataFrame'e çevir
            df = pd.read_excel(response.content, engine='openpyxl')
            
            # Üniversiteye ait bölümleri filtrele
            df = df[df['KODU'] == university_id]
            
            # DataFrame'i JSON formatına çevir
            departments = []
            for _, row in df.iterrows():
                department = {
                    'id': str(row['PROGRAM KODU']),
                    'name': row['PROGRAM ADI'],
                    'quota': row['KONTENJAN'],
                    'base_score': row['TABAN PUAN'],
                    'base_rank': row['TABAN BAŞARI SIRASI'],
                    'type': row['ÖĞRENİM SÜRESİ'],
                    'language': row['DİL'],
                    'scholarship': row['BURSLU'] if 'BURSLU' in row else None
                }
                departments.append(department)
            
            # Cache'e kaydet
            self._save_to_cache(departments, cache_key)
            return departments
            
        except Exception as e:
            logger.error(f"Bölüm listesi çekilirken hata: {str(e)}")
            raise
    
    def fetch_department_scores(self, department_id: str) -> Dict:
        """Bölümün puan bilgilerini çeker"""
        # Cache'den kontrol et
        cache_key = f'scores_{department_id}'
        cached_data = self._load_from_cache(cache_key)
        if cached_data:
            return cached_data
            
        # ÖSYM Tercih Kılavuzu'ndan puan bilgilerini çek
        url = f"{self.base_url}/tercih/tercih_2024.xlsx"
        
        try:
            # Excel dosyasını indir
            response = requests.get(url, verify=False)
            response.raise_for_status()
            
            # İndirilen dosyanın içeriğini kontrol et
            logger.debug(f"İndirilen dosya boyutu: {len(response.content)} bytes")
            logger.debug(f"İndirilen dosya içeriği: {response.content[:200]}")
            
            # Excel'i DataFrame'e çevir
            df = pd.read_excel(response.content, engine='openpyxl')
            
            # Bölüme ait puan bilgilerini filtrele
            df = df[df['PROGRAM KODU'] == department_id]
            
            if df.empty:
                raise ValueError(f"Bölüm bulunamadı: {department_id}")
            
            row = df.iloc[0]
            scores = {
                'base_score': row['TABAN PUAN'],
                'base_rank': row['TABAN BAŞARI SIRASI'],
                'quota': row['KONTENJAN'],
                'filled_quota': row['YERLEŞEN'],
                'min_score': row['TABAN PUAN'],
                'max_score': row['TAVAN PUAN'],
                'average_score': row['ORTALAMA PUAN'],
                'std_dev': row['STANDART SAPMA']
            }
            
            # Cache'e kaydet
            self._save_to_cache(scores, cache_key)
            return scores
            
        except Exception as e:
            logger.error(f"Puan bilgileri çekilirken hata: {str(e)}")
            raise 