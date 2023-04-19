// $(document).ready(function() {
//   $("#my-form").submit(function(event) {
//     event.preventDefault();  // フォームの自動送信を防止

//     $.ajax({
//       type: "POST",
//       url: "{% url 'my-url' %}",  // サブミット先のURLを指定
//       data: $("#my-form").serialize(),  // フォームのデータをシリアライズ
//       success: function(response) {
//         // 成功時の処理
//         alert("Success!");
//       },
//       error: function(response) {
//         // エラー時の処理
//         var errors = response.responseJSON;
//         $.each(errors, function(key, value) {
//           $("#id_" + key).addClass("is-invalid");
//           $("#"+key+"-errors").html(value.join("<br>"));
//         });
//       }
//     });
//   });
// });