
document.addEventListener('DOMContentLoaded', function() {
  var table = document.getElementById("manga-table"); // テーブルのID
  var startedAtHeader = document.getElementById("sort-started-at"); // 連載開始時の列
  var recommendationHeader = document.getElementById("sort-recommendation"); // おすすめランクの列
  var ascStartedAt = true; // 連載開始時の昇順／降順フラグ
  var ascRecommendation = true; // おすすめランクの昇順／降順フラグ

  function sortTable(columnIndex, numeric, asc) {
    var rows = Array.from(table.getElementsByTagName("tr")).slice(1);
    rows.sort(function(rowA, rowB) {
      var valA = rowA.cells[columnIndex].innerText;
      var valB = rowB.cells[columnIndex].innerText;
      if (numeric) {
        valA = parseFloat(valA.replace('%', ''));
        valB = parseFloat(valB.replace('%', ''));
        return asc ? valA - valB : valB - valA;
      } else {
        return asc ? valA.localeCompare(valB, undefined, {numeric: true}) : valB.localeCompare(valA, undefined, {numeric: true});
      }
    });

    rows.forEach(function(row) {
      table.appendChild(row);
    });
  }

  startedAtHeader.addEventListener("click", function() {
    sortTable(1, false, ascStartedAt); // 3番目の列（連載開始時）、数値ではない
    ascStartedAt = !ascStartedAt;
  });

  recommendationHeader.addEventListener("click", function() {
    sortTable(0, true, ascRecommendation); // 2番目の列（おすすめランク）、数値
    ascRecommendation = !ascRecommendation;
  });
});



//検索画面へ飛ぶアニメーション
$(function(){
  var searchtop = $('#search-top');
  searchtop.hide();
  $(window).scroll(function () {
     if ($(this).scrollTop() > 1000) {
          searchtop.fadeIn();
     } else {
          searchtop.fadeOut();
     }
  });
  searchtop.click(function () {
     $('body, html').animate({ scrollTop: 0 }, 500);
     return false;
  });
});


// フォームを送信したときにローディングインジケータを表示する
document.addEventListener('DOMContentLoaded', function() {
  var form = document.getElementById('searchForm');
  form.onsubmit = function() {
      // ローディングインジケータを表示
      document.getElementById('loadingIndicator').style.display = 'block';
  };
});

// checkboxをクリックしたときにスライダーを有効化する
document.addEventListener('DOMContentLoaded', function() {
  var toggleCheckbox = document.getElementById('toggleSliders');
  var sliders = document.getElementsByClassName('slider_container')[0].querySelectorAll('input[type=range]');

  toggleCheckbox.addEventListener('change', function() {
      sliders.forEach(function(slider) {
          slider.disabled = !toggleCheckbox.checked;
      });
  });
});

document.addEventListener('DOMContentLoaded', function() {
  var toggleCheckbox = document.getElementById('story_age_checkbox');
  var sliders = document.getElementsByClassName('age_slider_container')[0].querySelectorAll('input[type=range]');

  toggleCheckbox.addEventListener('change', function() {
      sliders.forEach(function(slider) {
          slider.disabled = !toggleCheckbox.checked;
      });
  });
});


// スライダーの値を表示する
const rangeslider = document.getElementById('range');
noUiSlider.create(rangeslider, {
  range: {
      'min': 1950,
      'max': 2023
    },
    step: 1,
    start: [1950, 2023],
    connect: true,
    behaviour: 'tap-drag',
    tooltips: true,
    pips: {
      mode: 'steps',
      stepped: true,
      density: 10,
    }
});






