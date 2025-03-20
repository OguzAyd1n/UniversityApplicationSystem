// main.js

// jQuery tabanlı kodlar
$(document).ready(function () {
    // Örnek: Bir elementi gizle/göster animasyonlu
    $("#toggleButton").click(function () {
        $("#hiddenElement").slideToggle(500); // 500 milisaniyede animasyonlu geçiş
    });

    // Örnek: Kullanıcıya hoş geldin mesajı ver
    $("#welcomeMessage").fadeIn(1000); // 1000 milisaniyede görünürlük animasyonu

    // Diğer jQuery tabanlı işlemleri buraya ekleyebilirsiniz
});

// Saf JavaScript kodları
document.addEventListener('DOMContentLoaded', function () {
    // Sayfa tamamen yüklendiğinde çalışacak JavaScript kodları buraya ekleyebilirsiniz

    // Örnek: Mouse ile üzerine gelinen elementi renklendir
    var hoverElement = document.getElementById('hoverElement');
    hoverElement.addEventListener('mouseover', function () {
        hoverElement.style.color = 'red';
    });
    hoverElement.addEventListener('mouseout', function () {
        hoverElement.style.color = ''; // Rengine geri döndürmek için boş bırakabilirsiniz
    });

    // Diğer JavaScript işlemleri buraya ekleyebilirsiniz
});

// Özel JavaScript fonksiyonları
function calculateTotal() {
    var totalScores = document.querySelectorAll('.rating-input');
    var total = 0;
    totalScores.forEach(function (score) {
        total += parseFloat(score.value) || 0;
    });
    var totalScoreElement = document.getElementById('totalScore');
    totalScoreElement.textContent = 'Toplam Puan: ' + total.toFixed(1);
    totalScoreElement.style.display = 'block';
}

// Diğer özel JavaScript fonksiyonlarını buraya ekleyebilirsiniz
