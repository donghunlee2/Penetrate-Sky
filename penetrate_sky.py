import pandas as pd
from flask import Flask, render_template, request
import requests
from datetime import datetime, timedelta
import xmltodict
import numpy as np
import re

db={}
df_10 = [{"서울특별시": "11B00000"}, {"인천광역시": "11B00000"}, {"경기도":"11B00000"}, {"대전광역시":"11C20000"}, {"세종특별자치시":"11C20000"}, {"충청남도": "11C20000"},
         {"충청북도":"11C10000"}, {"광주광역시":"11F20000"}, {"전라남도":"11F20000"}, {"전라북도":"11F10000"}, {"강원특별자치도":"11D20000"},{"대구광역시":"11H10000"}, {"경상북도": "11H10000"},
         {"부산광역시":"11H20000"}, {"울산광역시":"11H20000"}, {"경상남도":"11H20000"}, {"제주도":"11G00000"},{"이어도":"11G00000"}]
idname = [{"199": "수성"}, {"299": "금성"}, {"301": "달"}, {"499":"화성"}, {"599":"목성"}, {"699":"토성"}, {"799":"천왕성"}, {"899":"해왕성"}]


def makedf():
    df = pd.read_excel("./kor_region.xlsx", usecols='C:G')
    reglist = dict()
    #     dosi = row['1단계']
    #     gu = row['2단계']
    for index, row in df.iterrows():
        dosi = row['1단계']
        gu = row['2단계']
        dong = row['3단계']

        if dosi not in reglist:
            reglist[dosi] = {}
        if gu not in reglist[dosi]:
            if pd.isna(gu):
                gu = "선택안함"
            reglist[dosi][gu] = {}
        if dong not in reglist[dosi][gu]:
            if pd.isna(dong):
                dong = "선택안함"
            reglist[dosi][gu][dong] = []

        reglist[dosi][gu][dong].append({'nx': row['격자 X'], 'ny': row['격자 Y']})

    return reglist
    
# 1. Y-m-d => Ymd
def convert_date_format(input_date):       
    date_object = datetime.strptime(input_date, "%Y-%m-%d")
    formatted_date = date_object.strftime("%Y%m%d")
    return formatted_date
# 2. str => date
def get_input_date_string(days):
    current_date = datetime.now().date()
    date = current_date + timedelta(days)
    return date.strftime("%Y%m%d")

def forecast3(input_date, input_time):
    keys = '' # 단기예보 api key값 입력
    url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst'
    params ={'serviceKey' : keys, 
            'pageNo' : '1', 
            'numOfRows' : '10000', 
            'dataType' : 'XML', 
            'base_date' : get_input_date_string(-1),
            'base_time' : "2300", 
            'nx' : db['reg'][0]['nx'], 
            'ny' : db['reg'][0]['ny'] }

    # 값 요청 (웹 브라우저 서버에서 요청 - url주소와 파라미터)
    res = requests.get(url, params = params)

    #XML -> 딕셔너리
    xml_data = res.text
    dict_data = xmltodict.parse(xml_data)

    #값 가져오기
    weather_data = dict()
    for item in dict_data['response']['body']['items']['item']:
        if item['fcstDate'] == input_date and item['fcstTime'] == input_time:                      #입력값과 날짜가 같은
            # 하늘상태: 맑음(1) 구름많은(3) 흐림(4)
            if item['category'] == 'SKY':
                weather_data['sky'] = item['fcstValue']
            # 강수형태: 없음(0), 비(1), 비/눈(2), 눈(3), 빗방울(5), 빗방울눈날림(6), 눈날림(7)
            if item['category'] == 'PTY':
                weather_data['sky2'] = item['fcstValue']

    return weather_data

# 10일 날씨 예보 기준 날짜 계산
def get_input_hour():
    now = datetime.now()
    if now.hour<6:
        obs_hour = get_input_date_string(-1)
        input_time=obs_hour+"1800" # base_time와 base_date 구하는 함수
    else:
        obs_hour = get_input_date_string(0)
        input_time = obs_hour+"0600"
    return input_time

