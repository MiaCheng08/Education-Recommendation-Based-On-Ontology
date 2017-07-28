function loadMap(t,root){//传入的参数是options, node, line
    var l=t.width,i=t.height;

    var u=d3.layout.force()
     .on("tick",tick)
     .charge(function(d) { return d._children ? -d.size / 100*4 : -30*4; })
     .linkDistance(function(d) { return d.target._children ? 80*4 : 30*4; })
     .size([l,i])
     .alpha(.1);//获取或设置布局的冷却系数.(冷却系数为0时,节点间不再互相影响)

    var o=d3.select("#mapRow").append("svg").attr({id:"map",width:l,height:i});//选中id为mapRow的div，在此div里面加入svg标签，并将该svg标签的id设定为map，设置其宽和高
    var s=o.append("g");//在svg里面扩展g标签，这个标签是用来将多个形状组成为一组，这个标签用于svg标签中
    o.append("svg:defs").append("svg:marker").attr("id","arrow").attr("viewBox","0 -5 10 10").attr("refX",6).attr("markerWidth",5).attr("markerHeight",5).attr("orient","auto").append("svg:path").attr("d","M0,-5L10,0L0,5").attr("fill","#6ac6ff"),
    update();

    function update() {
        var nodes = flatten(root);
        var links = d3.layout.tree().links(nodes);
        //d3.layout.tree() 创建一个树布局实例，使用默认的设置 树布局与力学图是counterpart
        //.links(nodes)根据给定的结点数组 nodes，生成一组表示从父节点到子节点关系对象。
        //每个关系对象有两个属性：source - 父节点的引用 target - 子节点的引用
        u
         .nodes(nodes)
         .links(links)
         .start();

        //线
        s.selectAll("line.link").data(links, function(d) { return d.target.id; }).enter().append("line").attr("class","link");//n line是标签，link是类样式
        //s.selectAll("line.link").exit().remove();// Exit any old links.
        //线上的字
        var d=s.selectAll("link.desc").data(links, function(d) { return d.target.id; }).enter().append("text").attr("class","desc").text(function(t){return t.desc});//虽然class这些有关于样式的东西我动不了，但是它取数的东西我还是可以动的
        //s.selectAll("link.desc").exit().remove();// Exit any old links.

        //大圈小圈以及线，线上的文字的组合 是完整的节点
        var f=(
            u.drag().on("dragstart",function(t){t.fixed=!0}),
            s.selectAll("g.node")
             .data(nodes, function(d) { return d.id; })
            );
        var p=f.enter().append("g").attr("class",function(t,e){return 0===e?"node active":"node"}).call(u.drag).on("click",click);//.on("click",function(t){d3.event.defaultPrevented||window.open(t.href)});
        p.append("circle").attr({class:"ring"}).attr("r", function(d) { return d.children ? 14 : Math.sqrt(d.size)*8.5; });
        p.append("circle").attr({class:"outline"}).attr("r", function(d) { return d.children ? 12 : Math.sqrt(d.size)*8; }).style({fill:color,"stroke-width":"2px"});//这里设定的fill是根据c[t.index] c函数开头设的颜色组
        p.append("text").attr("class","nTxt").text(function(t){return t.name}).style({fill:"black","font-family":"SimSun"});

        //f.exit().remove();
    }

    function tick(){//上边是赋值，还没有拉回来
    s.selectAll("line.link")
      .attr("x1", function(d) { return d.source.x; })
      .attr("y1", function(d) { return d.source.y; })
      .attr("x2", function(d) { return d.target.x; })
      .attr("y2", function(d) { return d.target.y; });

    s.selectAll("g.node").selectAll("circle.ring")
      .attr("cx", function(d) { return d.x; })
      .attr("cy", function(d) { return d.y; });

    s.selectAll("g.node").selectAll("circle.outline")
      .attr("cx", function(d) { return d.x; })
      .attr("cy", function(d) { return d.y; });

    s.selectAll("g.node").selectAll("text.nTxt")
      .attr("x", function(d) { return d.x-15; })
      .attr("y", function(d) { return d.y+6; });
    }

    function click(d) {
        if (d.children) {
        d._children = d.children;
        d.children = null;
        } else {
        d.children = d._children;
        d._children = null;
        }
        update();
    }

    function color(d) {
    if(d.depth){
    var c=["#1f77b4","#ff7f0e","#2ca02c","#d62728","#9467bd","#8c564b","#e377c2","#7f7f7f","#bcbd22","#17becf"];
    return c[d.depth];
    }else{
    return d._children ? "#3182bd" : d.children ? "#c6dbef" : "#fd8d3c";
    }

    }

    function flatten(root) {
    var nodes = [], i = 0;

    function recurse(node) {//这里只是定义了函数，但是未被调用，在后面才被调用  reduce回调函数
    if (node.children) for (x in node.children){recurse(node.children[x]);};//迭代，具体不深究了，总之沿一条路下去找到了叶子结点，突然发现这里的输入进来的数据格式真是我sparqltree的输入格式
    //if (node.children) node.size = node.children.reduce(function(p, v) { return p + recurse(v); }, 0);
    //if(node.depth==2 && node.children){
        //node._children = node.children;
        //node.children = null;
    //}
    if (!node.id) node.id = ++i;
    nodes.push(node);//把node挤进nodes中 类似于append
    }

    recurse(root);//调用前面定义的函数，存入参数root，root才之前被赋予了JSON数据
    return nodes;
    }

}

