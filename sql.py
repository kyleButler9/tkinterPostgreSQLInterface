class DonorInfo:
    insertNewDonor = \
    """
    INSERT INTO donors(name,address)
    VALUES(%s,%s);
    """
    insertNewDonation = \
    """
    INSERT INTO donations(lotNumber,dateReceived,donor_id,sheetID)
    VALUES(%s,%s,(
        SELECT donor_id
        FROM donors
        WHERE name = %s
    ),%s);
    """
    getDonors = \
    """
    SELECT name from donors
    WHERE name ~* %s;
    """
    updateDonorInfo = \
    """
    UPDATE donations
    SET lotNumber = %s,
    dateReceived = %s
    WHERE donor_id = (
        SELECT donor_id
        FROM donors
        WHERE name = %s)
    """
    getDonationHeader = \
    """
    SELECT d.name,i.dateReceived,i.lotNumber
    FROM donors d
        INNER JOIN donations i
        ON i.donor_id = d.donor_id
    WHERE d.name ~* %s
    ORDER BY dateReceived DESC;
    """
    getDonationID = \
    """
    SELECT i.donation_id,i.sheetID
    FROM donors d
    INNER JOIN donations i
    ON i.donor_id = d.donor_id
    WHERE d.name = %s
    AND i.dateReceived = %s
    AND i.lotNumber = %s;
    """
class tidyup:
    cutdown = \
    """
    delete from processing p1
        USING processing p2
    WHERE
        p1.device_id <> p2.device_id
        AND p1.pid = p2.pid
        AND p1.devicehdsn = ''
        AND p2.devicehdsn !=''
        AND p1.donation_id = %s;
    """
class upsert_future:
    #the best way to handle this is to have
    #daily inserts go into a daily table that is then merged by this process
    #to the master table according to a process like the below
    sqlTempTableCreation = \
    """
    CREATE TEMP TABLE tempProcessing(pids VARCHAR(20),
        devicesn VARCHAR(100),
        devicehdsn VARCHAR(100))
    """
    sqlUploadMany = \
    """
    INSERT INTO tempProcessing(pids,devicesn,devicehdsn)
    VALUES(%s,%s,%s);
    """
    sqlUpsert = \
    """
    LOCK TABLE processing IN EXCLUSIVE MODE;

    UPDATE processing
    SET devicehdsn = tempProcessing.devicehdsn,

    FROM tempProcessing
    WHERE tempProcessing.pids = processing.pids
        AND processing.devicehdsn = '';

    INSERT INTO processing(pids,devicesn,devicehdsn)
    SELECT tempProcessing.pids,
            tempProcessing.devicesn,
            tempProcessing.devicehdsn
    FROM tempProcessing
    LEFT OUTER JOIN processing ON (processing.pids = tempProcessing.org_name)
    WHERE processing.pids IS NULL;
    DROP TABLE fromSheet;
    """