# 3~10 입력값 지역 코드 추출
def nxy2():
    reg_name = []
    reg_name = db['reg'][1].split()
    name_10 = reg_name[0]

    reg_index = next((i for i, d in enumerate(df_10) if name_10 in d), None)
    return df_10[reg_index][name_10]

def forecast10(input_date):
    keys = '' # 중기예보 api key값 입력
    url = 'http://apis.data.go.kr/1360000/MidFcstInfoService/getMidLandFcst'
    params ={'serviceKey' : keys, 
            'pageNo' : '1', 
            'numOfRows' : '100', 
            'dataType' : 'json', 
            'regId' : nxy2(),
            'tmFc': get_input_hour(), 
            }

    res = requests.get(url, params = params)
    dict_data= res.json()
    ''' XML로 했을 때 item이 str으로 인식
    #XML -> 딕셔너리
    xml_data = res.text 
    dict_data = xmltodict.parse(xml_data)
    '''

    afterday=get_opday(input_date)
    if afterday < 8:
        am_str = "wf" + str(afterday) + "Am"
        pm_str = "wf" + str(afterday) + "Pm"
    else:
        am_str = "wf"+str(afterday)
        pm_str = "wf"+str(afterday)

    weather_data = dict()
    for item in dict_data['response']['body']['items']['item']:
        # 딕셔너리에서 키가 존재하는지 확인하고 값을 가져옴
        if am_str in item and pm_str in item:
            weather_data['dayAm'] = item[am_str]
            weather_data['dayPm'] = item[pm_str]
            break  # 값을 찾았으면 더 이상 반복할 필요가 없으므로 루프 종료
            
    return weather_data

# forecast 3/10 계산
def get_opday(input_date):
    # Convert input_date_str to a datetime object
    input_date = datetime.strptime(input_date, '%Y%m%d')
    current_date = datetime.now().date()
    # Extract the date part from the input_date
    input_date = input_date.date()
    # Calculate the difference in days
    opday = (input_date - current_date).days

    return opday

# 날씨에 따른 관측 가능여부 판단
def proc_weather(input_date, input_time):
    opday=get_opday(input_date)
    if opday<3:
        dict_sky = forecast3(input_date, input_time)
        
        str_sky = input_date[0:4] + "년 " + input_date[4:6] + "월 " + input_date[6:] + "일 " + input_time[0:2] + "시" + input_time[2:]+"분 "+ db["reg"][1]
        if dict_sky['sky'] != None or dict_sky['sky2'] != None:
            str_sky = str_sky + " 날씨 : "
            if dict_sky['sky2'] == '0':
                if dict_sky['sky'] == '1':
                    str_sky = str_sky + "맑음"
                elif dict_sky['sky'] == '3':
                    str_sky = str_sky + "구름많음"
                elif dict_sky['sky'] == '4':
                    str_sky = str_sky + "흐림"
            elif dict_sky['sky2'] == '1':
                str_sky = str_sky + "비"
            elif dict_sky['sky2'] == '2':
                str_sky = str_sky + "비와 눈"
            elif dict_sky['sky2'] == '3':
                str_sky = str_sky + "눈"
            elif dict_sky['sky2'] == '5':
                str_sky = str_sky + "빗방울이 떨어짐"
            elif dict_sky['sky2'] == '6':
                str_sky = str_sky + "빗방울과 눈이 날림"
            elif dict_sky['sky2'] == '7':
                str_sky = str_sky + "눈이 날림"
            str_sky = str_sky + "\n"

            return Wdecision_maker(str_sky, dict_sky)
    else:
        dict_sky=forecast10(input_date)

        str_sky = input_date[0:4] + "년" + input_date[4:6] + "월" + input_date[6:] + "일 " +db["reg"][1]
        if dict_sky['dayAm'] != None or dict_sky['dayPm'] != None:
            str_sky = str_sky + " 날씨: "+ "오전 " + dict_sky['dayAm'] + ", " + "오후 " + dict_sky['dayPm'] + '\n'
            if dict_sky['dayAm'] == "맑음" and dict_sky['dayPm'] == "맑음":
                str_sky +="관측을 권장합니다."
            elif dict_sky['dayAm'] != "맑음" and dict_sky['dayPm'] == "맑음":
                str_sky +="오전에는 관측을 권장하지 않습니다."
            elif dict_sky['dayAm'] == "맑음" and dict_sky['dayPm'] != "맑음":
                str_sky +="오후에는 관측을 권장하지 않습니다."
            else:
                str_sky +="관측을 권장하지 않습니다."

        return str_sky

