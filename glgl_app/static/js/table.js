$(document).ready(function() {
    var table = $('#datatables').DataTable({
        "autoWidth": false,
        "paging": true,
        //"dom": 'T<"clear"><"toolbar">Clfrtip',
        "dom": 'iCflrtp',
        "iDisplayLength": 100,
        "lengthMenu": [[100, 500, 1000, -1], [100, 500, 1000, "所有"]],
        "stateSave": false,
        "processing": true,
        "ajax": {//即后端传来的数据，如果按照上述传来的数据格式的话，则下面的url就是后端指定的url:
            'url': "/history",
        },
        "order": [
                [0, "asc"],
                [1, "asc"],
                [2, "desc"],
            ],
        "columnDefs": [
              {width: '25%', targets: 3},
            ],
        "columns": [{//指定了传过来的数据的字段
            "data": "date",
        }, {
            "data": "knowledge",
        }, {
            "data": "title",
        }, {
            "data": "change",
            //"visible":falsevisible字段默认是true，如果设置false的话，显示的时候是隐藏的，当然也可以通过空间取消其隐藏。
        }, {
            "data": "score",
        }],
        "sPaginationType": "full_numbers",
        "oLanguage": {
            "sProcessing": "<img src='/images/datatable_loading.gif'>  努力加载数据中.",
            "sLengthMenu": "每页显示 _MENU_ 条记录",
            "sZeroRecords": "抱歉， 没有找到",
            "sInfo": "从 _START_ 到 _END_ /共 _TOTAL_ 条数据",
            "sInfoEmpty": "没有数据",
            "sInfoFiltered": "(从 _MAX_ 条数据中检索)",
            "sZeroRecords": "没有检索到数据",
            "sSearch": "模糊查询:  ",
            "oPaginate": {
                "sFirst": "首页",
                "sPrevious": "前一页",
                "sNext": "后一页",
                "sLast": "尾页"
            }
        }
    });
);