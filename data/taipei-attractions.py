import mysql.connector
import json

def insert_data_to_db():
    # 與資料庫建立連接
    conn = mysql.connector.connect(
        host='localhost',
        port=3306,
        user='root',
        password='123456789',
        database='taipei-attractions'
    )
    cursor = conn.cursor()

    # 從JSON檔案中加載資料
    with open("taipei-attractions.json", 'r', encoding='utf-8') as file:
        data = json.load(file)
        attractions_data = data["result"]["results"]

    # 要插入 mrt_stations 表中的捷運站名稱集合
    mrt_stations_set = set()

    try:
        for attraction in attractions_data:
            name = attraction.get('name')
            category = attraction.get('CAT')
            description = attraction.get('description')
            address = attraction.get('address')
            transport = attraction.get('direction')
            mrt = attraction.get('MRT')  # 注意這裡的大寫
            lat = attraction.get('latitude')
            lng = attraction.get('longitude')
            images = attraction.get('file').split('http')

            # 只過濾jpg和png圖片
            valid_images = [image for image in images if image.endswith('.jpg') or image.endswith('.png')]

            # 插入景點資料
            cursor.execute(
                "INSERT INTO attractions (name, category, description, address, transport, mrt, latitude, longitude) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                (name, category, description, address, transport, mrt, lat, lng)
            )
            attraction_id = cursor.lastrowid

            # 為景點插入圖片
            for image in valid_images:
                cursor.execute(
                    "INSERT INTO attraction_images (attraction_id, url) VALUES (%s, %s)",
                    (attraction_id, 'http' + image)
                )

            if mrt:
                mrt_stations_set.add(mrt)

        # 在 attractions 和 attraction_images 表中插入資料後，將捷運站名稱插入到 mrt_stations 表中
        for station in mrt_stations_set:
            cursor.execute(
                "INSERT INTO mrt_stations (name) VALUES (%s)",
                (station,)
            )

        # 提交資料庫事務
        conn.commit()

    except mysql.connector.Error as err:
        # 出錯時回滾
        conn.rollback()
        print(f"錯誤: {err}")
        
    finally:
        # 關閉游標和連接
        cursor.close()
        conn.close()

if __name__ == "__main__":
    insert_data_to_db()

