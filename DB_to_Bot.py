from flask import Flask, jsonify, request
from datetime import timedelta
import pymysql
import re
import math
import datetime
import requests


conn = pymysql.connect(host='127.0.0.1', user='ykhs', password='Ykhsdata2023!@', db='ykbot', charset='utf8') # RPi MariaDB 연결
curs = conn.cursor()
today = datetime.datetime.now()
Date = datetime.datetime.strptime(today.strftime("%Y%m%d"), '%Y%m%d')
days = ['월', '화', '수', '목', '금', '토', '일']
conn.autocommit(True)

def resub(): # [공통] DB값 더미데이터 제거
    tmp = re.sub(r'[-=+,#/\?:^@*\"※~ㆍ!』‘|\(\)\[\]`\'…》\”\“\’·]', '', str(curs.fetchone()))
    return tmp
def convert_day_of_the_week():
    A = datetime.date(int(Date.strftime("%Y")), int(Date.strftime("%m")), int(Date.strftime("%d"))).weekday()
    return A
#
def resub_Menu(): # [급식] DB값 더미데이터 제거
    tmp = re.sub(r'[-=+,#/\?:^@*\"※~ㆍ!』‘|\[\]`\'…》\”\“\’·]', '', str(curs.fetchone()))
    return tmp
def resub_enter(text): # [급식] Br 엔터
    text = re.sub(r'<br>', '\n', text) # <br> 을 줄바꿈으로 치환
    return text #치환결과 리턴함.
#
def resub_Schedule(): # [급식] DB값 더미데이터 제거
    tmp = re.sub(r'[-=+,#\?:^@*\"※~ㆍ!』‘|\[\]`\'…》\”\“\’·]', '', str(curs.fetchone()))
    return tmp
#
def get_position_Lat(): # [GPS] DB값 로드 (위도 Lat)
    try:
        Lat = ""
        curs.execute("SELECT Latitude FROM bot_businfo ORDER BY Server_Input_Time DESC LIMIT 1") # Lat_read_query
        Lat = resub()
    except:
        Lat = 0.0
    return Lat
def get_position_Lon(): # [GPS] DB값 로드 (경도 Lon)
    try:
        Lon = ""
        curs.execute("SELECT Longitude FROM bot_businfo ORDER BY Server_Input_Time DESC LIMIT 1") #Lon_read_query
        Lon = resub()
    except:
        Lon = 0.0
    return Lon
def get_date_BUS(): # [GPS] DB값 로드 (좌표 기록시간)
    try:
        Year = Month = Day = Hour = Minute = Second = ""
        curs.execute("SELECT Year FROM bot_businfo ORDER BY Server_Input_Time DESC LIMIT 1") #Year_read_query
        Year=resub()
        curs.execute("SELECT Month FROM bot_businfo ORDER BY Server_Input_Time DESC LIMIT 1") #Month_read_query
        Month=resub()
        curs.execute("SELECT Day FROM bot_businfo ORDER BY Server_Input_Time DESC LIMIT 1") #Day_read_query
        Day=resub()
        curs.execute("SELECT Hour FROM bot_businfo ORDER BY Server_Input_Time DESC LIMIT 1") #Hour_read_query
        Hour=resub()
        curs.execute("SELECT Minute FROM bot_businfo ORDER BY Server_Input_Time DESC LIMIT 1") #Minute_read_query
        Minute=resub()
        curs.execute("SELECT Second FROM bot_businfo ORDER BY Server_Input_Time DESC LIMIT 1") #Second_read_query
        Second=resub()
        Date = Year+"년 "+Month+"월 "+Day+"일 ("+days[convert_day_of_the_week()]+") "+Hour+"시 "+Minute+"분 "+Second+"초"
    except:
        Date = "None"
    return Date
