# Penetrate-Sky
천체 관측을 보조해주는 사이트

## 프로젝트 소개
날씨와 관측대상의 좌표값을 이용하여 천체 관측 가능여부를 알려주는 사이트입니다.

## 개발 기간
2023년 10월 27일 ~ 2023년 12월 22일

## API KEY
기상청 API(penetrate_sky.py의 forcast3(), forcast10() keys='')

카카오 지도 API(sky_result.html.j2의 appkey= 부분)

## 실행 방법
1. penetrate_sky.py 실행

    python penetrate_sky.py

2. http://127.0.0.1:5000 접속
3. 관측날짜, 관측위치, 관측대상 입력
4. Apply
