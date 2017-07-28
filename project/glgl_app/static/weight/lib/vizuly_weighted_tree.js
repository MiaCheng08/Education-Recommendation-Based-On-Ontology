/*! vizuly 06-04-2016 */
vizuly.viz.weighted_tree=function(a){
    function b(){
        l.selection.attr("class","vz-weighted_tree-viz"),
        v=l.selection.append("svg")
           .attr("id",l.id)
           .style("overflow","visible")
           .attr("class","vizuly vz-weighted_tree-viz"),
        C=vizuly.util.getDefs(n),
        x=v.append("rect").attr("class","vz-background"),
        w=v.append("g").attr("class","vz-weighted_tree-viz"),
        y=w.append("g")
           .attr("class","vz-weighted_tree-plot")
           .attr("clip-path","url(#"+l.id+"_plotClipPath)"),
        z=y.append("rect").attr("class","vz-plot-background"),
        A=y.append("g").attr("class","vz-weighted_tree-link-plot"),
        B=y.append("g").attr("class","vz-weighted_tree-node-plot"),
        l.dispatch.initialize()
    }

    function c(){
        function a(b){
            b.children&&(
                b._children=b.children,
                b._children.forEach(a),
                b.children=null
            )
        }
        n.validate(),
        q=vizuly.util.size(l.margin,l.width,l.height),
        D.size([q.height,q.width]),
        (1==o||p)&&(d(),1==o&&r.children.forEach(a),o=!1,p=!1);
        var b;
        -1==l.branchPadding?(
            b=Math.min(q.height,q.width)/l.children(l.data).length,
            console.log("scale = "+b)
            ):
            b=Math.min(q.height,q.width)*l.branchPadding,
        E.range([1.5,b/2]),
        D.nodeSize([b,0]),
        t=l.fixedSpan>0?l.fixedSpan:q.width/(u+1);
        for(var c=1;u+1>c;c++){
            var e=s.filter(function(a){return a.depth==c});
            F[c]=d3.max(e,function(a){return l.value(a)}),
            G[c]=d3.min(e,function(a){return l.value(a)})
        }
        l.dispatch.measure()
        }

    function d(){
        function a(b){
            l.children(b)&&(
                b._children||(
                    b.children=l.children(b),
                    b.children.forEach(function(c){c.x0=b.x,c.y0=b.y,a(c)})
                )
            )
        }
        u=0,
        a(l.data),
        r=l.data,
        r.x0=0,
        r.y0=0,
        s=D.nodes(r).reverse(),
        s.forEach(function(a){
            0!=a.depth&&(
                F[a.depth]||(F[a.depth]=-(1/0),G[a.depth]=1/0),
                u=Math.max(u,a.depth)
            )
        }
        ),
        l.dispatch.data_prepped()
    }

    function e(){o=!0}

    function f(a){
    c(),
    v.attr("width",l.width).attr("height",l.height),
    x.attr("width",l.width).attr("height",l.height),
    y.style("width",q.width).style("height",q.height).attr("transform","translate("+q.left+","+(q.top+q.height/2)+")"),
    g(r)}

    function g(a){
    var b=D(r).reverse(),c=D.links(b);
    h(a,b);
    var d=B.selectAll(".vz-weighted_tree-node").data(b,function(a){return a.vz_tree_id||(a.vz_tree_id=l.key(a))}),

    e=d.enter().append("g")
       .attr("class",function(a){return"vz-weighted_tree-node vz-id-"+a.vz_tree_id})
       .attr("transform",function(b){var c=b.y0?b.y0:a.y0,d=b.x0?b.x0:a.x0;return"translate("+c+","+d+")"})
       .on("click",function(a,b){l.dispatch.click(this,a,b)})
       .on("dblclick",function(a,b){l.dispatch.dblclick(this,a,b)})
       .on("mouseover",function(a,b){l.dispatch.mouseover(this,a,b)})
       .on("mouseout",function(a,b){l.dispatch.mouseout(this,a,b)});

    e.append("circle")
       .attr("class",".vz-weighted_tree-node-circle")
       .attr("r",(1e-6)*10)
       .style("cursor","pointer"),
    e.append("text")
       .attr("x",function(a){return a.children||a._children?-10:10})
       .attr("dy",".35em")
       .attr("text-anchor",function(a){return a.children||a._children?"end":"start"})
       .style("pointer-events","none")
       .text(function(a){return l.label(a)});

    var f=A.selectAll(".vz-weighted_tree-link").data(c,function(a){return a.target.vz_tree_id});

    f.enter().append("path").attr("class",function(a){return"vz-weighted_tree-link vz-id-"+a.target.vz_tree_id})
     .attr("d",function(b){
                var c=b.target.y0?b.target.y0:a.y0,
                    d=b.target.x0?b.target.x0:a.x0,
                    e={x:d,y:c};
                return H({source:e,target:e})
                }
           )
     .on("mouseover",function(a,b){l.dispatch.mouseover(this,a,b)})
     .on("mouseout",function(a,b){l.dispatch.mouseout(this,a,b)})
     .style("stroke-linecap","round"),

     l.dispatch.update();

     var g=d.transition();
     i(g,function(){l.dispatch.node_refresh()}),
     g.duration(l.duration).attr("transform",function(a){return"translate("+a.y+","+a.x+")"}),
     g.select("circle").attr("r",function(a){return I(a)});

     var j=d.exit().transition().duration(l.duration)
            .attr("transform",function(b){return b.x0=null,b.y0=null,"translate("+a.y+","+a.x+")"})
            .remove();
     j.select("circle").attr("r",1e-6),
     j.select("text"),

     f.transition().duration(l.duration).attr("d",H)
      .style("stroke-width",function(a){return 2*I(a.target)}),

     f.exit().transition().duration(l.duration)
      .attr("d",function(b){var c={x:a.x,y:a.y};return H({source:c,target:c})})
      .remove(),
     b.forEach(function(a){a.x0=a.x,a.y0=a.y})
    }

    function h(a,b){
        var c=d3.min(b,function(a){return a.x}),
        d=d3.max(b,function(a){return a.x}),
        e=d3.max(b,function(a){return a.depth})*t,
        f=Math.max(l.height,d-c+q.top),
        g=Math.max(l.width,e+.2*l.width+q.left);

        q.height/2+d>f&&(f=q.height/2+d+D.nodeSize()[0]),
        v.transition().duration(l.duration).style("height",f+"px").style("width",g+"px");

        var h=Math.max(0,-c-q.height/2)+D.nodeSize()[0]/2;
        b.forEach(function(a){a.y=a.depth*t,a.x=a.x+h-D.nodeSize()[0]}),
        j(a.x)
    }

    function i(a,b){
        var c=0;
        a.each(function(){++c}).each("end",function(){--c||b.apply(this,arguments)})
    }

    function j(a){
        function b(a){
            return function(){
                var b=d3.interpolateNumber(this.scrollTop,a);
                return function(a){
                    this.scrollTop=b(a)
                }
            }
        }
        l.selection.transition().duration(l.duration).tween("scrolltween",b(a))
    }

    function k(a){
        a.children?(a._children=a.children,a.children=null):(a.children=a._children,a._children=null),
        g(a)
    }

    var l={},
    m={
        data:null,
        margin:{top:"5%",bottom:"5%",left:"8%",right:"7%"},
        key:null,
        tree:d3.layout.tree(),
        children:null,
        duration:500,
        width:300,
        height:300,
        value:null,
        branchPadding:-1,
        fixedSpan:-1,
        label:function(a,b){
            return a
        }
    },
    n=vizuly.component.create(a,l,m,["node_refresh","data_prepped"]);

    n.type="viz.chart.weighted_tree";
    var o=!0,p=!1;
    n.on("data_change.internal",e);
    var q,r,s,t,u,v,w,x,y,z,A,B,C,
    D=l.tree,
    E=d3.scale.sqrt(),
    F={},G={},
    H=d3.svg.diagonal().projection(function(a){return[a.y,a.x]}),
    I=function(a){
        return 0==a.depth?E.range()[1]/2:(
            E.domain([G[a.depth],F[a.depth]]),
            E(l.value(a))
        )
    };

    return b(),

    n.update=function(a){
        return 1==a&&(p=!0),f(),n
    },

    n.toggleNode=function(a){k(a)},
    n
};