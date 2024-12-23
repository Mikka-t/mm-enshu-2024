let input_categories =[]
if (document.getElementById('liData').value){
    document.getElementById('liData').value = document.getElementById('liData').value.replace('_enc-28', ' '); //まず隠しフォーム内の文字列をreplaceした値に直す
    const items = document.querySelectorAll('#list-container li');

    // 各アイテムに対してループ処理
    items.forEach(item => {
        // リストアイテムの内部HTMLから 'enc-28' 文字列を削除
        const updatedHTML = item.innerHTML.replace('_enc-28', ' ');
        
        // 更新されたHTMLをリストアイテムに設定
        item.innerHTML = updatedHTML;
    });

    input_categories = document.getElementById('liData').value.split(','); //初めから入力されている場合はそちらを使用する
    document.getElementById('inputText').removeAttribute("required"); //入力されていないあらーとを回避
}
// フォームを取得
var form = document.getElementById('searchForm');

const autoCompleteJS = new autoComplete({
placeHolder: "例:いちごタルト、カレー、ショートケーキ　など",
selector: "#autoComplete",
data: {
src: full_categoires_list,
cache: true,
},
resultItem: {
highlight: true
},
resultsList: {
maxResults: 500, // 表示する結果の最大数を設定
},
events: {
input: {
selection: (event) => {
    const selection = event.detail.selection.value;
    //input_categories.push(selection); // 選択されたクエリをリストに追加
    //console.log(input_categories); // 選択されたクエリをコンソールに表示
    // alert(selection)
    
    autoCompleteJS.input.value = ""; // 入力フィールドをクリア
    addTask(selection);
}
}
}
});


const listContainer = document.getElementById("list-container");

function addTask(word){

    if (input_categories.includes(word)){
        //すでに存在しているものが選択された場合はエラーが出るように！
        //alert("すでに存在しています！");
        console.log("重複して選んでいます！");
    }else{
        let li =document.createElement("li");
        li.innerHTML = word;
        listContainer.appendChild(li);
        let span =document.createElement("span");
        span.innerHTML ="\u00d7"; /*クローズのやつ？らしい */
        li.prepend(span); //前に追加する
        input_categories.push(word);
        console.log(input_categories);
        document.getElementById('liData').value = input_categories.join(','); //隠しフォームに追加している
        if (input_categories.length !==0){
            document.getElementById('inputText').removeAttribute("required");
        }else{
            document.getElementById('inputText').setAttribute("required","");
        }
    }
    
}

listContainer.addEventListener("click",function(e){

    if(e.target.tagName === "SPAN"){
        remove_word = e.target.parentElement.innerHTML.replace(/<span.*<\/span>/, ''); //正規表現でgeneratedされたidを消去している
        // remove_index = input_categories.indexOf(remove_word);
        input_categories = input_categories.filter((value)=>value !== remove_word);
        // alert(remove_word+"を消去しました");
        e.target.parentElement.remove();
        document.getElementById('liData').value = input_categories.join(','); //隠しフォームに追加している
        if (input_categories.length !==0){
            document.getElementById('inputText').removeAttribute("required");
        }else{
            document.getElementById('inputText').setAttribute("required","");
        }
        
    }
},false);


// 材料用のコード．上記のコードとほぼ同じ．改修の余地あり
let input_categoriesIng =[]
if (document.getElementById('IngData').value){
    document.getElementById('IngData').value = document.getElementById('IngData').value.replace('_enc-28', ' '); //まず隠しフォーム内の文字列をreplaceした値に直す
    const itemsIng = document.querySelectorAll('#list-containerIng li');

    // 各アイテムに対してループ処理
    itemsIng.forEach(itemIng => {
        // リストアイテムの内部HTMLから 'enc-28' 文字列を削除
        const updatedHTMLIng = itemIng.innerHTML.replace('_enc-28', ' ');
        
        // 更新されたHTMLをリストアイテムに設定
        itemIng.innerHTML = updatedHTMLIng;
    });

    input_categoriesIng = document.getElementById('IngData').value.split(','); //初めから入力されている場合はそちらを使用する
    document.getElementById('inputText').removeAttribute("required"); //入力されていないあらーとを回避
}
// フォームを取得
var formIng = document.getElementById('searchForm');

