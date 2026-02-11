import sqlite3
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_name="digital_signage.db"):
        self.db_name = db_name
        self.conn = None
        self.cursor = None
        self.connect()
        self.setup_database()

    def connect(self):
        """Estabelece a conexão com o banco de dados."""
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

    def setup_database(self):
        """Cria a tabela de mídias se ela não existir, com a nova coluna de duração."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS medias (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT NOT NULL,
                file_path TEXT NOT NULL,
                duration_seconds INTEGER,
                schedule_start_date TEXT,
                schedule_start_time TEXT,
                schedule_end_date TEXT,
                schedule_end_time TEXT
            )
        ''')
        self.conn.commit()

    def add_media(self, name, media_type, file_path, duration_seconds=None):
        """Adiciona uma nova mídia ao banco de dados."""
        self.cursor.execute('''
            INSERT INTO medias (name, type, file_path, duration_seconds, schedule_start_date, schedule_start_time, schedule_end_date, schedule_end_time)
            VALUES (?, ?, ?, ?, NULL, NULL, NULL, NULL)
        ''', (name, media_type, file_path, duration_seconds))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_all_medias(self):
        """Retorna todos os registros de mídias do banco de dados."""
        self.cursor.execute('SELECT * FROM medias')
        return self.cursor.fetchall()

    def delete_medias(self, media_ids):
        """Deleta mídias do banco de dados com base em seus IDs."""
        if not media_ids:
            return
        placeholders = ','.join('?' * len(media_ids))
        self.cursor.execute(f"DELETE FROM medias WHERE id IN ({placeholders})", media_ids)
        self.conn.commit()

    def update_media_schedule(self, media_id, start_date, start_time, end_date, end_time):
        """Atualiza o agendamento de uma mídia no banco de dados."""
        self.cursor.execute('''
            UPDATE medias
            SET schedule_start_date = ?,
                schedule_start_time = ?,
                schedule_end_date = ?,
                schedule_end_time = ?
            WHERE id = ?
        ''', (start_date, start_time, end_date, end_time, media_id))
        self.conn.commit()

    def update_media_duration(self, media_id, duration_seconds):
        """Atualiza a duração de uma mídia no banco de dados."""
        self.cursor.execute('''
            UPDATE medias
            SET duration_seconds = ?
            WHERE id = ?
        ''', (duration_seconds, media_id))
        self.conn.commit()
    
    def close(self):
        """Fecha a conexão com o banco de dados."""
        self.conn.close()

    def get_active_medias(self):
        """Retorna apenas as mídias que estão dentro do período de validade."""
        self.cursor.execute('SELECT * FROM medias')
        all_medias = self.cursor.fetchall()
        
        active_medias = []
        now = datetime.now()

        for media in all_medias:
            # Índices: 5=start_date, 6=start_time, 7=end_date, 8=end_time
            s_date, s_time = media[5], media[6]
            e_date, e_time = media[7], media[8]

            # Se não tem início definido, consideramos ativa (ou ajuste conforme sua regra)
            if not s_date:
                active_medias.append(media)
                continue

            try:
                # Converte strings para objetos datetime
                start_dt = datetime.strptime(f"{s_date} {s_time}", "%dd/%mm/%YYYY %HH:%MM")
                
                # Verifica se já começou
                if now < start_dt:
                    continue

                # Verifica se tem fim e se já expirou
                if e_date:
                    end_dt = datetime.strptime(f"{e_date} {e_time}", "%dd/%mm/%YYYY %HH:%MM")
                    if now > end_dt:
                        continue
                
                active_medias.append(media)
            except Exception as e:
                print(f"Erro ao processar data da mídia {media[0]}: {e}")
                # Na dúvida, se o formato estiver errado, podemos manter ou pular
                active_medias.append(media) 

        return active_medias