class DeviceInfo:
    getStaff = \
    """
    SELECT name
    FROM staff
    WHERE active=TRUE;
    """
    getStaffqc = \
    """
    SELECT name
    FROM staff
    WHERE name != %s
    AND active=TRUE;
    """
    getDeviceTypes = \
    """
    SELECT deviceType
    FROM deviceTypes;
    """
    getDeviceQualities = \
    """
    SELECT q.quality
    FROM qualities q;
    """
    insertDevice = \
    """
    INSERT INTO processing(deviceType_id,
        deviceSN,
        deviceHDSN,
        assetTag,
        staff_id,
        pid,
        donation_id,
        entryDate)
    VALUES((SELECT dt.type_id
            FROM deviceTypes dt
            WHERE dt.deviceType = %s),
            TRIM(LOWER(%s)),TRIM(LOWER(%s)),LOWER(%s),(SELECT s.staff_id
                    FROM staff s
                    WHERE s.name =%s),%s,%s,%s);
    """
    insertDeviceNoHD = \
    """
    INSERT INTO processing(deviceType_id,
        deviceSN,
        assetTag,
        staff_id,
        pid,
        donation_id,
        entryDate)
    VALUES((SELECT dt.type_id
            FROM deviceTypes dt
            WHERE dt.deviceType = %s),
            TRIM(LOWER(%s)),LOWER(%s),(SELECT s.staff_id
                    FROM staff s
                    WHERE s.name =%s),LOWER(%s),%s,%s);
    """
    updateDeviceQuality = \
    """
    UPDATE processing
    SET quality_id = (SELECT quality_id
                    FROM qualities q
                    WHERE q.quality = %s)
    WHERE deviceSN = %s;
    """
    updateDeviceType = \
    """
    UPDATE processing
    set deviceType_id = (SELECT type_id
                        FROM deviceTypes
                        WHERE deviceType = %s)
    WHERE deviceSN = %s;
    """
    insertNewDeviceType = \
    """
    INSERT INTO deviceTypes(deviceType)
    VALUES(%s)
    """
    noteWipedHD = \
    """
    with w as(
    UPDATE processing
    set sanitized = TRUE,
        destroyed = FALSE,
        wipeDate = %s,
        staff_id = (Select staff_id from staff s where s.name = %s)
    WHERE deviceHDSN = LOWER(%s)
    RETURNING donation_id as d_id
    )
    UPDATE donations
    SET numwiped = numwiped + 1
    WHERE donation_id = (select d_id from w)
    RETURNING numwiped;

    """
    noteDestroyedHD = \
    """
    with w as (
    UPDATE processing
    SET sanitized = FALSE,
        destroyed = TRUE,
        wipeDate = %s,
        staff_id = (Select staff_id from staff s where s.name = %s)
    WHERE deviceHDSN = LOWER(%s)
    RETURNING donation_id as d_id
    )
    UPDATE donations
    SET numwiped = numwiped + 1
    WHERE donation_id = (select d_id from w)
    RETURNING numwiped;
    """
    donationIDFromHDSN = \
    """
    SELECT donation_id from processing
    WHERE devicehdsn = lower(%s);
    """
class testStation:
    insertLog = \
    """
    INSERT INTO missingparts(quality,
        resolved,
        issue,
        notes,
        device_id,
        pallet)
    VALUES(%s,%s,%s,%s,(SELECT device_id
                        FROM processing
                        WHERE pid LIKE LOWER(%s)),%s)
    RETURNING mp_id,device_id;
    """
    insertSNPK = \
    """
    INSERT INTO licenses(
        serialNumber,productKey)
    VALUES(%s,%s);
    """
    licenseToPid_QualityIncluded = \
    """
    UPDATE processing
    SET license_id = (SELECT license_id
                        FROM licenses
                        WHERE serialNumber=%s),
        quality_id = (SELECT quality_id
                        FROM qualities q
                        WHERE q.quality = %s)
    WHERE pid = %s
    RETURNING device_id,license_id;
    """
    licenseToPid = \
    """
    UPDATE processing
    SET license_id = (SELECT license_id
                        FROM licenses
                        WHERE serialNumber=%s)
    WHERE pid = %s
    RETURNING device_id,license_id;
    """
    getLog = \
    """
    SELECT quality,resolved,issue,notes,pallet
    FROM missingparts mp
    INNER JOIN processing p ON mp.device_id=p.device_id
    WHERE p.pid = %s
    """
    updateLog = \
    """
    UPDATE missingparts SET
        quality = %s,
        resolved = %s,
        issue = %s,
        notes = %s,
        pallet = %s
    RETURNING mp_id,device_id;
    """
class TechStationSQL:
    licenseFromSN = \
    """
    SELECT pid,serialNumber,productKey
    FROM processing p
    INNER JOIN licenses l ON l.license_id = p.license_id
    WHERE p.deviceSN = %s;
    """
