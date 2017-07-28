function MindMap(){
    function t(){
        r(),a([0,0]),e()
        }
    function e(){//设置左上角的按钮
        var t=u.select(".gbutton");
        t.empty()&&(t=u.append("g").attr("class","gbutton"));
        t.attr("transform","translate(20,40)");
        var e=u.select(".gstatus");
        e.empty()&&(e=u.append("g").attr("class","gstatus"));
        e.attr("transform","translate(35,88)");
        e.append("text").attr("fill","black").attr("font-size",12).text("Successful !").style("fill-opacity",0);
        t.append("rect").attr("x",0).attr("y",0).attr("width",112).attr("height",28).attr("rx",5).attr("ry",5).attr("fill","purple").attr("stroke","black").attr("stroke-width",.5);
        t.append("text").attr("dx",112*.1).attr("dy",28*.68).attr("fill","white").attr("font-size",12).text("Save on Server"),
        t.on("mouseover",function(){
                t.select("rect").attr("fill","yellow");
                t.select("text").attr("fill","purple");
                t.style("cursor","pointer")
                }
            )
         .on("mouseout",function(){
                t.select("rect").attr("fill","purple");
                t.select("text").attr("fill","white")
                }
            )
         .on("mousedown",function(){
                $.post(
                    "http://210.140.42.149:3000/save",
                    p,
                    function(t,r){
                        "success"==r?e.select("text").text("Successful !").style("fill-opacity",1).transition().duration(1e3).style("fill-opacity",0):e.select("text").text("Failed !").style("fill-opacity",1).transition().duration(1e3).style("fill-opacity",0)
                    }
                    )
                }
           )
         }
    function r(){
        x=d3.tree().size([360,120]).separation(
            function(t,e){
                return(t.parent==e.parent?1:2)/t.depth
                }
            ),
        g=d3.hierarchy(p),
        g.descendants().forEach(
            function(t,e){
                t.data.closed="true"==t.data.closed,
                t.data.closed&&i(t)
                }
            ),
        m=u.select(".gmind"),m.empty()&&(m=u.append("g").attr("class","gmind")),
        v=m.select(".glink"),v.empty()&&(v=m.append("g").attr("class","glink")),
        k=m.select(".gnode"),k.empty()&&(k=m.append("g").attr("class","gnode")),
        v.attr("transform","translate("+d/2+","+f/2+")"),
        k.attr("transform","translate("+d/2+","+f/2+")");
        var t=d3.zoom().scaleExtent([.7,2]).translateExtent([[-.7*d,-.7*f],[1.7*d,1.7*f]]).on(
            "zoom",
            function(){
                var t="scale("+d3.event.transform.k+")",
                e="translate("+d3.event.transform.x+","+d3.event.transform.y+")";
                m.attr("transform",e+t)
            }
        );
        u.call(t)
        }

    function n(t,e){
        var r=(t-90)/180*Math.PI,
        n=e;
        return[n*Math.cos(r),n*Math.sin(r)]
        }
    function a(t){
        x(g),
        y=g.descendants(),
        h=g.links(),
        y.forEach(
            function(t){
                t.y=120*t.depth,
                t.pos=n(t.x,t.y)
            }
        );
        for(var e=0;e<y.length;e++)
            y[e].id||(y[e].id=b,b++);
        for(var e=0;e<h.length;e++)
            h[e].id||(h[e].id=M,M++);
        var r=d3.scaleLinear().domain([0,180,360]).range([1,.3,1]),
        o=d3.scaleLinear().domain([0,1,5,10]).range([13,13,6.5,6.5]),
        c=k.selectAll(".node").data(y,function(t){return t.id}),
        u=c.enter(),d=c.exit(),
        f=u.append("g").attr("class","node").attr("transform",function(e){return"translate("+t[0]+","+t[1]+")"}).on(
            "mousedown",
            function(t){//收缩事件
                d3.event.defaultPrevented||(i(t),a(t.prevPos))
                }
            ).on(
            "mouseover",
            function(t){
                d3.select(this).style("cursor","pointer").select("text").style("fill-opacity",1)
                }
            ).on(
            "mouseout",
            function(t){
                d3.select(this).select("text").transition(600).style("fill-opacity",0)
                }
            );
        f.append("circle").attr("r",0).style(
            "fill",
            function(t){
                var e="";
                return t.depth>1?(e=d3.hsl(t.parent.color),e=e.brighter(.5),e.l=r(t.x)):e=t.depth>0?d3.hsl(t.x,1,.5):"#FFFFFF",t.color=e+"",t.color+""}).style("stroke-width",2).style("stroke","black").style("opacity",0),f.append("text").attr("dominant-baseline","text-before-edge").attr("text-anchor","middle").attr("font-size",12).attr("dy",13).text(function(t){var e=d3.rgb(t.color);return l(e.r,e.g,e.b)}).style("fill-opacity",0);var p=f.merge(c).transition().duration(600).attr("transform",function(t){return"translate("+t.pos[0]+","+t.pos[1]+")"});p.select("circle").attr("r",function(t){return o(t.depth)}).style("opacity",1),p.select("text").attr("dy",function(t){return o(t.depth)}).style("fill-opacity",0);var m=d.transition().duration(600).attr("transform",function(e){return"translate("+t[0]+","+t[1]+")"}).remove();m.select("circle").style("opacity",0).attr("r",0),m.select("text").style("fill-opacity",0);var w=v.selectAll(".link").data(h,function(t){return t.target.id}),F=w.enter(),z=w.exit();F.append("path").attr("class","link").attr("fill","none").attr("stroke","rgba(20,20,20,0.2)").attr("stroke-width",1).attr("opacity",0).attr("d",function(e){var r={x:t[0],y:t[1]};return s({source:r,target:r})}).merge(w).transition().duration(600).attr("opacity",1).attr("d",function(t){var e={x:t.source.pos[0],y:t.source.pos[1]},r={x:t.target.pos[0],y:t.target.pos[1]};return"M"+e.x+","+e.y+"L"+r.x+","+r.y}),z.transition().duration(600).attr("opacity",0).attr("d",function(e){var r={x:t[0],y:t[1]},n={x:t[0],y:t[1]};return"M"+r.x+","+r.y+"L"+n.x+","+n.y}).remove(),y.forEach(function(t){t.prevPos=[t.pos[0],t.pos[1]]})}function o(){}function s(t){return"M"+t.source.x+","+t.source.y+"C"+(t.source.x+t.target.x)/2+","+t.source.y+" "+(t.source.x+t.target.x)/2+","+t.target.y+" "+t.target.x+","+t.target.y}function i(t){t.children?(t._children=t.children,t.children=null,t.data.closed=!0):(t.children=t._children,t._children=null,t.data.closed=!1)}function l(t,e,r){return c(t)+c(e)+c(r)}function c(t){return t=parseInt(t,10),isNaN(t)?"00":(t=Math.max(0,Math.min(t,255)),"0123456789ABCDEF".charAt((t-t%16)/16)+"0123456789ABCDEF".charAt(t%16))}var u,d,f,p,y,h,x,g,m,v,k,b=0,M=0;this.svg=function(t){if(arguments.length<1)return u;u=t},this.data=function(t){if(arguments.length<1)return p;p=t},this.size=function(t,e){if(arguments.length<2)return[d,f];d=t,f=e},this.getRoot=function(){return g},this.render=t,this.update=o}