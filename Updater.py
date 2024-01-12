import re
import json
from sqlite3 import ProgrammingError
import requests
import datetime
import pymysql
import time
import calendar

conn = pymysql.connect(host='127.0.0.1', user='ykhs', password='Ykhsdata2023!@', db='ykbot', charset='utf8') # RPi MariaDB 연결
curs = conn.cursor()
NEIS_API_KEY = "dcc0a228f2fd4ae299876840395e9423" # NEIS API 인증키 입력
Office_of_Education = "ATPT_OFCDC_SC_CODE=R10" # 시도교육청 코드입력
School_Code = "SD_SCHUL_CODE=8750188" # 표준 학교코드 입력
today = datetime.datetime.now()# 오늘 날짜

def resub(): # DB값 더미데이터 제거
    tmp = re.sub(r'[-=+,#/\?:^@*\"※~ㆍ!』‘|\(\)\[\]`\'…》\”\“\’·]', '', str(curs.fetchone()))
    return tmp
def json_request(Send_URL = '', encoding = 'utf-8', success = None): # NEIS 서버에 Data 요청하는 함수
    resp = requests.get(Send_URL) # URL 전송
    return resp.text  # 전송결과 반환
def days_of_week(Date):
    A = datetime.date(int(Date.strftime("%Y")), int(Date.strftime("%m")), int(Date.strftime("%d"))).weekday()
    return A
def get_GradeClass():
    Default_URL = "https://open.neis.go.kr/hub/classInfo?KEY="+NEIS_API_KEY+"&Type=json&pIndex=1&pSize=1000&"+Office_of_Education+"&"+School_Code #URl기본 / 수정금지
    Full_URL = '%s&AY=%s' %(Default_URL, today.strftime("%Y"))
    json_req = json_request(Send_URL = Full_URL)
    json_data = json.loads(json_req)
    json_doc = json_data.get('classInfo')[1]
    first = []
    second = []
    third = []
    for i in range(json_data.get('classInfo')[0].get('head')[0].get('list_total_count')):
        json_road = json_doc.get('row')[i]
        if json_road.get('GRADE') == "1":
            first.append(json_road.get('CLASS_NM'))
        elif json_road.get('GRADE') == "2":
            second.append(json_road.get('CLASS_NM'))
        elif json_road.get('GRADE') == "3":
            third.append(json_road.get('CLASS_NM'))
    return first, second, third
def get_Schedule():  # 학사일정 받아와서 DB 에 Insert.
    Default_URL = "https://open.neis.go.kr/hub/SchoolSchedule?KEY="+NEIS_API_KEY+"&Type=json&pIndex=1&pSize=1000&"+Office_of_Education+"&"+School_Code #URl기본 / 수정금지
    try:
        total = 0
        repeat = 0
        tmp_today = today
        tmp = tmp_today + datetime.timedelta(days=10)
        curs.execute("CREATE TABLE IF NOT EXISTS bot_schedule (No INT(3), Year INT(4), Month INT(2), Day INT(2), day_of_the_week INT(1), Event VARCHAR(50)) DEFAULT CHARACTER SET UTF8")
        curs.execute("SELECT Month From bot_schedule ORDER BY MONTH ASC LIMIT 1")
        if str(resub()) == str(tmp.strftime("%m")):
            print("Schedule Data Update doesn't required.")
            pass
        else:
            curs.execute("TRUNCATE bot_schedule")
            conn.commit()
            print("Outdated Schedule Data Cleared Successfully!")
            time.sleep(1)
            print("Getting the number of Data...")
            for j in range(2):
                Full_URL = '%s&AA_FROM_YMD=%s&AA_TO_YMD=%s' %(Default_URL, tmp_today.strftime("%Y%m")+"01", tmp_today.strftime("%Y%m")+str(calendar.monthrange(int(tmp_today.strftime("%Y")), int(tmp_today.strftime("%m")))[1]))
                json_req = json_request(Send_URL = Full_URL)
                json_data = json.loads(json_req)
                json_doc = json_data.get('SchoolSchedule')[1]
                for jj in range(json_data.get('SchoolSchedule')[0].get('head')[0].get('list_total_count')):
                    json_road = json_doc.get('row')[jj]
                    if json_road.get('EVENT_NM') !="토요휴업일":
                        total += 1
                    else:
                        pass
                tmp_today = tmp_today + datetime.timedelta(days=28)
            tmp_today = today
            print("The number of the data Got Successfully!")
            time.sleep(2)
            print("Trying to Write Newest Schedule Data...\n")
            for i in range(2):
                Event = ''
                Full_URL = '%s&AA_FROM_YMD=%s&AA_TO_YMD=%s' %(Default_URL, tmp_today.strftime("%Y%m")+"01", tmp_today.strftime("%Y%m")+str(calendar.monthrange(int(tmp_today.strftime("%Y")), int(tmp_today.strftime("%m")))[1]))
                json_req = json_request(Send_URL = Full_URL)
                json_data = json.loads(json_req)
                json_doc = json_data.get('SchoolSchedule')[1]
                for ii in range(json_data.get('SchoolSchedule')[0].get('head')[0].get('list_total_count')):
                    json_road = json_doc.get('row')[ii]
                    if json_road.get('EVENT_NM') !="토요휴업일":
                        Date = datetime.datetime.strptime(json_road.get('AA_YMD'), '%Y%m%d')
                        repeat += 1
                        curs.execute("INSERT INTO ykbot.bot_schedule (No, Year, Month, Day, day_of_the_week, Event) VALUES (" + str(repeat) + ", " + Date.strftime("%Y")+ ", " + Date.strftime("%m") + ", " + Date.strftime("%d") + ", " + str(days_of_week(Date)) + ", " + "'" + json_road.get('EVENT_NM') + "'" + ")")
                        conn.commit()
                        print("Writing Newest Schedule Data... (%d / %d)" % (repeat, total))
                        time.sleep(0.01)
                    else:
                        pass
                
                tmp_today = tmp_today + datetime.timedelta(days=28)
            print("\nNewest Schedule Data Updated Successfully!")
    except ProgrammingError as error:
        print(error)
