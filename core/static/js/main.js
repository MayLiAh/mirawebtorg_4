let green = function () {
    $('.header-radius').css('background-color', 'green')
    setTimeout(white, 9000)
}

let white = function () {
    $('.header-radius').css('background-color', 'white')
}

let red = function () {
    $('.header-radius').css('background-color', 'red')
    setTimeout(white, 9000)
}

function productAdded_basket_dialog_show(basket_dialog_response) {
    $(`body`).css("overflow", "hidden")
    $(`.dialog_window_background`).css("display", "block")
    $(`.product_added_into_basket_msg`).css('display', "block")
    if (basket_dialog_response === "product_added") {
        $('.message_product_added').css("display", "block") 
    }
    if (basket_dialog_response === "product_already_exists") {
        $('.message_product_already_added').css("display", "block")
    }
}

function productAdded_basket_dialog_hide() {
    $("body").css('overflow', '')
    $(".dialog_window_background").css("display", "")
    $('.product_added_into_basket_msg').css("display", "none")
    $(`.message_product_added`).css("display", "none")
    $(`.message_product_already_added`).css("display", "none")
}

$(`.button_stay_here`).on("click", () => productAdded_basket_dialog_hide())

function send_ajax(data, request_path) {
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    console.log(request_path)
    const csrftoken = getCookie('csrftoken');
    $.ajax({
        url: 'http://127.0.0.1:8000' + request_path,
        type: "POST",
        headers: {'X-CSRFToken': csrftoken},
        data: JSON.stringify(data),
        dataType: 'json',
        contentType: "application/json;charset=utf-8",
        statusCode: {
            500: function (response) {
                console.log('ОШИБКА СЕРВЕРА - код 500');
            }
        }
    })
        .done(function  (data) {
            if (data["basket_dialog_response"]) {
                productAdded_basket_dialog_show(data['basket_dialog_response'])
            }
            if (data["callback"] === "deletion_completed"){
                  
            }
        })
        .fail(function (data, jqXHR) {
            if (jqXHR.status === 500) {
                console.log(jqXHR.status + "Ошибка сервера")
            }
            if (jqXHR.status) {
                console.log(jqXHR.status)
            }
            if (jqXHR.status && jqXHR.status === 401) {
                console.log(jqXHR.status)
            }
        })
    return done()
}
