/* Date 입력창 날짜, 분 고정 */
function updateDateRange() {
    // 현재 날짜와 시간을 가져옴
    const now = new Date();
    const offset = now.getTimezoneOffset() * 60000; //ms단위라 60000곱해줌
    const kornow = new Date(now.getTime() - offset);
    // 현재 날짜 이후와 10일 후까지의 날짜를 계산
    if(now.getHours() < 9){
        partT="T0"
    }else{
        partT="T"
    }
    const minDate = kornow.toISOString().split("T")[0] + partT + (now.getHours()) + ":00";
    const tenDays = kornow;
    tenDays.setDate(kornow.getDate() + 9);
    const maxDate = tenDays.toISOString().split("T")[0] + "T23:59";

    // 입력 요소의 min과 max 속성을 업데이트
    document.getElementById("datetime").min = minDate;
    document.getElementById("datetime").max = maxDate;
}
// 페이지 로드 시 초기 설정, 입력 값이 변경될 때마다 날짜 범위를 업데이트
updateDateRange();
document.getElementById("datetime").addEventListener("input", updateDateRange);
/* date formatting (python input) */
function formatDT() {
    const inputDT = document.getElementById("datetime").value;
    const datePart = inputDT.split("T")[0];
    const timePart = inputDT.split("T")[1];
    // 날짜와 시간을 원하는 형식으로 조합
    const DT_py = `${datePart} ${timePart.slice(0,2)}`+"00";
    return DT_py;
}

function refreshPage() {
    // 페이지 새로고침
    location.reload();
}


/* 지역 선택 영역 */
function updateLevel2() {
    var level1 = document.getElementById('level1').value;
    var level2Select = document.getElementById('level2');
    
    // Clear previous options
    while (level2Select.options.length > 1) {
        level2Select.remove(1);
    }

    // Populate level2 options
    for (var level2 in data[level1]) {
        var option = document.createElement('option');
        option.value = level2;
        option.text = level2;
        level2Select.add(option);
    }

    // Clear level3 options
    var level3Select = document.getElementById('level3');
    while (level3Select.options.length > 1) {
        level3Select.remove(1);
    }
}
function updateLevel3() {
    var level1 = document.getElementById('level1').value;
    var level2 = document.getElementById('level2').value;
    var level3Select = document.getElementById('level3');
    
    // Clear previous options
    while (level3Select.options.length > 1) {
        level3Select.remove(1);
    }

    // Populate level3 options
    for (var level3 in data[level1][level2]) {
        var option = document.createElement('option');
        option.value = level3;
        option.text = level3;
        level3Select.add(option);
    }
}

function openModal() {
    // 모달 열기
    document.getElementById('myModal').style.display = 'block';
}
function updateInput() {
    var inputloc = document.getElementById('inputloc');
    var level1Select = document.getElementById('level1');
    var level2Select = document.getElementById('level2');
    var level3Select = document.getElementById('level3');

    var selectedLevel1 = level1Select.options[level1Select.selectedIndex].text;
    var selectedLevel2 = level2Select.options[level2Select.selectedIndex].text;
    var selectedLevel3 = level3Select.options[level3Select.selectedIndex].text;

    // Concatenate selected values and update the input
    inputloc.value = selectedLevel1 + ' ' + selectedLevel2 + ' ' + selectedLevel3;
    // 모달 닫기
    document.getElementById('myModal').style.display = 'none';

}
function closeModal() {
// 모달 닫기
document.getElementById('myModal').style.display = 'none';
}
/* region formatting (python input) */
function formatLoc() {
    let dosi = document.getElementById('level1').value;
    let gu = document.getElementById('level2').value;
    let dong = document.getElementById('level3').value;
    let output = [];
    output.push(data[dosi][gu][dong][0]);   //[{nx}, {ny}]
    output.push(`${dosi} ${gu} ${dong}`);
    return output;
}


/* form 태그 오류처리 */
document.getElementById("applyButton").addEventListener("click", function(event) {
    event.preventDefault(); // 폼 제출 막기
    submitForm(); // 사용자 정의 함수 호출
});
document.getElementById("user_location").addEventListener("click", function(event) {
    event.preventDefault(); // 폼 제출 막기
    // 추가적인 처리 코드...
});
document.getElementById("user_object").addEventListener("click", function(event) {
    event.preventDefault(); // 폼 제출 막기
    // 추가적인 처리 코드...
});


/* submit 클릭 -> 파이썬 입력값으로 */
function submitForm() {
    
    var date_to_py = formatDT();
    var loc_to_py = formatLoc();
    var obj_to_py = document.getElementById('object').value;

    console.log(date_to_py, loc_to_py, obj_to_py);
    // 다른 필요한 값도 추가하세요.

    var formData = {
        'datetime': date_to_py,
        'location': loc_to_py,
        'object': obj_to_py
        // 필요한 경우 다른 폼 값도 추가하세요.
    };

    // 데이터를 서버로 보내기 위해 AJAX 사용
    var xhr = new XMLHttpRequest();
    xhr.open('POST', '/sky-result', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onreadystatechange = function () {
        if (xhr.readyState == 4 && xhr.status == 200) {
            // 서버로부터의 응답을 처리하세요 (필요한 경우)
            console.log(xhr.responseText);
            // 페이지 전환
            window.location.href = '/sky-result';
        }
    };
    xhr.send(JSON.stringify(formData));
}