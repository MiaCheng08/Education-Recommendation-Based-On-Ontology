function loadMap(a){//传入的参数是options, node, line
    var c=["#1f77b4","#ff7f0e","#2ca02c","#d62728","#9467bd","#8c564b","#e377c2","#7f7f7f","#bcbd22","#17becf"];
    var datatip='<div class="tip" style="width: 250px; background-opacity:.5"><div class="header3">HEADER1</div><div class="header-rule"></div><div class="header3"> HEADER2 </div><div class="header-rule"></div><div class="header3"> HEADER3 </div></div>';
    if(a.length < 6){
        var l=718,i=300;
    }
    else if(a.length < 10){
        var l=718,i=450;
    }
    else if(a.length < 20){
        var l=718,i=1200;
    }
    else if(a.length < 30){
        var l=718,i=1400;
    }
    else if(a.length < 40){
        var l=718,i=1700;
    }
    else{
        var l=718,i=2000;
    }

    var o=d3.select("#mapRow")
            .append("svg")
            .attr({id:"map",width:l,height:i});//选中id为mapRow的div，在此div里面加入svg标签，并将该svg标签的id设定为map，设置其宽和高

    var s=o.append("g");//在svg里面扩展g标签，这个标签是用来将多个形状组成为一组，这个标签用于svg标签中
    //s.attr("class","path-scroll")
    var u=d3.layout.force();

    //o.append("svg:defs").append("svg:marker").attr("id","arrow").attr("viewBox","0 -5 10 10").attr("refX",6).attr("markerWidth",5).attr("markerHeight",5).attr("orient","auto").append("svg:path").attr("d","M0,-5L10,0L0,5").attr("fill","#6ac6ff");

    var p=s.selectAll("g.node")//大圈小圈以及线，线上的文字的组合 是完整的节点
           .data(a)
           .enter().append("g")
           .attr("class",function(t,e){return 0===e?"node active":"node"})
           .on("click",click);
    //下面四句是为结点添加元素，纯表现用
    p.append("circle")
     .attr({r:14,class:"ring"})
     .attr({
        cx:function(t){return t.x},
        cy:function(t){return t.y}
     });

    p.append("circle")
     .attr({r:10,class:"outline"})
     .style({fill:function(t){return c[t.index]},stroke:"#5CA8DB","stroke-width":"2px"})//这里设定的fill是根据c[t.index] c函数开头设的颜色组
     .attr({
        cx:function(t){return t.x},
        cy:function(t){return t.y}
     });

    p.append("text")
     .attr("class","propName")
     .text(function(t){return t.name})
     .style({fill:"black","font-family":"arial,helvetica,sans-serif"})
     .attr({
        x:function(t){return t.x+35},
        y:function(t){return t.y}
     });

    u.start();
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
/*
    s.selectAll("line.link")
     .data(n)//n line是标签，link是类样式
     .enter()
     .append("line")
     .attr("class","link")
     .attr({
            x1:function(t){return t.source.x},
            x2:function(t){return t.target.x},
            y1:function(t){return t.source.y},
            y2:function(t){return t.target.y}
     });

    var d=s.selectAll("link.desc")
           .data(n)
           .enter()
           .append("text")
           .attr("class","desc")
           .text(function(t){return t.desc})
           .attr({
                x:function(t){return(t.source.x+t.target.x)/2-25},
                y:function(t){return(t.source.y+t.target.y)/2+5},
           });
    //线上的字
*/

 /*  o.append("<p><font color=\"#9467bd\">100%</font></p>"+
     "<p><font color=\"#2ca02c\">60%</font></p>"+
     "<p><font color=\"#ff7f0e\">20%</font></p>"+
     "<p><font color=\"#d62728\">0%</font></p>"
     )

         var stand = o.append("g");

    stand.append("circle")
     .style({fill:c[3]})
     .attr({r:10,class:"ring"})
     .attr({
        cx:230,
        cy:20}
     );
    stand.append("text")
     .text("0%")
     .style({fill:"black","font-family":"SimSun"})
     .attr({
        x:220,
        y:45
     });
     stand.append("circle")
     .style({fill:c[1]})
     .attr({r:10,class:"ring"})
     .attr({
        cx:45,
        cy:20}
     );
    stand.append("text")
     .text("20%")
     .style({fill:"black","font-family":"SimSun"})
     .attr({
        x:40,
        y:35
     });
     stand.append("circle")
     .style({fill:c[2]})
     .attr({r:10,class:"ring"})
     .attr({
        cx:70,
        cy:20}
     );
     stand.append("text")
     .text("60%")
     .style({fill:"black","font-family":"SimSun"})
     .attr({
        x:65,
        y:35
     });
     stand.append("circle")
     .style({fill:c[4]})
     .attr({r:10,class:"ring"})
     .attr({
        cx:95,
        cy:20}
     );
     stand.append("text")
     .text("100%")
     .style({fill:"black","font-family":"arial,helvetica,sans-serif"})
     .attr({
        x:90,
        y:35
     });
*/