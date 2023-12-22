// 수직 스크롤이 발생하면 header 태그에 active 클래스 추가 및 삭제
(function(){
    const headerEl = document.querySelector("header");
    window.addEventListener("scroll", function(){
        requestAnimationFrame(scrollCheck);
    });

    function scrollCheck(){
        const browerScrollY = window.scrollY ? window.scrollY : window.pageYOffset;
        if(browerScrollY > 0){
            headerEl.classList.add('active');
        }
        else{
            headerEl.classList.remove('active');
        }
    }
})();

(function(){
    const animationMove = function(selector){
        const target = document.querySelector(selector);
        const browerScrollY = window.pageYOffset;
        const targetScrollY = target.getBoundingClientRect().top + browerScrollY;
        window.scrollTo({top: targetScrollY, behavior:'smooth'});
    }
    
    const scrollMoveEl = document.querySelectorAll("[data-animation-scroll='true']");
    console.log(scrollMoveEl);
    for(let i=0; i< scrollMoveEl.length; i++){
        scrollMoveEl[i].addEventListener("click", function(e){
            animationMove(this.dataset.target);
        })
    }
})();

function goBack() {
    // 이전 페이지로 이동
    window.history.back();
}

var map;
    function initMap() {
      // 지도 생성
      map = new kakao.maps.Map(document.getElementById('map'), {
        center: new kakao.maps.LatLng(37.5665, 126.9780), // 초기 중심 좌표 (서울)
        level: 10,
      });

      // 검색어
      var query = "천문대";

      // 검색 객체 생성
      var ps = new kakao.maps.services.Places();

      // 키워드 검색 요청
      ps.keywordSearch(query, placesSearchCB);
    }

    // 카카오 지도 API 스크립트 로드 후 초기화 함수 실행
    kakao.maps.load(initMap);

    // 키워드 검색 완료 시 호출되는 콜백함수
    function placesSearchCB(data, status, pagination) {
      if (status === kakao.maps.services.Status.OK) {
        // 검색 결과 마커 표시 및 지도 이동
        var bounds = new kakao.maps.LatLngBounds();

        for (var i = 0; i < data.length; i++) {
          displayMarker(data[i]);
          bounds.extend(new kakao.maps.LatLng(data[i].y, data[i].x));
        }

        // 검색된 위치들을 모두 포함할 수 있도록 지도 이동
        map.setBounds(bounds);
      }
    }

    // 지도에 마커를 표시하는 함수
    function displayMarker(place) {
      var marker = new kakao.maps.Marker({
        map: map,
        position: new kakao.maps.LatLng(place.y, place.x),
        title: place.place_name,
      });
    }