class Report:
    donationInfo = \
        """
        SELECT d.name, don.dateReceived, don.lotNumber
        FROM donors d
        INNER JOIN donations don ON don.donor_id = d.donor_id
        WHERE don.donation_id = %s;
        """
    deviceInfo = \
    """
    SELECT dts.deviceType, p.deviceSN, p.deviceHDSN,
        p.assetTag, p.destroyed, p.sanitized, s.nameabbrev,
        CASE WHEN p.deviceHDSN = '' THEN TO_CHAR(p.entryDate,'MM/DD/YYYY HH24:MI')
        ELSE TO_CHAR(p.wipeDate,'MM/DD/YYYY HH24:MI')
        END AS date
    FROM processing p
    INNER JOIN deviceTypes dts on dts.type_id = p.deviceType_id
    INNER JOIN staff s on s.staff_id = p.staff_id
    WHERE p.donation_id = %s
    ORDER BY p.entryDate;
    """
    qcInfo = \
    """
    SELECT qc.hdserial, TO_CHAR(qc.qcDate,'MM/DD/YYYY'),s.name
    FROM qualitycontrol qc
    INNER JOIN staff s on qc.staff_id =s.staff_id
    WHERE qc.donation_id = %s;
    """
    qualityControlLog = \
    """
    INSERT INTO qualitycontrol(hdserial,qcDate,donation_id,staff_id)
    VALUES(%s,%s,%s,
        (SELECT s.staff_id from staff s
        WHERE s.name = %s));
    Update donations
    set numwiped = 2
    WHERE donation_id = %s;
    """
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
        CREATE TABLE processing (
            device_id SERIAL PRIMARY KEY,
            pid VARCHAR(20),
            category VARCHAR(20),
            quality_id INTEGER,
            deviceType_id INTEGER,
            deviceSN VARCHAR(100),
            deviceHDSN VARCHAR(100) UNIQUE,
            destroyed Boolean,
            sanitized Boolean,
            staff_id INTEGER,
            entryDate timestamp,
            wipeDate timestamp,
            assetTag VARCHAR(255),
            donation_id INTEGER NOT NULL,
            license_id INTEGER,
            recipient_id INTEGER,
            pallet_id INTEGER,
            FOREIGN KEY (staff_id)
                REFERENCES staff (staff_id),
            FOREIGN KEY (donation_id)
                REFERENCES donations (donation_id),
            FOREIGN KEY (license_id)
                REFERENCES licenses (license_id),
            FOREIGN KEY (recipient_id)
                REFERENCES recipients (recipient_id),
            FOREIGN KEY (pallet_id)
                REFERENCES pallets (pallet_id),
            FOREIGN KEY (quality_id)
                REFERENCES qualities (quality_id),
            FOREIGN KEY (deviceType_id)
                REFERENCES deviceTypes (type_id)
        )
        """,
        """
        CREATE TABLE qualitycontrol(
            qc_id SERIAL PRIMARY KEY,
            hdserial VARCHAR(255),
            staff_id INTEGER,
            qcDate timestamp,
            donation_id INTEGER,
            FOREIGN KEY (staff_id)
                REFERENCES staff (staff_id),
            FOREIGN KEY (donation_id)
                REFERENCES donations (donation_id)
        )
        """,
        """
        CREATE TABLE missingparts(
            mp_id SERIAL PRIMARY KEY,
            quality VARCHAR(20),
            resolved Boolean,
            issue VARCHAR(255),
            notes VARCHAR(255),
            device_id INTEGER,
            pallet VARCHAR(20),
            FOREIGN KEY (device_id)
                REFERENCES processing (device_id)
        )
        """,
    )

    initializeDatabaseCommands = (
        """
        INSERT INTO qualities(quality)
        VALUES('good'),('better'),('best');
        """,
        """
        INSERT INTO deviceTypes(deviceType)
        VALUES('Laptop'),('Desktop');
        """,
        """
        INSERT INTO donors(name)
        VALUES('BDEC');
        """,
        """
        INSERT INTO donations(datereceived,donor_id,lotNumber,sheetID)
        VALUES('12/25/2020',
            (SELECT donor_id
            FROM donors
            WHERE name = 'BDEC'),0,
            '1FxJ7qYRYnN2CaxB08emRUtk_X4psalprlvs0fYrYe6A')
        """,
        """
        INSERT INTO staff(name)
        VALUES('Employee M'),('Employee R'),('Kyle Butler');
        """,
    )
    dropTablesCommands = (
    """
    DROP table missingparts;
    """,
    """
    DROP TABLE processing;
    """,
    """
    DROP TABLE pallets;
    """,
    """
    DROP TABLE licenses;
    """,
    """
    DROP TABLE recipients;
    """,
    """
    DROP TABLE donations;
    """,
    """
    DROP TABLE donors;
    """,
    """
    DROP TABLE qualities;
    """,
    """
    DROP TABLE devicetypes;
    """,
    """
    DROP TABLE qualitycontrol;
    """,
    """
    DROP TABLE staff;
    """,
    )
