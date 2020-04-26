import pymysql
import requests

with open ("/run/secrets/mysql_userr", "r") as secrets:
    user = secrets.readline().replace("\n","")

with open ("/run/secrets/mysql_rpass", "r") as secrets:
    password = secrets.readline().replace("\n","")

def main():

    # check if nextcloud is up
    url = "http://nextcloud:80/ocs/v2.php/apps/serverinfo/api/v1/info"

    payload = {}
    headers = {'Authorization': 'Basic YWJhc3RvczphYmFzdG9z'}

    try:
        response = requests.request("GET", url, headers=headers, data=payload)
        # print(response)
    except Exception as e:
        print(e)

    # connection
    mysql = pymysql.connect(host="db", user=user, passwd=password, db="appBD", port=3306)

    # create cursor
    cur = mysql.cursor()

    # insert into appDB result of healthcheck

    try:
        cur.execute('UPDATE healthcheck SET response=%s, reg_date=NULL WHERE service="nextcloud"', response.status_code)
    except Exception as e:
        print(e)

    mysql.commit()

    cur.close()


if __name__ == '__main__':
    main()
