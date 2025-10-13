// DOM 요소 가져오기
const toggleBtn = document.querySelector('.navbar__toogleBtn');
const menu = document.querySelector('.navbar__menu');

// 토글 버튼 클릭 이벤트 리스너 추가
toggleBtn.addEventListener('click', () => {
    // 'active' 클래스를 추가하거나 제거하여 메뉴를 보이거나 숨김
    menu.classList.toggle('active');
});