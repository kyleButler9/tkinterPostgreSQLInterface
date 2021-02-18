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
class DeviceInfo:
    getStaff = \
    """
    SELECT name
    FROM staff;
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
            %s,%s,%s,(SELECT s.staff_id
                    FROM staff s
                    WHERE s.name =%s),%s,%s,%s);
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
    UPDATE processing
    set sanitized = TRUE,
        destroyed = FALSE,
        wipeDate = %s
    WHERE deviceHDSN = %s
    RETURNING device_id;
    """
    noteDestroyedHD = \
    """
    UPDATE processing
    SET sanitized = FALSE,
        destroyed = TRUE,
        wipeDate = %s
    WHERE deviceHDSN = %s
    RETURNING device_id;
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
                        WHERE pid LIKE %s),%s)
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
        p.assetTag, p.destroyed, p.sanitized, s.name, p.wipeDate
    FROM processing p
    INNER JOIN deviceTypes dts on dts.type_id = p.deviceType_id
    INNER JOIN staff s on s.staff_id = p.staff_id
    WHERE p.donation_id = %s
    ORDER BY p.entryDate;
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
            name VARCHAR(255),
            address VARCHAR(255)
        )
        """,
        """
        CREATE TABLE donations (
            donation_id SERIAL PRIMARY KEY,
            donor_id INTEGER NOT NULL,
            lotNumber bigint,
            dateReceived timestamp,
            sheetID varchar(100),
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
            name VARCHAR(255),
            password VARCHAR(100),
            active Boolean
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
            deviceHDSN VARCHAR(100),
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
            donation_id INTEGER,
            hdserial VARCHAR(255)
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