const autoCompleteJSIng = new autoComplete({
placeHolder: "例:いちご、にんじん、じゃがいも　など",
selector: "#autoCompleteIng",
data: {
src: full_categoires_listIng,
cache: true,
},
resultItem: {
highlight: true
},
resultsList: {
maxResults: 500, // 表示する結果の最大数を設定
},
events: {
input: {
selection: (event) => {
    const selection = event.detail.selection.value;
    //input_categories.push(selection); // 選択されたクエリをリストに追加
    //console.log(input_categories); // 選択されたクエリをコンソールに表示
    // alert(selection)
    
    autoCompleteJSIng.input.value = ""; // 入力フィールドをクリア
    addTaskIng(selection);
}
}
}
});


const listContainerIng = document.getElementById("list-containerIng");

function addTaskIng(word){

    if (input_categoriesIng.includes(word)){
        //すでに存在しているものが選択された場合はエラーが出るように！
        //alert("すでに存在しています！");
        console.log("重複して選んでいます！");
    }else{
        let Ing =document.createElement("li");
        Ing.innerHTML = word;
        listContainerIng.appendChild(Ing);
        let span =document.createElement("span");
        span.innerHTML ="\u00d7"; /*クローズのやつ？らしい */
        Ing.prepend(span); //前に追加する
        input_categoriesIng.push(word);
        console.log(input_categoriesIng);
        document.getElementById('IngData').value = input_categoriesIng.join(','); //隠しフォームに追加している
        if (input_categoriesIng.length !==0){
            document.getElementById('inputText').removeAttribute("required");
        }else{
            document.getElementById('inputText').setAttribute("required","");
        }
    }
    
}

listContainerIng.addEventListener("click",function(e){

    if(e.target.tagName === "SPAN"){
        remove_word = e.target.parentElement.innerHTML.replace(/<span.*<\/span>/, ''); //正規表現でgeneratedされたidを消去している
        // remove_index = input_categories.indexOf(remove_word);
        input_categoriesIng = input_categoriesIng.filter((value)=>value !== remove_word);
        // alert(remove_word+"を消去しました");
        e.target.parentElement.remove();
        document.getElementById('IngData').value = input_categoriesIng.join(','); //隠しフォームに追加している
        if (input_categoriesIng.length !==0){
            document.getElementById('inputText').removeAttribute("required");
        }else{
            document.getElementById('inputText').setAttribute("required","");
        }
        
    }
},false);


// // フォームを取得
// var form = document.getElementById('searchForm');

// // フォームの送信イベントに関数をバインド
// form.onsubmit = function() {
// // input_categories 配列のデータを文字列に変換
// var liData = input_categories.join(',');

// // 隠しフィールドにセット
// document.getElementById('liData').value = liData;

// };

// //下記のコードはinput_categoriesをPOST内容に加えるもの（GPTによって作成）→Ajax動作なのでPOSTされた後にページが更新されず断念
// document.getElementById('searchForm').addEventListener('submit', function(e) {
//     e.preventDefault(); // 通常のフォーム送信を防止
  
//     // FormDataオブジェクトを使用してフォームデータを取得
//     var formData = new FormData(this);
  
//     // input_categories配列が既に定義されていると仮定
//     var inputCategories = input_categories; // ここでinput_categoriesを取得
  
//     // input_categories配列の内容をJSON文字列として追加
//     formData.append('inputCategories', JSON.stringify(inputCategories));
  
//     // Ajaxを使用してPOSTリクエストを送信
//     var xhr = new XMLHttpRequest();
//     xhr.open("POST", this.action, true);
//     xhr.send(formData);
  
//     // POSTリクエストの送信後の処理
//     xhr.onload = function() {
//         if (xhr.status === 200) {
//           console.log("送信成功:", xhr.responseText);
//           window.location.reload(); // ページをリロード
//         } else {
//           console.log("送信失敗:", xhr.status);
//         }
//       }
//   });