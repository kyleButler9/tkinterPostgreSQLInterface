import psycopg2
from config import config

TEST_COMMAND = ('SELECT 1',)
def batchExecuteSqlCommands(ini_section,commands=TEST_COMMAND):
    conn = None
    try:
        # read the connection parameters
        params = config(ini_section=ini_section)
        # connect to the PostgreSQL server
        conn = psycopg2.connect(**params)
        cur = conn.cursor()
        # create table one by one
        for command in commands:
            cur.execute(command)
        # close communication with the PostgreSQL database server
        cur.close()
        # commit the changes
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()

class DBAdmin:
    createTableCommands = (
        """
        CREATE TABLE recipients (
            recipient_id SERIAL PRIMARY KEY,
            complete Boolean,
            name VARCHAR(255),
            address VARCHAR(255),
            notes VARCHAR(255)
        )
        """,
        """
        CREATE TABLE donors(
            donor_id SERIAL PRIMARY KEY,
            name VARCHAR(255) UNIQUE,
            address VARCHAR(255)
        )
        """,
        """
        CREATE TABLE donations (
            donation_id SERIAL PRIMARY KEY,
            donor_id INTEGER NOT NULL,
            lotNumber bigint UNIQUE,
            dateReceived timestamp,
            sheetID varchar(100),
            numwiped INTEGER DEFAULT 0,
            report Boolean DEFAULT FALSE,
            FOREIGN KEY (donor_id)
                REFERENCES donors (donor_id)
        )
        """,
        """
        CREATE TABLE licenses (
            license_id SERIAL PRIMARY KEY,
            serialNumber VARCHAR(100),
            productKey VARCHAR(100)
        )
        """,
        """
        CREATE TABLE pallets (
            pallet_id SERIAL PRIMARY KEY,
            pallet INTEGER,
            recipient_id INTEGER NOT NULL,
            FOREIGN KEY (recipient_id)
                REFERENCES recipients (recipient_id)
                ON UPDATE CASCADE ON DELETE CASCADE
        )
        """,
        """
        CREATE TABLE qualities (
            quality_id SERIAL PRIMARY KEY,
            quality VARCHAR(15)
        )
        """,
        """
        CREATE TABLE deviceTypes (
            type_id SERIAL PRIMARY KEY,
            deviceType VARCHAR(15)
        )
        """,
        """
        CREATE TABLE staff (
            staff_id SERIAL PRIMARY KEY,
            name VARCHAR(255) UNIQUE,
            password VARCHAR(100),
            active Boolean,
            nameabbrev VARCHAR(100)
        )
        """,
        """
        CREATE TABLE harddrives(
            hd_id SERIAL PRIMARY KEY,
            hdpid VARCHAR(25) UNIQUE NOT NULL,
            hdsn VARCHAR(100),
            destroyed Boolean,
            sanitized Boolean,
            model VARCHAR(100),
            size VARCHAR(20),
            wipedate Timestamp,
            staff_id INTEGER,
            FOREIGN KEY (staff_id)
                REFERENCES staff (staff_id)
        )
        """, #note no unique constraint on hdsn
        """
        create table computers(
            p_id SERIAL PRIMARY KEY,
            pid VARCHAR(20) UNIQUE,
            quality_id INTEGER,
            type_id INTEGER not null,
            sn varchar(100),
            FOREIGN KEY (quality_id) REFERENCES qualities (quality_id),
            FOREIGN KEY (type_id) REFERENCES devicetypes (type_id)
        )
        """, #note that there isn't a unique constraint on device sn but there is on the pid
        """
        create table donatedgoods(
            id SERIAL PRIMARY KEY,
            donation_id INTEGER NOT NULL,
            p_id INTEGER,
            hd_id INTEGER UNIQUE,
            staff_id INTEGER NOT NULL,
            intakedate timestamp NOT NULL,
            assettag VARCHAR(255),
            FOREIGN KEY (p_id) REFERENCES computers (p_id),
            FOREIGN KEY (hd_id) REFERENCES harddrives (hd_id),
            FOREIGN KEY (staff_id) REFERENCES staff (staff_id)
        )
        """,
        """
        CREATE TABLE qualitycontrol(
            qc_id SERIAL PRIMARY KEY,
            hd_id INTEGER,
            staff_id INTEGER,
            qcDate timestamp,
            donation_id INTEGER,
            FOREIGN KEY (staff_id)
                REFERENCES staff (staff_id),
            FOREIGN KEY (donation_id)
                REFERENCES donations (donation_id),
            FOREIGN KEY (hd_id)
                REFERENCES harddrives (hd_id)
        )
        """,
        """
        CREATE TABLE missingparts(
            mp_id SERIAL PRIMARY KEY,
            quality VARCHAR(20),
            resolved Boolean,
            issue VARCHAR(255),
            notes VARCHAR(255),
            p_id INTEGER,
            pallet VARCHAR(20),
            FOREIGN KEY (p_id)
                REFERENCES computers (p_id)
        )
        """,
        """
        CREATE TABLE refurbishedDevices(
            device_id SERIAL PRIMARY KEY,
            p_id INTEGER,
            hd_id INTEGER,
            license_id INTEGER,
            FOREIGN KEY (p_id)
                REFERENCES computers (p_id),
            FOREIGN KEY (hd_id)
                REFERENCES harddrives (hd_id),
            FOREIGN KEY (license_id)
                REFERENCES licenses (license_id)
        )
        """,
        """
        CREATE TABLE internet (
            internet_id SERIAL PRIMARY KEY,
            hotspot_meid VARCHAR(25)
        )
        """,

        """
        CREATE TABLE distributedDevices (
            distdev_id SERIAL PRIMARY KEY,
            internet_id INTEGER,
            device_id INTEGER,
            recipient_id INTEGER NOT NULL,
            pallet_id INTEGER,
            FOREIGN KEY (internet_id)
                REFERENCES internet (internet_id),
            FOREIGN KEY (device_id)
                REFERENCES refurbishedDevices (device_id),
            FOREIGN KEY (recipient_id)
                REFERENCES recipients (recipient_id),
            FOREIGN KEY (pallet_id)
                REFERENCES pallets (pallet_id)
        )
        """,
    )

    initializeDatabaseCommands = (
        """
        INSERT INTO qualities(quality)
        VALUES('Fair'),('Good'),('Better'),('Best');
        """,
        """
        INSERT INTO deviceTypes(deviceType)
        VALUES('Laptop'),('Desktop'),('Loose HD'),('Unknown');
        """,
        """
        INSERT INTO donors(name)
        VALUES('Individual Donor');
        """,
        """
        INSERT INTO donations(datereceived,donor_id,lotNumber)
        VALUES('12/25/2020',
            (SELECT donor_id
            FROM donors
            WHERE name = 'Individual Donor'),0)
        """,
        """
        INSERT INTO staff(name,active,nameabbrev)
        VALUES('Kyle Butler',TRUE,'kbutler');
        """,
        """
        ALTER TABLE donatedgoods add UNIQUE (p_id,hd_id)
        """,
    )
    dropTablesCommands = (
    """
    DROP TABLE if exists qualitycontrol;
    """,
    """
    DROP TABLE IF EXISTS donatedgoods;
    """,
    """
    DROP TABLE if exists donations;
    """,
    """
    DROP TABLE if exists donors;
    """,
    """
    DROP TABLE if exists distributedDevices;
    """,
    """
    DROP TABLE IF EXISTS refurbishedDevices;
    """,
    """
    DROP table if exists missingparts;
    """,
    """
    DROP TABLE IF EXISTS computers;
    """,
    """
    DROP TABLE if exists qualities;
    """,
    """
    DROP TABLE if exists devicetypes;
    """,
    """
    DROP TABLE IF EXISTS harddrives;
    """,
    """
    DROP TABLE if exists staff;
    """,
    """
    DROP TABLE if exists licenses;
    """,
    """
    DROP TABLE IF EXISTS internet;
    """,
    """
    DROP TABLE if exists pallets;
    """,
    """
    DROP TABLE if exists recipients;
    """,
    )
if __name__ == '__main__':
    batchExecuteSqlCommands('local_launcher',commands=DBAdmin.dropTablesCommands)
    batchExecuteSqlCommands('local_launcher',commands=DBAdmin.createTableCommands)
    batchExecuteSqlCommands('local_launcher',commands=DBAdmin.initializeDatabaseCommands)