def convertURL(): # [GPS] 위/경도 -> 도분초 (단위변환) & URL변환
    try:
        Lat = float(get_position_Lat())
        Lon = float(get_position_Lon())
        do_Lat = math.floor(Lat)
        do_Lon = math.floor(Lon)
        bun_Lat = math.floor((Lat-do_Lat)*60)
        bun_Lon = math.floor((Lon-do_Lon)*60)
        cho_Lat = (((Lat-do_Lat)*60)-math.floor((Lat-do_Lat)*60))*60
        cho_Lon = (((Lon-do_Lon)*60)-math.floor((Lon-do_Lon)*60))*60
        URL = "https://www.google.com/maps/place/"+str(do_Lat)+"%C2%B0"+str(bun_Lat)+"'"+str(cho_Lat)+"%22N+"+str(do_Lon)+"%C2%B0"+str(bun_Lon)+"'"+str(cho_Lon)+"%22E"
    except:
        URL = "\n\n일시적 오류입니다.\n\n※ 문제가 지속되면 학생회로 문의바랍니다."
    return URL
#
def get_menu(day_of_the_week): # [급식] DB에서 급식메뉴 로드
    try:
        curs.execute("SELECT Year FROM bot_mealmenu WHERE day_of_the_week=%s" %(day_of_the_week)) # year_read_query
        Year = resub()
        curs.execute("SELECT Month FROM bot_mealmenu WHERE day_of_the_week=%s" %(day_of_the_week)) # Month_read_query
        Month = resub()
        curs.execute("SELECT Day FROM bot_mealmenu WHERE day_of_the_week=%s" %(day_of_the_week)) # Day_read_query
        Day = resub()
        curs.execute("SELECT Menu FROM bot_mealmenu WHERE day_of_the_week=%s AND Code = 1" %(day_of_the_week)) # breakfast_read_query
        Breakfast = resub_enter(resub_Menu()).strip("(")[:-1]
        curs.execute("SELECT Menu FROM bot_mealmenu WHERE day_of_the_week=%s AND Code = 2" %(day_of_the_week)) # lunch_read_query
        Lunch = resub_enter(resub_Menu()).strip("(")[:-1]
        curs.execute("SELECT Menu FROM bot_mealmenu WHERE day_of_the_week=%s AND Code = 3" %(day_of_the_week)) # dinner_read_query
        Dinner = resub_enter(resub_Menu()).strip("(")[:-1]
        footnote = ""
        if "Non" in Breakfast:
            Breakfast = "메뉴 존재 X / 메뉴 로드 불가"
            footnote = "※ 급식을 실시함에도 메뉴가 출력되지 않으면, 학생회로 문의바랍니다.\n\n"
        if "Non" in Lunch:
            Lunch = "메뉴 존재 X / 메뉴 로드 불가"
            footnote = "※ 급식을 실시함에도 메뉴가 출력되지 않으면, 학생회로 문의바랍니다.\n\n"
        if "Non" in Dinner:
            Dinner = "메뉴 존재 X / 메뉴 로드 불가"
            footnote = "※ 급식을 실시함에도 메뉴가 출력되지 않으면, 학생회로 문의바랍니다.\n\n"
        Menu = "[아침]\n" + Breakfast + "\n\n[점심]\n" + Lunch + "\n\n[저녁]\n" + Dinner
        responsedata = Year + "년 " + Month + "월 " + Day + "일 " + days[day_of_the_week] +"요일 급식\n\n￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣\n" + Menu + "\n\n￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣\n"+footnote+"※ 식단 우측에 표시된 번호는 알레르기 유발 가능성이 있는 식재료를 의미합니다."
        if "Non" in Month:
            responsedata = "급식메뉴 정보가 없습니다.\n(급식 여부 확인요망)\n\n※ 문제가 지속되면 학생회로 문의바랍니다"
    except:
        responsedata = "급식메뉴 정보가 없습니다.\n(급식 여부 확인요망)\n\n※ 문제가 지속되면 학생회로 문의바랍니다"
    return responsedata
#
def get_timetable(Grade, Class): # 학년 반 입력받아 시간표 로드
    try:
        Subject = ""
        curs.execute("SELECT COUNT(*) FROM bot_timetable WHERE Grade=%s AND Class=%s AND day_of_the_week=%s" %(Grade, Class, convert_day_of_the_week()))
        for i in range(int(resub())):
            curs.execute("SELECT Subject FROM bot_timetable WHERE Grade=%s AND Class=%s AND day_of_the_week=%s AND Time=%s" %(Grade, Class, convert_day_of_the_week(), i))
            Subject = Subject + "\n" + str(i+1) + ". " + resub()
        showText = Grade+"학년 "+Class+"반 "+"\'"+days[convert_day_of_the_week()]+"요일\'"+" 시간표입니다.\n\n￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣"+str(Subject)+"\n\n￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣\n표시되는 선택과목과 자신의 선택과목이 불일치할 수 있습니다.\n자신의 선택과목군을 숙지하여 이용에 참고하기 바랍니다."
    except:
        showText = "시간표 정보가 없습니다.\n(수업 여부 확인요망)\n\n※ 문제가 지속되면 학생회로 문의바랍니다"
    return showText
