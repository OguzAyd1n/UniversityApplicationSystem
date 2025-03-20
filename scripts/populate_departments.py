import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app, db
from models import University, Department

def populate_departments():
    with app.app_context():
        # Örnek bölüm verileri
        departments_data = [
            # Bilgisayar Mühendisliği
            {
                'university_name': 'Boğaziçi Üniversitesi',
                'name': 'Bilgisayar Mühendisliği',
                'quota': 100,
                'type': 'Örgün',
                'language': 'İngilizce',
                'duration': 4,
                'base_score': 520.45,
                'ceiling_score': 550.32,
                'base_rank': 1500,
                'ceiling_rank': 500,
                'score_type': 'SAY'
            },
            {
                'university_name': 'Orta Doğu Teknik Üniversitesi',
                'name': 'Bilgisayar Mühendisliği',
                'quota': 120,
                'type': 'Örgün',
                'language': 'İngilizce',
                'duration': 4,
                'base_score': 515.67,
                'ceiling_score': 545.89,
                'base_rank': 2000,
                'ceiling_rank': 600,
                'score_type': 'SAY'
            },
            # Tıp Fakültesi
            {
                'university_name': 'Hacettepe Üniversitesi',
                'name': 'Tıp',
                'quota': 250,
                'type': 'Örgün',
                'language': 'Türkçe',
                'duration': 6,
                'base_score': 530.12,
                'ceiling_score': 560.45,
                'base_rank': 500,
                'ceiling_rank': 100,
                'score_type': 'SAY'
            },
            # İşletme
            {
                'university_name': 'Marmara Üniversitesi',
                'name': 'İşletme',
                'quota': 150,
                'type': 'Örgün',
                'language': 'Türkçe',
                'duration': 4,
                'base_score': 420.34,
                'ceiling_score': 450.67,
                'base_rank': 15000,
                'ceiling_rank': 5000,
                'score_type': 'EA'
            },
            # Hukuk
            {
                'university_name': 'Ankara Üniversitesi',
                'name': 'Hukuk',
                'quota': 200,
                'type': 'Örgün',
                'language': 'Türkçe',
                'duration': 4,
                'base_score': 440.23,
                'ceiling_score': 470.56,
                'base_rank': 10000,
                'ceiling_rank': 3000,
                'score_type': 'EA'
            },
            # İngiliz Dili ve Edebiyatı
            {
                'university_name': 'İstanbul Teknik Üniversitesi',
                'name': 'İngiliz Dili ve Edebiyatı',
                'quota': 80,
                'type': 'Örgün',
                'language': 'İngilizce',
                'duration': 4,
                'base_score': 410.78,
                'ceiling_score': 440.12,
                'base_rank': 20000,
                'ceiling_rank': 8000,
                'score_type': 'DİL'
            }
        ]

        # Bölümleri ekle
        for dept_data in departments_data:
            university = University.query.filter_by(name=dept_data['university_name']).first()
            if university:
                department = Department(
                    university_id=university.id,
                    name=dept_data['name'],
                    quota=dept_data['quota'],
                    type=dept_data['type'],
                    language=dept_data['language'],
                    duration=dept_data['duration'],
                    base_score=dept_data['base_score'],
                    ceiling_score=dept_data['ceiling_score'],
                    base_rank=dept_data['base_rank'],
                    ceiling_rank=dept_data['ceiling_rank'],
                    score_type=dept_data['score_type']
                )
                db.session.add(department)

        # Değişiklikleri kaydet
        db.session.commit()
        print(f"{len(departments_data)} bölüm başarıyla eklendi.")

if __name__ == '__main__':
    populate_departments() 