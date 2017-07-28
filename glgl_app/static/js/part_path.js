function loadMap(t,a,n){//传入的参数是options, node, line
    var c=["#1f77b4","#ff7f0e","#2ca02c","#d62728","#9467bd","#8c564b","#e377c2","#7f7f7f","#bcbd22","#17becf"];
    var l=t.width,i=t.height;

    var o=d3.select("#mapRow").append("svg").attr({id:"map",width:l,height:i});//选中id为mapRow的div，在此div里面加入svg标签，并将该svg标签的id设定为map，设置其宽和高
    var s=o.append("g");//在svg里面扩展g标签，这个标签是用来将多个形状组成为一组，这个标签用于svg标签中

    var u=d3.layout.force()
     .on(//当置为tick时，触发执行里面的匿名函数？
        "tick",
        function(){
            s.selectAll("line.link").each(
                function(t){
                    var e,r,a,n,c=d3.select(this);
                    if("NEXT"==t.type){
                        var l=t.target.x-t.source.x;
                        var i=t.target.y-t.source.y;
                        var o=Math.sqrt(l*l+i*i);
                        var s=l/o,u=i/o,d=35,f=35;
                        e=t.source.x+d*s;
                        r=t.target.x-f*s;
                        a=t.source.y+d*u;
                        n=t.target.y-f*u;
                        c.attr("marker-end","url(#arrow)")
                    }
                    else
                        e=t.source.x,a=t.source.y,r=t.target.x,n=t.target.y;
                    c.attr("x1",e);
                    c.attr("x2",r);
                    c.attr("y1",a);
                    c.attr("y2",n)
                }
            );
            s.selectAll("g.node").selectAll("circle.ring").attr({
                cx:function(t){return t.x},
                cy:function(t){return t.y}
            });
            s.selectAll("g.node").selectAll("circle.outline").attr({
                cx:function(t){return t.x},
                cy:function(t){return t.y}
            });
            s.selectAll("g.node").selectAll("text.propName").attr({
                x:function(t){return t.x+35},
                y:function(t){return t.y}
            });
            d.attr({//d=s.selectAll("link.desc")
                x:function(t){return(t.source.x+t.target.x)/2-25},
                y:function(t){return(t.source.y+t.target.y)/2+5},
                transform:function(t){
                    var e=t.target.x-t.source.x,r=t.target.y-t.source.y,a=360*Math.atan(r/e)/(2*Math.PI),n=(t.target.x+t.source.x)/2,c=(t.target.y+t.source.y)/2;return"rotate("+a+","+n+","+c+")"
                }
            })
        }
    )
     //.charge(-1200)
     //.linkDistance(200)
     .nodes(a)
     .links(n)
     .size([l,i])
     .alpha(-1);//获取或设置布局的冷却系数.(冷却系数为0时,节点间不再互相影响)

    o.append("svg:defs").append("svg:marker").attr("id","arrow").attr("viewBox","0 -5 10 10").attr("refX",6).attr("markerWidth",5).attr("markerHeight",5).attr("orient","auto").append("svg:path").attr("d","M0,-5L10,0L0,5").attr("fill","#6ac6ff"),

    s.selectAll("line.link").data(n).enter().append("line").attr("class","link");//n line是标签，link是类样式
    var d=s.selectAll("link.desc").data(n).enter().append("text").attr("class","desc").text(function(t){return t.desc});//虽然class这些有关于样式的东西我动不了，但是它取数的东西我还是可以动的
    //线上的字
    var f=(//大圈小圈以及线，线上的文字的组合 是完整的节点
        u.drag().on("dragstart",function(t){t.fixed=!0}),
        s.selectAll("g.node").data(a)
        );//a
    var p=f.enter().append("g")
           .attr("class",function(t,e){return 0===e?"node active":"node"})
           //.call(u.drag)
           .on("click",click);
    //下面四句是为结点添加元素，纯表现用
    p.append("circle").attr({r:29,class:"ring"});
    p.append("circle").attr({r:25,class:"outline"}).style({fill:function(t){return c[t.index]},stroke:"#5CA8DB","stroke-width":"2px"});//这里设定的fill是根据c[t.index] c函数开头设的颜色组
    p.append("text").attr("class","nTxt").text(function(t){return t.nTxt}).style({fill:"black"});
    p.append("text").attr("class","propName").text(function(t){return t.name}).style({fill:"black","font-family":"SimSun"});

    u.start();
    for(var x=0;x<50;x++)
        u.tick();
    var g=setInterval(
        function(){u.alpha()<.01?clearInterval(g):u.tick()},
        80
    )
}

//这里要该的能传数组给服务器 用隐藏的form
function click(t){
    if(t.need)
    {
        document.getElementById("videos").value = t.videos;
        document.getElementById("knowledge_name").value = t.name;
        document.getElementById("video_form").submit();
    }
}