import mysql.connector
from mysql.connector import Error
from PIL import Image
import io
import base64
import time
from urllib.parse import unquote

old_pic_id = -1

def getLastImg(wait=False):
    global old_pic_id
    
    try:
        connection = mysql.connector.connect(host='db-mysql-sgp1-56454-do-user-9070143-0.b.db.ondigitalocean.com',
                                            database='fik',
                                            user='fik',
                                            password='jlq5c9g372j74r03',
                                            port = '25060')
        if connection.is_connected():
            db_Info = connection.get_server_info()
            print("Connected to MySQL Server version ", db_Info)
            cursor = connection.cursor()

            cursor.execute("select database();")
            record = cursor.fetchone()
            print("You're connected to database: ", record)

            id = """SELECT max(picID) FROM image;"""
            cursor.execute(id)
            pic_id, = cursor.fetchone()
            
            bSame = False
            while wait:
                if pic_id == old_pic_id:
                    time.sleep(5)
                    id = """SELECT max(picID) FROM image;"""
                    cursor.execute(id)
                    pic_id, = cursor.fetchone()
                else:
                    old_pic_id = pic_id
                    break
                
            if not wait:   
                for i in range(6):
                    if pic_id == old_pic_id:
                        bSame = True
                        time.sleep(5)
                        id = """SELECT max(picID) FROM image;"""
                        cursor.execute(id)
                        pic_id, = cursor.fetchone()
                    else:
                        old_pic_id = pic_id
                        bsame = False
                        break
                
            if bSame:
                print("SameImage")
                return "SameImage"
            else:
                print("Getting last image from server")
                q = """SELECT pic FROM image WHERE picID=({});""".format(pic_id)
                cursor.execute(q)
                pic_base64_byte_encoded = cursor.fetchone()
                pic_base64_urldecoded = unquote(pic_base64_byte_encoded[0].decode('utf-8')).split("data:image/jpeg;base64,")[1]

                imgdata = base64.b64decode(pic_base64_urldecoded)
                
                # with WImage(file=io.BytesIO(imgdata)) as img:
                #     print(img.size)
                #     img.virtual_pixel = 'transparent'
                #     img.distort('barrel', (0.1, 0.0, 0.0, 1.0))
                #     img.save(filename='checks_barrel.png')
                    
    
                image = Image.open(io.BytesIO(imgdata)) 
                return image
            
        
    except Error as e:
        print("Error while connecting to MySQL", e)
        cursor.close()
        connection.close()
        print("MySQL connection is closed")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")



if __name__ == "__main__":
    image = getLastImg("image")
    image.show()

# image_base64 = getLastImg("base64")
# print(image_base64)