def Wdecision_maker(str_sky, dict_sky):
    str_sky += "구름의 양: " + dict_sky['sky'] + ", 강수형태: " + dict_sky['sky2']
    if dict_sky['sky2'] != '0' or dict_sky['sky'] != '1':
        str_sky += "\n관측을 권장하지 않습니다."
    else:
        str_sky += "\n관측을 권장합니다."
    return str_sky


'''
행성 이각 부분 시작
'''
# stop 날짜
def get_tomorrow(input_date):
    origin_date = input_date
    today = datetime.strptime(origin_date, "%Y-%m-%d")
    # 날짜 계산
    next_date = today + timedelta(days=1)
    return next_date.strftime("%Y-%m-%d")

# 2023-12-01 => 2023-DEC-01
def date_to_str(sdate):     
    input_date = datetime.strptime(sdate, "%Y-%m-%d")
    # 새로운 포맷으로 날짜를 문자열로 변환
    formatted_date_str = input_date.strftime("%Y-%b-%d")
    return formatted_date_str

# input 관측대상 좌표값 구함
def get_planet_coordinates(object, ob_date):
    base_url = "https://ssd.jpl.nasa.gov/api/horizons.api"

    params = {
        "format": "json",
        "CENTER": "500@0",      #기준 좌표계
        "COMMAND": object,
        "EPHEM_TYPE": "VECTORS",
        "START_TIME": ob_date,
        "STOP_TIME": get_tomorrow(ob_date),
        "STEP_SIZE": "1d",
        "VEC_TABLE": "1",
        "VEC_LABELS": "YES",
    }    
   
    response = requests.get(base_url, params=params)

    info=[]
    co_info={}
    coordinate = {'x': 0, 'y': 0, 'z': 0}
 
    if response.status_code == 200:
        data = response.json()
        #temp = data['result'] 내용 확인용
        coordinates = data["result"].split('*******************************************************************************\n')       
        
        # $$SOE~##EOE part
        for word in coordinates:
            if "$$SOE" in word:
                OEselect = word
        
        info = OEselect.split('\n')
        for word in info:
            if "$$" in word:
                info.remove(word)        

        for word in info:
            if date_to_str(params["START_TIME"]) in word:
                co_info[params["START_TIME"]] = coordinate
            if "X =" in word:
                # 정규표현식을 사용하여 x, y, z 좌표값 추출
                matches = re.findall(r'([-+]?\d*\.\d+E[+-]\d+)', word)
                # 결과를 실수로
                co_info[params["START_TIME"]]['x'], co_info[params["START_TIME"]]['y'], co_info[params["START_TIME"]]['z'] = map(float, matches)
                break
        return co_info[params["START_TIME"]]
    else:
        print(f"Error: {response.status_code}")
        return None

# 이각 반환
def calculate_signed_angle(vector1, vector2, reference_vector):
    dot_product = np.dot(vector1, vector2)
    magnitude_product = np.linalg.norm(vector1) * np.linalg.norm(vector2)
    cosine_similarity = dot_product / magnitude_product
    
    angle_in_radians = np.arccos(np.clip(cosine_similarity, -1.0, 1.0))
    
    #시계방향: -, 반시계방향: +
    signed_angle_in_radians = np.arctan2(np.linalg.norm(np.cross(vector1, vector2)), dot_product)
    signed_angle_in_degrees = np.degrees(signed_angle_in_radians)
    
    cross_product = np.cross(vector1, vector2)
    if np.dot(reference_vector, cross_product) < 0:
        signed_angle_in_degrees = -signed_angle_in_degrees
    
    return signed_angle_in_degrees

# id를 이름으로 변환(출력 위함)
def id_to_name(obj_id):
    obj_index = next((i for i, d in enumerate(idname) if obj_id in d), None)
    print(type(obj_index), obj_index, obj_id)
    return idname[obj_index][obj_id]

