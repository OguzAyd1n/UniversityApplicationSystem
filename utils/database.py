import sqlite3
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class Database:
    """SQLite veritabanı işlemleri için sınıf"""
    
    def __init__(self, db_path: str = "universities.db"):
        """Veritabanı bağlantısını başlatır"""
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self._connect()
        self._create_tables()
    
    def _connect(self):
        """Veritabanına bağlanır"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            logger.info("Veritabanına bağlanıldı")
        except sqlite3.Error as e:
            logger.error(f"Veritabanına bağlanırken hata: {str(e)}")
            raise
    
    def _create_tables(self):
        """Gerekli tabloları oluşturur"""
        try:
            # Üniversiteler tablosu
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS universities (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    city TEXT,
                    type TEXT,
                    website TEXT
                )
            """)
            
            # Bölümler tablosu
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS departments (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    university_id TEXT NOT NULL,
                    quota INTEGER,
                    base_score REAL,
                    base_rank INTEGER,
                    type TEXT,
                    language TEXT,
                    scholarship TEXT,
                    FOREIGN KEY (university_id) REFERENCES universities (id)
                )
            """)
            
            # Puan bilgileri tablosu
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS scores (
                    department_id TEXT PRIMARY KEY,
                    base_score REAL,
                    base_rank INTEGER,
                    quota INTEGER,
                    filled_quota INTEGER,
                    min_score REAL,
                    max_score REAL,
                    average_score REAL,
                    std_dev REAL,
                    FOREIGN KEY (department_id) REFERENCES departments (id)
                )
            """)
            
            self.conn.commit()
            logger.info("Tablolar oluşturuldu")
            
        except sqlite3.Error as e:
            logger.error(f"Tablolar oluşturulurken hata: {str(e)}")
            raise
    
    def add_university(self, university: Dict):
        """Üniversite ekler veya günceller"""
        try:
            self.cursor.execute("""
                INSERT OR REPLACE INTO universities (id, name, city, type, website)
                VALUES (?, ?, ?, ?, ?)
            """, (
                university['id'],
                university['name'],
                university['city'],
                university['type'],
                university.get('website')
            ))
            self.conn.commit()
            logger.debug(f"Üniversite eklendi/güncellendi: {university['name']}")
            
        except sqlite3.Error as e:
            logger.error(f"Üniversite eklenirken hata: {str(e)}")
            raise
    
    def add_department(self, department: Dict, university_id: str, scores: Dict):
        """Bölüm ve puan bilgilerini ekler veya günceller"""
        try:
            # Bölümü ekle/güncelle
            self.cursor.execute("""
                INSERT OR REPLACE INTO departments (
                    id, name, university_id, quota, base_score, base_rank,
                    type, language, scholarship
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                department['id'],
                department['name'],
                university_id,
                department['quota'],
                department['base_score'],
                department['base_rank'],
                department['type'],
                department['language'],
                department.get('scholarship')
            ))
            
            # Puan bilgilerini ekle/güncelle
            self.cursor.execute("""
                INSERT OR REPLACE INTO scores (
                    department_id, base_score, base_rank, quota, filled_quota,
                    min_score, max_score, average_score, std_dev
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                department['id'],
                scores['base_score'],
                scores['base_rank'],
                scores['quota'],
                scores['filled_quota'],
                scores['min_score'],
                scores['max_score'],
                scores['average_score'],
                scores['std_dev']
            ))
            
            self.conn.commit()
            logger.debug(f"Bölüm eklendi/güncellendi: {department['name']}")
            
        except sqlite3.Error as e:
            logger.error(f"Bölüm eklenirken hata: {str(e)}")
            raise
    
    def get_universities(self) -> List[Dict]:
        """Tüm üniversiteleri getirir"""
        try:
            self.cursor.execute("SELECT * FROM universities")
            columns = [description[0] for description in self.cursor.description]
            return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Üniversiteler getirilirken hata: {str(e)}")
            raise
    
    def get_departments(self, university_id: str) -> List[Dict]:
        """Üniversiteye ait bölümleri getirir"""
        try:
            self.cursor.execute("""
                SELECT d.*, s.*
                FROM departments d
                LEFT JOIN scores s ON d.id = s.department_id
                WHERE d.university_id = ?
            """, (university_id,))
            
            columns = [description[0] for description in self.cursor.description]
            return [dict(zip(columns, row)) for row in self.cursor.fetchall()]
            
        except sqlite3.Error as e:
            logger.error(f"Bölümler getirilirken hata: {str(e)}")
            raise
    
    def close(self):
        """Veritabanı bağlantısını kapatır"""
        if self.conn:
            self.conn.close()
            logger.info("Veritabanı bağlantısı kapatıldı") 