import os
import sys
import logging
from datetime import datetime
from typing import Dict, List

# Ana dizini Python path'ine ekle
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.data_fetcher import YOKAtlasFetcher
from utils.database import Database

# Loglama ayarları
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def update_database():
    """Veritabanını günceller"""
    try:
        # Veri çekiciyi başlat
        fetcher = YOKAtlasFetcher()
        
        # Veritabanı bağlantısını başlat
        db = Database()
        
        # Üniversiteleri çek
        logger.info("Üniversiteler çekiliyor...")
        universities = fetcher.fetch_universities()
        
        # Her üniversite için
        for university in universities:
            # Üniversiteyi veritabanına ekle/güncelle
            db.add_university(university)
            
            # Üniversitenin bölümlerini çek
            logger.info(f"{university['name']} bölümleri çekiliyor...")
            departments = fetcher.fetch_departments(university['yok_id'])
            
            # Her bölüm için
            for department in departments:
                # Bölümün puan bilgilerini çek
                scores = fetcher.fetch_department_scores(department['yok_id'])
                
                # Bölümü veritabanına ekle/güncelle
                db.add_department(department, university['yok_id'], scores)
        
        logger.info("Veritabanı başarıyla güncellendi!")
        
    except Exception as e:
        logger.error(f"Veritabanı güncellenirken hata: {str(e)}")
        raise
    finally:
        # Veritabanı bağlantısını kapat
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    update_database() 