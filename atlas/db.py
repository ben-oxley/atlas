import json
import psycopg2
from psycopg2 import Error

from atlas.jobs import JobStatus
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
            cur.execute("CREATE TABLE IF NOT EXISTS jobs(id SERIAL PRIMARY KEY, jobtype VARCHAR(64), jobparams JSON, status VARCHAR(64));")
            #cur.execute("CREATE TABLE IF NOT EXISTS detections(id SERIAL PRIMARY KEY, tilex INT, tiley INT, tilez INT, time TIMESTAMP, name VARCHAR(64), location geography(POINT,4326));")
            cur.close()
            conn.commit()
        except (Exception, Error) as error:
            print("Error while connecting to PostgreSQL", error)

    def detection_insert(self):
        return self._db_execute("INSERT INTO detections (tilex, tiley, tilez, time, name, location) VALUES (1,1,1,NOW(),'boat','POINT(-22.6056 63.9850)');",())            

    def metric_insert(self,tileid,x,y,z,time,metric,value):
        return self._db_execute(f"INSERT INTO metrics (tileid, tilex, tiley, tilez, time, metric, value) VALUES (%s,%s,%s,%s,%s,%s,%s);",(tileid,x,y,z,time,metric,value))

    def get_metric(self,tile_x:int,tile_y:int,tile_z:int,metric:str):
        return self._db_fetchall(f"SELECT time,value FROM metrics WHERE tilex=%s AND tiley=%s AND tilez=%s AND metric=%s;",(str(tile_x),str(tile_y),str(tile_z),metric))

    def get_tile_id(self,x,y,z,sourceid):
        return self._db_fetchone(f"SELECT id FROM tiles WHERE tilex=%s AND tiley=%s AND tilez=%s AND sourceid=%s;",(str(x),str(y),str(z),sourceid))

    def get_tile_time(self,id):
        return self._db_fetchone(f"SELECT time FROM tiles WHERE id={id}")
        
    def tile_insert(self,x,y,z,time,sourceid):
        return self._db_fetchone(f"INSERT INTO tiles (tilex, tiley, tilez, time, sourceid) VALUES (%s,%s,%s,%s,%s) RETURNING id;",(str(x),str(y),str(z),time,sourceid))

    def source_insert(self,time,source,url):
        return self._db_fetchone(f"INSERT INTO sources (source, baseimageurl, time) VALUES (%s,%s,%s) RETURNING id;",(source,url,time))

    def add_job(self,job_type,job_params):
        params_str = json.dumps(job_params)
        return self._db_fetchone(f"INSERT INTO jobs (jobtype, jobparams, status) VALUES (%s,%s,%s) RETURNING id;",(str(job_type),params_str,str(JobStatus.NOT_STARTED)))
    
    def peek_job(self,job_type):
        return self._db_fetchone(f"SELECT * FROM jobs WHERE jobtype=%s AND status=%s",(str(job_type),str(JobStatus.NOT_STARTED)))
    
    def get_job(self,job_id):
        return self._db_fetchone(f"SELECT * FROM jobs WHERE id=%s",(str(job_id)))

    def update_job(self,job_id,job_type,job_status,previous_job_status):
        return self._db_fetchone(f"UPDATE jobs SET status=%s WHERE id=%s AND jobtype=%s AND status=%s",(str(job_status),str(job_id),str(job_type),str(previous_job_status)))

    def pop_job(self,job_id):
        return self._db_execute(f"DELETE FROM jobs WHERE id=%s",(str(job_id)))

    



    def _db_execute(self,query,params):
        try:
            # Connect to an existing database
            conn = self._get_connection()
            cur = conn.cursor()
            cur.execute(query,params)
            cur.close()
            conn.commit()
        except (Exception, Error) as error:
            print("Error while connecting to PostgreSQL", error)

    def _db_fetchone(self,query,params):
        try:
            # Connect to an existing database
            conn = self._get_connection()
            cur = conn.cursor()
            cur.execute(query,params)
            result = cur.fetchone()[0]
            cur.close()
            conn.commit()
            return result
        except (Exception, Error) as error:
            print("Error while connecting to PostgreSQL", error)
            return None
    
    def _db_fetchall(self,query,params):
        try:
            # Connect to an existing database
            conn = self._get_connection()
            cur = conn.cursor()
            cur.execute(query,params)
            result = cur.fetchall()
            cur.close()
            conn.commit()
            return result
        except (Exception, Error) as error:
            print("Error while connecting to PostgreSQL", error)
            return None


    
