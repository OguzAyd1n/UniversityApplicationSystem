from your_project.models import db, University
import csv
import logging

def add_universities_from_csv(file_path):
    """
    CSV dosyasından üniversite verilerini yükler ve veritabanına ekler.
    CSV dosyası şu formatta olmalıdır:
    name,location,description
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                university = University(
                    name=row['name'],
                    location=row['location'],
                    description=row.get('description', '')
                )
                db.session.add(university)
        db.session.commit()
        print("Üniversite verileri başarıyla yüklendi.")
    except Exception as e:
        print(f"Hata oluştu: {str(e)}")
        db.session.rollback()

def load_sample_data():
    """
    Örnek verileri yükler (test için)
    """
    sample_universities = [
        {
            'name': 'İstanbul Üniversitesi',
            'location': 'İstanbul',
            'description': 'Türkiye\'nin en eski üniversitesi'
        },
        {
            'name': 'Ankara Üniversitesi',
            'location': 'Ankara',
            'description': 'Türkiye\'nin başkentindeki en eski üniversite'
        },
        {
            'name': 'Ege Üniversitesi',
            'location': 'İzmir',
            'description': 'Ege Bölgesi\'nin en köklü üniversitesi'
        }
    ]

    for uni_data in sample_universities:
        university = University(**uni_data)
        db.session.add(university)
    
    try:
        db.session.commit()
        print("Örnek veriler başarıyla yüklendi.")
    except Exception as e:
        print(f"Hata oluştu: {str(e)}")
        db.session.rollback()

    #Diğer importlar ve fonkaiyon tanımları
def add_universities_from_csv(csv_path):
    try:
        with open(csv_path, 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                university = University(name=row['name'], location=row['location'],
                                        established_year=row['established_year'])
                db.session.add(university)
        db.session.commit()
        logging.info('Veri yükleme işlemi başarıyla tamamlandı.')
    except Exception as e:
        db.session.rollback()
        logging.error(f'Veri yükleme işleminde bir hata oluştu: {str(e)}')

        # data_loader.py
        def add_universities_from_csv(csv_path):
            try:
                with open(csv_path, 'r') as csv_file:
                    csv_reader = csv.DictReader(csv_file)
                    for row in csv_reader:
                        try:
                            university = University(name=row['name'], location=row['location'],
                                                    established_year=row['established_year'])
                            db.session.add(university)
                        except Exception as e:
                            logging.warning(f'Bir üniversite eklenirken hata oluştu: {str(e)}')
                    db.session.commit()
                logging.info('Veri yükleme işlemi başarıyla tamamlandı.')
            except Exception as e:
                db.session.rollback()
                logging.error(f'Veri yükleme işleminde bir hata oluştu: {str(e)}')

