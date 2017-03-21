from flask import jsonify
import dbconnect


def sava_spot(uid, value):
    spot_name = value["name"]
    spot_type = value["type"]
    is_official = int(False)
    lon = value["lon"]
    lat = value["lat"]
    description = value["description"]

    con, c = dbconnect.connect()
    query = """
        INSERT INTO spot(spot_name, spot_type, is_official, 
        longitude, longitude, description, user_id) 
        VALUES (%s, %s, %s, %s, %s, %s)

    """
    c.execute(query, (spot_name, spot_type, is_official, lon, lat, description, uid))
    con.commit()
    dbconnect.close(con, c)

    return jsonify({"Status": 1, "Message": "Successfully save your spot."})
