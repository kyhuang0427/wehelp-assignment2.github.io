from flask import *
import json
import mysql.connector


connection = mysql.connector.connect(host='localhost',
                                     port='3306',
                                     user='root',
                                     password='123456789',
                                     database='taipei-attractions')
cursor = connection.cursor()
app=Flask(__name__)
app.config["JSON_AS_ASCII"]=False
app.config["TEMPLATES_AUTO_RELOAD"]=True

# Pages
@app.route("/")
def index():
	return render_template("index.html")
@app.route("/attraction/<id>")
def attraction(id):
	return render_template("attraction.html")
@app.route("/booking")
def booking():
	return render_template("booking.html")
@app.route("/thankyou")
def thankyou():
	return render_template("thankyou.html")

@app.route("/api/attractions")
def get_attractions():
    try:
        page = request.args.get("page", type=int, default=0)
        keyword = request.args.get("keyword", default=None)
        
        # Calculate the offset for pagination
        offset = page * 12
        sql_query = "SELECT * FROM attractions "
        params = []
        
        if keyword:
            sql_query += "WHERE name LIKE %s OR mrt LIKE %s "
            params.extend([f"%{keyword}%", f"%{keyword}%"])
        
        sql_query += "LIMIT 12 OFFSET %s"
        params.append(offset)
        
        cursor.execute(sql_query, params)
        attractions = cursor.fetchall()
        
        data = []
        for attraction in attractions:
            # Query for images related to the attraction
            cursor.execute("SELECT url FROM attraction_images WHERE attraction_id = %s", (attraction[0],))
            images = [row[0] for row in cursor.fetchall()]
            
            data.append({
                "id": attraction[0],
                "name": attraction[1],
                "category": attraction[2],
                "description": attraction[3],
                "address": attraction[4],
                "transport": attraction[5],
                "mrt": attraction[6],
                "lat": float(attraction[7]),
                "lng": float(attraction[8]),
                "images": images
            })
        
        return jsonify({
            "nextPage": page + 1 if len(data) == 12 else None,
            "data": data
        }), 200

    except Exception as e:
        return jsonify({"error": True, "message": str(e)}), 500

# API to get attraction by ID
@app.route("/api/attraction/<int:attractionId>")
def get_attraction_by_id(attractionId):
    try:
        cursor.execute("SELECT * FROM attractions WHERE id = %s", (attractionId,))
        attraction = cursor.fetchone()
        
        if not attraction:
            return jsonify({"error": True, "message": "Attraction not found."}), 400
        
        # Query for images related to the attraction
        cursor.execute("SELECT url FROM attraction_images WHERE attraction_id = %s", (attractionId,))
        images = [row[0] for row in cursor.fetchall()]
        
        data = {
            "id": attraction[0],
            "name": attraction[1],
            "category": attraction[2],
            "description": attraction[3],
            "address": attraction[4],
            "transport": attraction[5],
            "mrt": attraction[6],
            "lat": float(attraction[7]),
            "lng": float(attraction[8]),
            "images": images
        }
        
        return jsonify({"data": data}), 200

    except Exception as e:
        return jsonify({"error": True, "message": str(e)}), 500
        
@app.route("/api/mrts")
def get_mrts():
    try:
        # 從資料庫中取得捷運站名稱，並按照其相關的景點數量由多到少排序
        sql_query = """
            SELECT mrt, COUNT(id) as count
            FROM attractions
            WHERE mrt IS NOT NULL AND mrt != ''
            GROUP BY mrt
            ORDER BY count DESC
        """
        cursor.execute(sql_query)
        results = cursor.fetchall()

        # 從結果中提取捷運站名稱
        mrt_names = [row[0] for row in results]

        return jsonify({"data": mrt_names}), 200

    except Exception as e:
        return jsonify({"error": True, "message": str(e)}), 500


app.run(host="0.0.0.0", port=3000)