def get_Timetable():
    Default_URL = "https://open.neis.go.kr/hub/hisTimetable?KEY="+NEIS_API_KEY+"&Type=json&pIndex=1&pSize=1000&"+Office_of_Education+"&"+School_Code #URl기본 / 수정금지
    curs.execute("CREATE TABLE IF NOT EXISTS bot_timetable (day_of_the_week INT(2), Grade INT(1), Class INT(1), Time INT(1), Subject VARCHAR(20)) DEFAULT CHARACTER SET UTF8")
    curs.execute("TRUNCATE bot_timetable")
    conn.commit()
    print("Outdated Timetable Data Cleared Successfully!")
    time.sleep(1)
    try:
        print("Getting the number of Data...")
        first, second, third = get_GradeClass()
        repeat = 0
        total = 0
        d = 5-days_of_week(datetime.datetime.strptime(today.strftime("%Y%m%d"), '%Y%m%d'))
        r = 0
        if d == -1:
            r = 5
            LoadDate = today + datetime.timedelta(days = 1)
            for Grade in range(1,4):
                if Grade == 1:
                    list = first
                elif Grade == 2:
                    list = second
                elif Grade == 3:
                    list = third
                for Class in range(1,len(list)+1):
                    curs.execute("INSERT INTO ykbot.bot_timetable (day_of_the_week, Grade, Class, Time, Subject) VALUES (%s, %s, %s, %s, '%s')" %(str(6), str(Grade), str(Class), str(0), "일요일입니다."))
                    conn.commit()
        else:
            r = d
            LoadDate = today
        tmp_LoadDate = LoadDate
        for i in range(0, r+1):
            Full_URL = '%s&ALL_TI_YMD=%s' %(Default_URL, tmp_LoadDate.strftime("%Y%m%d"))
            json_req = json_request(Send_URL = Full_URL)
            if "해당하는 데이터가 없습니다." in json_req:
                pass
            else:
                json_data = json.loads(json_req)
                json_doc = json_data.get('hisTimetable')[1]
                Class_None = 0
                for i in range(json_data.get('hisTimetable')[0].get('head')[0].get('list_total_count')):
                    json_road = json_doc.get('row')[i]
                    if json_road.get('CLASS_NM') is None:
                        Class_None += 1
                total += json_data.get('hisTimetable')[0].get('head')[0].get('list_total_count') - Class_None
                tmp_LoadDate += datetime.timedelta(days = 1)
        print("The number of the data Got Successfully!")
        time.sleep(2)
        print("Trying to Write Newest Timetable Data...\n")
        for i in range(0, r+1):
            Full_URL = '%s&ALL_TI_YMD=%s' %(Default_URL, LoadDate.strftime("%Y%m%d"))
            json_req = json_request(Send_URL = Full_URL)
            if "해당하는 데이터가 없습니다." in json_req:
                pass
            else:
                json_data = json.loads(json_req)
                json_doc = json_data.get('hisTimetable')[1]
                for i in range(json_data.get('hisTimetable')[0].get('head')[0].get('list_total_count')):
                    json_road = json_doc.get('row')[i]
                    if json_road.get('CLASS_NM') is not None:
                        Date = datetime.datetime.strptime(json_road.get('ALL_TI_YMD'), '%Y%m%d')
                        curs.execute("INSERT INTO ykbot.bot_timetable (day_of_the_week, Grade, Class, Time, Subject) VALUES (%s, %s, %s, %s, '%s')" %(str(days_of_week(Date)), json_road.get('GRADE'), json_road.get('CLASS_NM'), json_road.get('PERIO'), json_road.get('ITRT_CNTNT')))
                        conn.commit()
                        repeat += 1
                    else:
                        pass
                    print("Writing Newest Timetable Data... (%d / %d)" % (repeat, total))
                    time.sleep(0.01)
                LoadDate += datetime.timedelta(days = 1)
        time.sleep(2)
        print("\nNewest Timetable Data Updated Successfully!")
    except ProgrammingError as error:
        print(error)
