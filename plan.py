from flask import jsonify
import dbconnect


def sava_plan(uid, value):
    source_id = value["source"]
    destination_id = value["destination"]
    distance = value["distance"]
    duration = value["duration"]
    air_pollution_level = value["air"]
    transportation = value["transportation"]
    is_oneway = int(value["is_oneway"])
    fixed_duration = int(value["fixed_duration"])

    con, c = dbconnect.connect()
    query = """
        INSERT INTO plan(user_id, source_id, destination_id, distance, 
        duration, air_pollution_level, transportation, is_oneway, fixed_duration) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)

    """
    c.execute(query, (uid, source_id, destination_id, distance,
                      duration, air_pollution_level, transportation, is_oneway, fixed_duration))
    con.commit()
    dbconnect.close(con, c)

    return jsonify({"Status": 1, "Message": "Successfully save your plan."})


def get_plan(uid):
    con, c = dbconnect.connect()
    query = " SELECT * FROM plan WHERE user_id = %s "
    c.execute(query, (uid,))
    rows = c.fetchall()
    dbconnect.close(con, c)
    if len(rows) == 0:
        return jsonify(dict())
    plans = dict()
    for row in rows:
        plan = dict()
        plan["source_id"] = row[2]
        plan["destination_id"] = row[3]
        plan["distance"] = row[4]
        plan["duration"] = row[5]
        plan["air"] = row[6]
        plan["transportation"] = row[7]
        plan["fixed_duration"] = row[8]
