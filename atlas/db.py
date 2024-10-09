import psycopg2
from psycopg2 import Error

from atlas.settings import Settings

class AtlasDBFacade:

    def connect(self):
        # Connect to an existing database
        self.connection = self._get_connection()
        try:
            

            # Create a cursor to perform database operations
            cursor = self.connection.cursor()
            # Print PostgreSQL details
            print("PostgreSQL server information")
            print(self.connection.get_dsn_parameters(), "\n")
            # Executing a SQL query
            cursor.execute("SELECT version();")
            # Fetch result
            record = cursor.fetchone()
            print("Connected to - ", record, "\n")

            self._create_tables()

        except (Exception, Error) as error:
            print("Error while connecting to PostgreSQL", error)
        finally:
            if (self.connection):
                cursor.close()
                self.connection.close()
                print("PostgreSQL connection is closed")

    def _get_connection(self):
        settings = Settings()
        return psycopg2.connect(user=settings.postgres_user,
                                        password=settings.postgres_password,
                                        host=settings.postgres_server,
                                        port=settings.postgres_port,
                                        database=settings.postgres_db)

    def _create_tables(self):
        try:
            # Connect to an existing database
            conn = self._get_connection()
            
            # Open a cursor to perform database operations
            cur = conn.cursor()
            
            # Execute a command: this creates a new table
            cur.execute("CREATE TABLE IF NOT EXISTS sources(id SERIAL PRIMARY KEY, source VARCHAR(256), baseimageurl VARCHAR(1024), time TIMESTAMP);")
            cur.execute("CREATE TABLE IF NOT EXISTS tiles(id SERIAL PRIMARY KEY, sourceid SERIAL, tilex INT, tiley INT, tilez INT, time TIMESTAMP, CONSTRAINT fk_source FOREIGN KEY(sourceid) REFERENCES sources(id));")
            cur.execute("CREATE TABLE IF NOT EXISTS metrics(id SERIAL PRIMARY KEY, tileid SERIAL, tilex INT, tiley INT, tilez INT, time TIMESTAMP, metric VARCHAR(64), value FLOAT, CONSTRAINT fk_tile FOREIGN KEY(tileid) REFERENCES tiles(id));")
            #cur.execute("CREATE TABLE IF NOT EXISTS detections(id SERIAL PRIMARY KEY, tilex INT, tiley INT, tilez INT, time TIMESTAMP, name VARCHAR(64), location geography(POINT,4326));")
            cur.close()
            conn.commit()
        except (Exception, Error) as error:
            print("Error while connecting to PostgreSQL", error)

    def detction_insert(self):
        try:
            # Connect to an existing database
            conn = self._get_connection()
            cur = conn.cursor()
            cur.execute("INSERT INTO detections (tilex, tiley, tilez, time, name, location) VALUES (1,1,1,NOW(),'boat','POINT(-22.6056 63.9850)');")            
            cur.close()
            conn.commit()
        except (Exception, Error) as error:
            print("Error while connecting to PostgreSQL", error)

    def metric_insert(self,tileid,x,y,z,time,metric,value):
        try:
            # Connect to an existing database
            conn = self._get_connection()
            cur = conn.cursor()
            cur.execute(f"INSERT INTO metrics (tileid, tilex, tiley, tilez, time, metric, value) VALUES (%s,%s,%s,%s,%s,%s,%s);",(tileid,x,y,z,time,metric,value))
            cur.close()
            conn.commit()
        except (Exception, Error) as error:
            print("Error while connecting to PostgreSQL", error)

    def get_tile_id(self,x,y,z,sourceid):
        try:
            # Connect to an existing database
            conn = self._get_connection()
            cur = conn.cursor()
            cur.execute(f"SELECT id FROM tiles WHERE tilex=%s AND tiley=%s AND tilez=%s AND sourceid=%s;",(str(x),str(y),str(z),sourceid))
            id_of_row = cur.fetchone()[0]
            cur.close()
            conn.commit()
            return id_of_row
        except (Exception, Error) as error:
            print("Error while connecting to PostgreSQL", error)

    def get_tile_time(self,id):
        try:
            # Connect to an existing database
            conn = self._get_connection()
            cur = conn.cursor()
            cur.execute(f"SELECT time FROM tiles WHERE id={id}")
            time = cur.fetchone()[0]
            cur.close()
            conn.commit()
            return time
        except (Exception, Error) as error:
            print("Error while connecting to PostgreSQL", error)
        
    def tile_insert(self,x,y,z,time,sourceid):
        try:
            # Connect to an existing database
            conn = self._get_connection()
            cur = conn.cursor()
            cur.execute(f"INSERT INTO tiles (tilex, tiley, tilez, time, sourceid) VALUES (%s,%s,%s,%s,%s) RETURNING id;",(str(x),str(y),str(z),time,sourceid))
            id_of_new_row = cur.fetchone()[0]
            cur.close()
            conn.commit()
            return id_of_new_row
        except (Exception, Error) as error:
            print("Error while connecting to PostgreSQL", error)

    def source_insert(self,time,source,url):
        try:
            # Connect to an existing database
            conn = self._get_connection()
            cur = conn.cursor()
            cur.execute(f"INSERT INTO sources (source, baseimageurl, time) VALUES (%s,%s,%s) RETURNING id;",(source,url,time))
            id_of_new_row = cur.fetchone()[0]
            cur.close()
            conn.commit()
            return id_of_new_row
        except (Exception, Error) as error:
            print("Error while connecting to PostgreSQL", error)