# 이각에 따른 관측 가능 여부 판단
def decision_maker(obj, SEP):
    SEP=int(SEP)
    obj_str = f"{obj}과의 이각은 {SEP}입니다.\n"
    if SEP>0:
        obj_str += "관측이 가능합니다. "
        if SEP<30:
            obj_str += "해가 지는 초저녁 서쪽에서 관측됩니다."
        elif SEP<75:
            obj_str += "18시경 남서, 21시경 서쪽에서 관측됩니다."
        elif SEP<105:
            obj_str += "18시경 남, 21시경 남서, 24시경 서쪽에서 관측됩니다."
        elif SEP<150:
            obj_str += "18시경 남동, 21시경 남, 24시경 남서, 3시경 서쪽에서 관측됩니다."
        else :
            obj_str += "18시경 동, 21시경 남동, 24시경 남, 3시경 남서, 6시경 서쪽에서 관측됩니다."
    elif SEP==0:
        obj_str += "태양과 같이 뜨고 져서 관측이 불가능합니다. "
    else:
        obj_str += "관측이 가능합니다. "
        if SEP>-30:
            obj_str += "해가 뜨기 전 새벽 동쪽에서 관측됩니다."
        elif SEP>-75:
            obj_str += "3시경 동, 6시경 남동쪽에서 관측됩니다."
        elif SEP>-105:
            obj_str += "당일 24시경 동, 3시경 남동, 6시경 남쪽에서 관측됩니다."
        elif SEP>-150:
            obj_str += "21시경 동, 24시경 남동, 3시경 남, 6시경 남서쪽에서 관측됩니다."
        else:
            obj_str += "18시경 동, 21시경 남동, 24시경 남, 3시경 남서, 6시경 서쪽에서 관측됩니다."

    return obj_str  


cache_db=[]
app = Flask(__name__)

@app.route('/')
def index():
    my_dict = makedf()
    return render_template('psindex.html.j2', data=my_dict)


@app.route('/sky-result', methods=['POST'])
def process_res():
    data = request.get_json()

    # JSON 객체에서 폼 데이터에 접근
    date_value = data.get('datetime')
    loc_value = data.get('location')
    obj_value = data.get('object')

    # 데이터 처리 (예: 출력 또는 데이터베이스에 저장)
    db['dt'] = date_value.split()
    db['reg'] = loc_value
    db['obj'] = obj_value
    #{'dt': ['2023-12-23', '1300'], 'reg': [{'nx': 90, 'ny': 91}, '대구광역시 동구 선택안함'], 'obj': '599'} 
    db['reg'][1] = db['reg'][1].replace("선택안함", "")
    
    print(db)

    weather_vs = proc_weather(convert_date_format(db['dt'][0]), db['dt'][1])

    # 지구와 태양은 항상 기준
    sun = get_planet_coordinates(10, db['dt'][0])
    sun_position = np.array([sun['x'], sun['y'], sun['z']])
    earth = get_planet_coordinates(399, db['dt'][0])
    earth_position = np.array([earth['x'], earth['y'], earth['z']])

    obj_coordinates = get_planet_coordinates(db['obj'], db['dt'][0])
    obj_position = np.array([obj_coordinates['x'], obj_coordinates['y'], obj_coordinates['z']])
    vector_ES = sun_position - earth_position
    vector_EP = obj_position - earth_position
    #이각 계산
    sep = calculate_signed_angle(vector_ES, vector_EP, reference_vector=np.array([0, 0, 1]))
    obj_vs = decision_maker(id_to_name(db['obj']), sep)

    global cache_db
    cache_db = [weather_vs, obj_vs]

    return render_template('sky_result.html.j2', data=cache_db)
    # return render_template('sky_result.html.j2', data=vs_info)


@app.route('/sky-result')
def sky_result():
    global cache_db
    return render_template('sky_result.html.j2', data=cache_db)
    # # /sky-result로 전환된 후의 페이지를 렌더링하는 코드

if __name__ == '__main__':
    app.run(debug=True)
