/*
*project: calendar Widgets
*version: 1.0
*create: 2013-5-28
*update: 2013-5-28 9:00
*author: F2E xiechengxiong
*/
(function(win, doc) {
    var days = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
    Date.prototype.getNewDate = function(y, m, d) {
        !isNaN(y) && this.setFullYear(y);
        !isNaN(m) && this.setMonth(m);
        !isNaN(d) && this.setDate(d);
        return this;
    };
    Date.prototype.getDayCount = function(){
        if(X.isLeapYear(this.getFullYear())) {
            days[1] = 29;
        }
        return days[this.getMonth()];
    };
    Date.prototype.getPrevNextMonth = function(poor){
        var y = this.getFullYear();
        var m = this.getMonth() + poor;
        if(m < 0) {
            y -= 1;
            m = 11;
        } else if(m > 11) {
            y += 1;
            m = 0;
        }
        return new Date().getNewDate(y, m, 1);
    };
    var Calendar = function(obj, opts) {
        this.obj = obj;
        X.addClass(this.obj, ‘xcx-calendar-obj’);
        this.opts = opts;
        this.date = new Date().getNewDate();
        this.curDate = new Date().getNewDate();
        this.prevDate = this.date.getPrevNextMonth(-1);
        this.wrap = this.createWrap();
        this.yearMonthObj = X.getByClass(‘yearMonth’, this.wrap)[0];
        this.daysObj = X.getByClass(‘xcx-calendar-days’, this.wrap)[0];
        this.bindEvent.call(this);
    };
    Calendar.prototype = {
        bindEvent: function() {
        var _this = this;
        X.addEvent(this.wrap, ‘click’, function(e) {
        X.stopPropagation(e);
        var target = e.target || win.event.srcElement;
        switch(target.className) {
        case ‘xcx-calendar-day':
        case ‘xcx-calendar-day focus': _this.daysClickHandler(target.title); break;
        case ‘nextMonth': _this.changeMonth(1); break;
        case ‘preMonth': _this.changeMonth(-1); break;
        default: break;
        }
        });
        if(this.obj.tagName === ‘INPUT’) {
        X.addEvent(this.obj, ‘click’, function(e) {
        X.stopPropagation(e);
        _this.show();
        });
        X.addEvent(doc, ‘click’, function(e) {
        _this.hide();
        });
        }
        },
        daysClickHandler: function(d) {
        if(this.obj.tagName === ‘INPUT’) {
        this.obj.value = d;
        this.hide();
        } else {
        alert(d);
        }
        },
        show: function() {
        var off = X.getOffset(this.obj);
        this.wrap.style.left = off[0] +’px';
        this.wrap.style.top = off[1] + this.obj.offsetHeight +’px';
        this.wrap.style.display = ”;
        },
        hide: function() {
        this.wrap.style.display = ‘none';
        },
        createWrap: function() {
            var wrap = doc.createElement(‘div’);
            wrap.className = ‘xcx-calendar-wrap';
            wrap.innerHTML = this.createTitle() + this.createContent();
            if(this.obj.tagName === ‘INPUT’) {
            wrap.style.position = ‘absolute';
            wrap.style.display = ‘none';
            doc.body.appendChild(wrap);
            } else {
            this.obj.appendChild(wrap);
            }
            return wrap;
        },
        changeMonth: function(poor) {
            this.date = this.date.getPrevNextMonth(poor);
            this.prevDate = this.date.getPrevNextMonth(-1);
            this.yearMonthObj.innerHTML = this.date.getFullYear() +’年’+ (this.date.getMonth() + 1) +’月';
            this.daysObj.innerHTML = this.createDate();
        },
        createTitle: function() {
            var preMonth = ‘<a class=”preMonth” href=”javascript:void(0);” title=”上一月”></a>';
            var yearMonth = ‘<span class=”yearMonth”>’+ this.date.getFullYear() +’年’+ (this.date.getMonth() + 1) +’月</span>';
            var nextMonth = ‘<a class=”nextMonth” href=”javascript:void(0);” title=”下一月”></a>';
            return ‘<div class=”xcx-calendar-title”>’+ preMonth + yearMonth + nextMonth +'</div>';
        },
        createContent: function() {
            var weeks = ‘<div class=”xcx-calendar-weeks”><span>日</span><span>一</span><span>二</span><span>三</span><span>四</span><span>五</span><span>六</span></div>';
            var days = ‘<div class=”xcx-calendar-days”>’+ this.createDate() +'</div>';
            return ‘<div class=”xcx-calendar-content”>’ + weeks + days +'</div>';
        },
        createDate: function() {
            var date = ”;
            var cd = this.curDate;
            var td = this.date;
            var d = td.getFullYear() +’年’+ (td.getMonth() + 1) +’月';
            var cc = td.getDayCount();
            var pc = this.prevDate.getDayCount();
            var fw = new Date(td.getFullYear(), td.getMonth(), 1).getDay();
            for(var i = pc – fw; i < pc; i++) {
                date += ‘<a class=”disable prevDay” data-index=”p’+ i +'” title=”‘+ d + i +’日”>’+ i +'</a>';
            }
            for(var j = 1; j <= cc; j++) {
                var cls = ”;
                if(j === cd.getDate() && td.getMonth() === cd.getMonth() && td.getFullYear() === cd.getFullYear()) {
                    cls = ‘xcx-calendar-day focus';
                } else {
                    cls = ‘xcx-calendar-day';
                }
                date += ‘<a class=”‘+ cls +'” data-index=”‘+ j +'” title=”‘+ d + j +’日”>’+ j +'</a>';
            }
            for(var k = 1; k <= 42 – fw – cc; k++) {
                date += ‘<a class=”disable nextDay” data-index=”n’+ k +'” title=”‘+ d + k +’日”>’+ k +'</a>';
            }
            return date;
        }
    };
    win.Calendar = Calendar;
})(window, document);