#
def get_schedule(): # 학사일정 로드
    try:
        Schedule = today.strftime("%Y")+"년 "+today.strftime("%m")+"월 학사일정입니다.\n\n￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣"
        curs.execute("SELECT COUNT(*) FROM bot_schedule WHERE Month=%s" %(today.strftime("%m")))
        for i in range(int(resub())):
            curs.execute("SELECT Event FROM bot_schedule WHERE No=%s" %(i+1))
            tmp = resub_Schedule().strip("(")[:-1]
            curs.execute("SELECT Month FROM bot_schedule WHERE No=%s" %(i+1))
            Month = resub()
            curs.execute("SELECT Day FROM bot_schedule WHERE No=%s" %(i+1))
            Day = resub()
            curs.execute("SELECT day_of_the_week FROM bot_schedule WHERE No=%s" %(i+1))
            converted_date = Month+"월 "+Day+"일("+days[int(resub())]+"): "
            Schedule +="\n"+converted_date+tmp
        Schedule += "\n\n￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣￣\n※ 학교 사정에 의해 일정이 변동될 수 있습니다."
    except:
        Schedule = "학사일정 정보가 없습니다.\n(학교에서 등록하지 않았거나 일시적 오류임)\n\n※ 문제가 지속되면 학생회로 문의바랍니다."
    return Schedule
