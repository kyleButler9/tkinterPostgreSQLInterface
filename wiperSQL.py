class DeviceInfo:
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
class Report:
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
class hdsearch:
    longsearch = \
    """
    with basicTrim as (
        SELECT devicehdsn as hd,
        CASE
            WHEN destroyed is TRUE THEN 'destroyed'
            WHEN sanitized is TRUE THEN 'sanitized'
            ELSE 'unknown'
            END AS status
        FROM processing
        WHERE devicehdsn ~* SUBSTRING(%s,1,
            length(%s)-1)
        OR devicehdsn ~* SUBSTRING(%s,2,
            length(%s))
    )
    CASE
        WHEN count((select devicehdsn from basicTrim)) > 0
        THEN (SELECT * from basicTrim)
        ELSE
            SELECT devicehdsn,
            CASE
                WHEN destroyed is TRUE THEN 'destroyed'
                WHEN sanitized is TRUE THEN 'sanitized'
                ELSE 'unknown'
                END AS status
            FROM processing
            WHERE devicehdsn ~* SUBSTRING(%s,4,4)
            OR devicehdsn ~* SUBSTRING(%s,7,4)
    """
