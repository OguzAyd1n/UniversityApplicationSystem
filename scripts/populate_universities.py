import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app, db
from models import University

def populate_universities():
    with app.app_context():
        # Örnek üniversite verileri
        universities = [
            {
                'yok_id': '1001',
                'name': 'Boğaziçi Üniversitesi',
                'location': 'İstanbul',
                'type': 'Devlet',
                'website': 'https://www.boun.edu.tr'
            },
            {
                'yok_id': '1002',
                'name': 'Orta Doğu Teknik Üniversitesi',
                'location': 'Ankara',
                'type': 'Devlet',
                'website': 'https://www.metu.edu.tr'
            },
            {
                'yok_id': '1003',
                'name': 'İstanbul Teknik Üniversitesi',
                'location': 'İstanbul',
                'type': 'Devlet',
                'website': 'https://www.itu.edu.tr'
            },
            {
                'yok_id': '1004',
                'name': 'Ankara Üniversitesi',
                'location': 'Ankara',
                'type': 'Devlet',
                'website': 'https://www.ankara.edu.tr'
            },
            {
                'yok_id': '1005',
                'name': 'Ege Üniversitesi',
                'location': 'İzmir',
                'type': 'Devlet',
                'website': 'https://www.ege.edu.tr'
            },
            {
                'yok_id': '1006',
                'name': 'Hacettepe Üniversitesi',
                'location': 'Ankara',
                'type': 'Devlet',
                'website': 'https://www.hacettepe.edu.tr'
            },
            {
                'yok_id': '1007',
                'name': 'Yıldız Teknik Üniversitesi',
                'location': 'İstanbul',
                'type': 'Devlet',
                'website': 'https://www.yildiz.edu.tr'
            },
            {
                'yok_id': '1008',
                'name': 'Dokuz Eylül Üniversitesi',
                'location': 'İzmir',
                'type': 'Devlet',
                'website': 'https://www.deu.edu.tr'
            },
            {
                'yok_id': '1009',
                'name': 'Marmara Üniversitesi',
                'location': 'İstanbul',
                'type': 'Devlet',
                'website': 'https://www.marmara.edu.tr'
            },
            {
                'yok_id': '1010',
                'name': 'Gazi Üniversitesi',
                'location': 'Ankara',
                'type': 'Devlet',
                'website': 'https://www.gazi.edu.tr'
            }
        ]

        # Veritabanını temizle
        University.query.delete()
        
        # Yeni üniversiteleri ekle
        for uni_data in universities:
            university = University(
                yok_id=uni_data['yok_id'],
                name=uni_data['name'],
                location=uni_data['location'],
                type=uni_data['type'],
                website=uni_data['website']
            )
            db.session.add(university)
        
        # Değişiklikleri kaydet
        db.session.commit()
        print(f"{len(universities)} üniversite başarıyla eklendi.")

if __name__ == '__main__':
    populate_universities() 