#
application = Flask(__name__) # Server Setting.
@application.route("/API/Call_Data", methods=["POST"]) # Server Setting.
def SendToBot():
    conn.ping(reconnect=True)
    payloads = request.get_json()
    requestdata = str(payloads['action']['params'])
    responsedata = ''
    try:
        if "Bus" in requestdata:   # 버스 정보 요청
            if requestdata == "{'Bus': 'Position'}": # 버스위치 요청
                responsedata = "현재 스쿨버스의 위치는 다음과 같습니다.\n\n버스와의 통신 상태, 서버 상태 등에 따라 실제 차량의 위치와 차이가 발생할 수 있으므로 버스 노선과 마지막 위치 수신일자를 꼭 참고하십시오.\n\n서비스 오류 및 착오로 인한 피해는 책임지지 않습니다. 이용 시 참고하십시오.\n\n출력되는 URL 을 클릭하여 상세 위치를 파악하시기 바랍니다.\n\n"
                date = str(get_date_BUS()) # 날짜 Reading
                if "None" in date: # 날짜 Reading 실패
                    responsedata += "***************************\n\n버스 운행 시작 전입니다.\n버스 운행 중이라면, 잠시 후 다시 시도해주시기 바랍니다.\n\n※ 문제가 지속되면 학생회로 문의바랍니다. \n\n(Error 1 - Date Reading Failed...)"
                elif str(get_position_Lat()) == "0.0": # Latitude Reading 실패
                    responsedata += "***************************\n\n위치정보를 불러올 수 없습니다.\n잠시 후 다시 시도해주시기 바랍니다.\n\n※ 문제가 지속되면 학생회로 문의바랍니다. \n\n(Error 2 - Lat Reading Failed...)"
                elif str(get_position_Lon()) == "0.0": # Longitude Reading 실패
                    responsedata += "***************************\n\n위치정보를 불러올 수 없습니다.\n잠시 후 다시 시도해주시기 바랍니다.\n\n※ 문제가 지속되면 학생회로 문의바랍니다. \n\n(Error 3 - Lon Reading Failed...)"
                else: # 날자, Latitude, Longitude Reading 성공 -> URL 반환
                    responsedata += "***************************\n\n<마지막 위치 수신일자>\n"+ date + "\n\n<URL>\n"+str(convertURL())
            elif requestdata == "{'Bus': 'School'}": # 등교 노선 요청
                today = datetime.datetime.now() # 요청일 추출
                if today.month%2!=0: # 요청 기준 홀수달일 때
                    responsedata = "http://210.104.6.82:26615/Odd_go_to_school.png"
                else:  # 요청 기준 짝수달일 때
                    responsedata = "http://210.104.6.82:26615/Even_go_to_school.png"
            elif requestdata == "{'Bus': 'Home_(studyX)'}": # 하교 노선 요청
                responsedata = "http://210.104.6.82:26615/go_to_Home.png"
            elif requestdata == "{'Bus': 'Home_(studyO)'}": # 야간자습노선 요청
                responsedata = "http://210.104.6.82:26615/Study_go_to_school.png"
            if requestdata == "{'Bus': 'School'}" or requestdata == "{'Bus': 'Home_(studyX)'}" or requestdata == "{'Bus': 'Home_(studyO)'}":
                response = {  # 요청노선 Img 반환
                    "version": "2.0",
                    "template": {"outputs": [{"simpleImage": {
                                    "imageUrl": responsedata,
                                    "altText": "노선을 조회할 수 없습니다.\n\n※ 문제가 지속되면 학생회로 문의바랍니다"}}]}}
            else: 
                response = {
                    "version": "2.0",
                    "template": {"outputs": [{"simpleText": {"text": responsedata }}]}}
        elif "Meal" in requestdata: # 급식 정보 요청
            if requestdata == "{'Meal': 'Today'}": # 오늘 급식 요청
                responsedata = get_menu(convert_day_of_the_week())
            elif requestdata == "{'Meal': 'Monday'}": # 월요일 급식 요청
                day_of_the_week = 0
                responsedata = get_menu(day_of_the_week)
            elif requestdata == "{'Meal': 'Tuesday'}": # 화요일 급식 요청
                day_of_the_week = 1
                responsedata = get_menu(day_of_the_week)
            elif requestdata == "{'Meal': 'Wednesday'}": # 수요일 급식 요청
                day_of_the_week = 2
                responsedata = get_menu(day_of_the_week)
            elif requestdata == "{'Meal': 'Thursday'}": # 목요일 급식 요청
                day_of_the_week = 3
                responsedata = get_menu(day_of_the_week)
            elif requestdata == "{'Meal': 'Friday'}": # 금요일 급식 요청
                day_of_the_week = 4
                responsedata = get_menu(day_of_the_week)
            elif requestdata == "{'Meal': 'Saturday'}": # 토요일 급식 요청
                day_of_the_week = 5
                responsedata = get_menu(day_of_the_week)
            elif requestdata == "{'Meal': 'Allergy'}": # 급식 알레르기 정보 요청
                responsedata = "알레르기 정보는 다음과 같습니다.\n\n1. 난류, 2. 우유, 3. 메밀, 4. 땅콩 \n5. 대두, 6. 밀, 7. 고등어, 8. 게 \n9. 새우, 10. 돼지고기, 11. 복숭아 \n12. 토마토, 13. 아황산염, 14. 호두\n15. 닭고기, 16. 쇠고기, 17. 오징어\n18. 조개류(굴,전복,홍합 등)"
            response={
                        "version": "2.0",
                        "data": {"Meal": responsedata}}
        elif "Grade" in requestdata: # 시간표 요청
            Grade = payloads['action']['params']['Grade']
            Class = payloads['action']['params']['Class']
            if get_timetable(Grade, Class) == "시간표 정보가 없습니다.\n(수업 여부 확인요망)": #시간표 없을 때
                response={
                    "version": "2.0",
                    "data": {
                        "Subject": "시간표 정보가 없습니다.\n(수업 여부 확인요망)\n\n※ 문제가 지속되면 학생회로 문의바랍니다.\n\n※학기 초인 경우, NEIS 에 시간표가 미 등록되어 불러올 수 없습니다."
                    }}
            else: # 시간표 있을 때
                response={
                    "version": "2.0",
                    "data": {
                        "Subject": get_timetable(Grade, Class),
                    }}
        elif requestdata == "{}":
            response={
                    "version": "2.0",
                    "data": {"Schedule": get_schedule()}}
        return jsonify(response)
    except:
        responsedata = "일시적 오류입니다.\n\n※ 문제가 지속되면 학생회로 문의바랍니다."

if __name__ == "__main__":
    application.run(host='0.0.0.0', port=26614, debug = False) # Server Setting.
