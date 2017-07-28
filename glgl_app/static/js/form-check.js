function show_error(msg) {
    var error = document.createElement('div');//为error创建一个区域
    error.setAttribute('class', 'alert alert-danger alert-dismissible');
    //所添加的'alert alert-danger alert-dismissible'是模板中使用的类class，这两个''连起来用，字典类似：
    //class = 'alert alert-danger alert-dismissible'
    error.setAttribute('role', 'alert');//同理role="alert"
    //通过上面两次添加属性，从而定位到了模板中的div
        error.innerHTML = "<button type='button' class='close' data-dismiss='alert' aria-label='Close'><span \
                    aria-hidden='true'>&times;</span></button> \
                    <strong>Error!</strong>" + msg + "</div>";
    //知道后改变标签里面的所有内容，通过重写
    /*原来长这样：
                        <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                        <span aria-hidden="true">
                            &times;
                        </span>
                    </button>
                    <strong>Error!</strong> {{ error }}<!--strong是加粗-->
    */
    document.getElementById('show-error').innerHTML = "";//在模板中找id=show-error的标签元素
    //这个元素一开始是这样的：<div id="show-error"></div>，先加个""
    document.getElementById('show-error').appendChild(error);
    //将刚刚代码编写设计的元素加入查询到的元素中，神奇
}

function validate_required(field, alerttxt) {
    with (field) {//with (field)相当于field.  这样就可以直接使用value，而不是field.value
        if (value == null || value == "") {
            show_error(alerttxt);
            return false
        }
        else {
            return true
        }
    }
}

function check_password(field) {//这个是在哪里被用了/
    with (field) {
        if (value == null || value == "") {
            show_error("请填写密码");
            return false;
        }
        else if (value.length < 6) {
            show_error("密码长度太短");
            return false;
        }
        return true;
    }
}