def get_MealMenu():
    Default_URL = "https://open.neis.go.kr/hub/mealServiceDietInfo?KEY="+NEIS_API_KEY+"&Type=json&pIndex=1&pSize=1000&"+Office_of_Education+"&"+School_Code #URl기본 / 수정금지
    try:
        repeat = 0
        total = 0
        curs.execute("CREATE TABLE IF NOT EXISTS bot_mealmenu (Year INT(4), Month INT(2), Day INT(2), day_of_the_week INT(1), Code INT(1), Menu VARCHAR(21000), Kcal VARCHAR(25)) DEFAULT CHARACTER SET UTF8")
        curs.execute("TRUNCATE bot_mealmenu")
        conn.commit()
        print("Outdated Cafeteria Menu Data Cleared Successfully!")
        time.sleep(1)
        print("Getting the number of Data...")
        d = 5-days_of_week(datetime.datetime.strptime(today.strftime("%Y%m%d"), '%Y%m%d'))
        r = 0
        if d == -1:
            r = 5
        else:
            r = d
        end_day = today + datetime.timedelta(days = r)
        Full_URL = '%s&MLSV_FROM_YMD=%s&MLSV_TO_YMD=%s' %(Default_URL, today.strftime("%Y%m%d"), end_day.strftime("%Y%m%d"))
        json_req = json_request(Send_URL = Full_URL)
        json_data = json.loads(json_req)
        json_doc = json_data.get('mealServiceDietInfo')[1]
        total = json_data.get('mealServiceDietInfo')[0].get('head')[0].get('list_total_count')
        print("The number of the data Got Successfully!")
        time.sleep(2)
        print("Trying to Write Newest Cafeteria Menu Data...\n")
        for i in range(total):
            json_road = json_doc.get('row')[i]
            Date = datetime.datetime.strptime(json_road.get('MLSV_YMD'), '%Y%m%d')
            curs.execute("INSERT INTO ykbot.bot_mealmenu (Year, Month, Day, day_of_the_week, Code, Menu, Kcal) VALUES (%s, %s, %s, %s, %s, '%s', '%s')" %(str(Date.strftime("%Y")), str(Date.strftime("%m")), str(Date.strftime("%d")), days_of_week(Date), json_road.get('MMEAL_SC_CODE'), json_road.get('DDISH_NM'), json_road.get('CAL_INFO')))
            conn.commit()
            repeat += 1
            print("Writing Newest Cafeteria Menu Data... (%d / %d)" % (repeat, total))
            time.sleep(0.01)
        time.sleep(2)
        print("\nNewest Cafeteria Menu Data Updated Successfully!")
    except ProgrammingError as error:
        print(error)

if __name__ == "__main__":
    print("\nYKHS School Info Updater for Kakao Chatbot - executed at " + today.strftime("%Y-%m-%d (%A) %H:%M:%S"))
    time.sleep(0.8)
    print("\n*******************************************************\n")
    curs.execute("CREATE TABLE IF NOT EXISTS bot_businfo (Latitude DOUBLE, Longitude DOUBLE, Year INT(4), Month INT(2), Day INT(2), Hour INT(2), Minute INT(2), Second INT(2), Server_Input_Time timestamp default current_timestamp) DEFAULT CHARACTER SET UTF8")
    time.sleep(0.8)
    print("1. Schedule Data Update\n")
    time.sleep(0.3)
    get_Schedule()
    time.sleep(0.3)
    print("\n-------------------------------------------------------\n")
    time.sleep(0.3)
    print("2. Timetable Data Update\n")
    time.sleep(0.8)
    get_Timetable()
    time.sleep(0.3)
    print("\n-------------------------------------------------------\n")
    time.sleep(0.3)
    print("3. School Meal Menu Data Update\n")
    time.sleep(0.8)
    get_MealMenu()
    time.sleep(0.3)
    print("\n-------------------------------------------------------\n")
    time.sleep(0.5)
    curs.close()
    today = datetime.datetime.now()
    print("Update Finished Successfully! - Finished at " + today.strftime("%Y-%m-%d (%A) %H:%M:%S"))
    time.sleep(2)
    print("\n*******************************************************\n")
