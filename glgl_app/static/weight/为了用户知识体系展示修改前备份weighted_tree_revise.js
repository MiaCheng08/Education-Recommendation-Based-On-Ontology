//**************************************************************************************************************
//
//  This is a test/example file that shows you one way you could use a vizuly object.
//  We have tried to make these examples easy enough to follow, while still using some more advanced
//  techniques.  Vizuly does not rely on any libraries other than D3.  These examples do use jQuery and
//  materialize.css to simplify the examples and provide a decent UI framework.
//
//**************************************************************************************************************

// html element that holds the chart
var viz_container;

// our weighted tree
var viz;

// our theme
var theme;

// nested data
var data = {};

var valueField = "weight";//size也可以
var valueFields = [ "weight","demand"];


function loadData() {

    $.get('/showtree/', function(root) {//d3.json这个函数在d3.js里面

        data = flatten(root);
        initialize();

    });

}

// Returns a list of all nodes under the root.
function flatten(root) {
    var i = 0;

    function recurse(node) {//这里只是定义了函数，但是未被调用，在后面才被调用  reduce回调函数
    if (node.children) for (x in node.children){recurse(node.children[x]);};

    if (!node.id) node.id = ++i;

    }

    recurse(root);//调用前面定义的函数，存入参数root，root才之前被赋予了JSON数据
    return root;
}

function prepData(json) {

    var nest=json;

    //This will be a viz.data function;
    vizuly.data.aggregateNest(nest.values, valueField, function (a, b) {
        return Number(a) + Number(b);
    });

    //Remove empty child nodes left at end of aggregation and add unqiue ids
    function removeEmptyNodes(node,parentId,childId) {
        if (!node) return;
        node.id=parentId + "_" + childId;
        if (node.values) {
            for(var i = node.values.length - 1; i >= 0; i--) {
                node.id=parentId + "_" + i;
                removeEmptyNodes(node.values[i],node.id,i)
            }
        }
    }

    removeEmptyNodes(nest,"0","0");

    return nest;
}

function initialize() {

    viz = vizuly.viz.weighted_tree(document.getElementById("viz_container"));

    //Here we create three vizuly themes for each radial progress component.
    //A theme manages the look and feel of the component output.  You can only have
    //one component active per theme, so we bind each theme to the corresponding component.
    theme = vizuly.theme.weighted_tree(viz).skin(vizuly.skin.WEIGHTED_TREE_AXIIS);

    //Like D3 and jQuery, vizuly uses a function chaining syntax to set component properties
    //Here we set some bases line properties for all three components.
    viz.data(data)                                                      // Expects hierarchical array of objects.
        .width(600)                                                     // Width of component
        .height(600)                                                    // Height of component
        .children(function (d) { return d.children })                     // Denotes the property that holds child object array
        .key(function (d) { return d.id })                              // Unique key
        .value(function (d) {
            return Number(d[valueField])})                    // The property of the datum that will be used for the branch and node size
        .fixedSpan(-1)                                                  // fixedSpan > 0 will use this pixel value for horizontal spread versus auto size based on viz width
        .label(function (d) {                                           // returns label for each node.
            return trimLabel(d.key)})
        .on("measure",onMeasure)                                        // Make any measurement changes
        .on("mouseover",onMouseOver)                                    // mouseover callback - all viz components issue these events
        .on("mouseout",onMouseOut)                                      // mouseout callback - all viz components issue these events
        .on("click",onClick)                                           // mouseout callback - all viz components issue these events
        .on("dblclick",click);


    //We use this function to size the components based on the selected value from the RadiaLProgressTest.html page.
    changeSize("1000,1000");

    // Open up some of the tree branches.这里可以自定义页面舒刷新后的初始展示情况
    viz.toggleNode();//这样只展开第一级节点，也就是默认情况
    //viz.toggleNode(data.children[1]);//再展开第一级结点的基础上，将展开第一级节点的第二个节点的全部子节点
    //viz.toggleNode(data.children[2]);


}


function trimLabel(label) {
   return (String(label).length > 15) ? String(label).substr(0, 12) + "..." : label;
}


var datatip='<div class="tip" style="width: 250px; background-opacity:.5">' +
    '<div class="header1"> HEADER1 </div>' +
    '<div class="header-rule"></div>' +
    '<div class="header2"> HEADER2 </div>' +
    '<div class="header-rule"></div>' +
    '<div class="header3"> HEADER3 </div>' +
    '</div>';


// This function uses the above html template to replace values and then creates a new <div> that it appends to the
// document.body.  This is just one way you could implement a data tip.
function createDataTip(x,y,h1,h2,h3) {

    var html = datatip.replace("HEADER1", h1);
    html = html.replace("HEADER2", h2);
    html = html.replace("HEADER3", h3);

    d3.select("body")
        .append("div")
        .attr("class", "vz-weighted_tree-tip")
        .style("position", "absolute")
        .style("top", y + "px")
        .style("left", (x - 125) + "px")
        .style("opacity",0)
        .html(html)
        .transition().style("opacity",1);

}

function onMeasure() {
   // Allows you to manually override vertical spacing
   //viz.tree().nodeSize([100,0]);
}

function onMouseOver(e,d,i) {
    if (d == data) return;
    var rect = e.getBoundingClientRect();
    if (d.target) d = d.target; //This if for link elements
    createDataTip(rect.left, rect.top, d.key, "大纲要求", (d["demand"]));

}

function onMouseOut(e,d,i) {
    d3.selectAll(".vz-weighted_tree-tip").remove();
}



//We can capture click events and respond to them
function onClick(g,d,i) {
    viz.toggleNode(d);
}

function click(d) {
    d3.event.defaultPrevented||window.open("category/1");
}

//This function is called when the user selects a different skin.
function changeSkin(val) {
    if (val == "None") {
        theme.release();
    }
    else {
        theme.viz(viz);
        theme.skin(val);
    }

    viz().update();  //We could use theme.apply() here, but we want to trigger the tween.
}

//This changes the size of the component by adjusting the radius and width/height;
function changeSize(val) {
    var s = String(val).split(",");
    viz_container.transition().duration(300).style('width', s[0] + 'px').style('height', s[1] + 'px');
    viz.width(s[0]).height(s[1]*.8).update();
}

//**************************************************************************************************************
//
//  This is a test/example file that shows you one way you could use a vizuly object.
//  We have tried to make these examples easy enough to follow, while still using some more advanced
//  techniques.  Vizuly does not rely on any libraries other than D3.  These examples do use jQuery and
//  materialize.css to simplify the examples and provide a decent UI framework.
//
//**************************************************************************************************************

// html element that holds the chart
var viz_container;

// our weighted tree
var viz;

// our theme
var theme;

// nested data
var data = {};

var valueField = "weight";//size也可以
var valueFields = [ "weight","demand"];


function loadData() {

    $.get('/showtree/', function(root) {//d3.json这个函数在d3.js里面

        data = flatten(root);
        initialize();

    });

}

// Returns a list of all nodes under the root.
function flatten(root) {
    var i = 0;

    function recurse(node) {//这里只是定义了函数，但是未被调用，在后面才被调用  reduce回调函数
    if (node.children) for (x in node.children){recurse(node.children[x]);};

    if (!node.id) node.id = ++i;

    }

    recurse(root);//调用前面定义的函数，存入参数root，root才之前被赋予了JSON数据
    return root;
}

function prepData(json) {

    var nest=json;

    //This will be a viz.data function;
    vizuly.data.aggregateNest(nest.values, valueField, function (a, b) {
        return Number(a) + Number(b);
    });

    //Remove empty child nodes left at end of aggregation and add unqiue ids
    function removeEmptyNodes(node,parentId,childId) {
        if (!node) return;
        node.id=parentId + "_" + childId;
        if (node.values) {
            for(var i = node.values.length - 1; i >= 0; i--) {
                node.id=parentId + "_" + i;
                removeEmptyNodes(node.values[i],node.id,i)
            }
        }
    }

    removeEmptyNodes(nest,"0","0");

    return nest;
}

function initialize() {


    viz = vizuly.viz.weighted_tree(document.getElementById("viz_container"));


    //Here we create three vizuly themes for each radial progress component.
    //A theme manages the look and feel of the component output.  You can only have
    //one component active per theme, so we bind each theme to the corresponding component.
    theme = vizuly.theme.weighted_tree(viz).skin(vizuly.skin.WEIGHTED_TREE_AXIIS);

    //Like D3 and jQuery, vizuly uses a function chaining syntax to set component properties
    //Here we set some bases line properties for all three components.
    viz.data(data)                                                      // Expects hierarchical array of objects.
        .width(600)                                                     // Width of component
        .height(600)                                                    // Height of component
        .children(function (d) { return d.children })                     // Denotes the property that holds child object array
        .key(function (d) { return d.id })                              // Unique key
        .value(function (d) {
            return Number(d[valueField])})                    // The property of the datum that will be used for the branch and node size
        .fixedSpan(-1)                                                  // fixedSpan > 0 will use this pixel value for horizontal spread versus auto size based on viz width
        .label(function (d) {                                           // returns label for each node.
            return trimLabel(d.key)})
        .on("measure",onMeasure)                                        // Make any measurement changes
        .on("mouseover",onMouseOver)                                    // mouseover callback - all viz components issue these events
        .on("mouseout",onMouseOut)                                      // mouseout callback - all viz components issue these events
        .on("click",onClick)                                           // mouseout callback - all viz components issue these events
        .on("dblclick",click);


    //We use this function to size the components based on the selected value from the RadiaLProgressTest.html page.
    changeSize("1000,1000");

    // Open up some of the tree branches.这里可以自定义页面舒刷新后的初始展示情况
    viz.toggleNode();//这样只展开第一级节点，也就是默认情况
    //viz.toggleNode(data.children[1]);//再展开第一级结点的基础上，将展开第一级节点的第二个节点的全部子节点
    //viz.toggleNode(data.children[2]);


}


function trimLabel(label) {
   return (String(label).length > 20) ? String(label).substr(0, 17) + "..." : label;
}


var datatip='<div class="tip" style="width: 250px; background-opacity:.5">' +
    '<div class="header2"> HEADER2 </div>' +
    '<div class="header-rule"></div>' +
    '<div class="header3"> HEADER3 </div>' +
    '</div>';


// This function uses the above html template to replace values and then creates a new <div> that it appends to the
// document.body.  This is just one way you could implement a data tip.
function createDataTip(x,y,h1,h2) {

    var html = datatip.replace("HEADER2", h1);
    //html = html.replace("HEADER2", h2);
    html = html.replace("HEADER3", h2);

    d3.select("body")
        .append("div")
        .attr("class", "vz-weighted_tree-tip")
        .style("position", "absolute")
        .style("top", y + "px")
        .style("left", (x - 125) + "px")
        .style("opacity",0)
        .html(html)
        .transition().style("opacity",1);

}

function onMeasure() {
   // Allows you to manually override vertical spacing
   // viz.tree().nodeSize([100,0]);
}

function onMouseOver(e,d,i) {
    if (d == data) return;
    var rect = e.getBoundingClientRect();
    if (d.target) d = d.target; //This if for link elements
    createDataTip(rect.left, rect.top,"大纲要求", (d[valueField]));

}

function onMouseOut(e,d,i) {
    d3.selectAll(".vz-weighted_tree-tip").remove();
}



//We can capture click events and respond to them
function onClick(g,d,i) {
    viz.toggleNode(d);
}

function click(d) {
    d3.event.defaultPrevented||window.open("category/1");
}

//This function is called when the user selects a different skin.
function changeSkin(val) {
    if (val == "None") {
        theme.release();
    }
    else {
        theme.viz(viz);
        theme.skin(val);
    }

    viz().update();  //We could use theme.apply() here, but we want to trigger the tween.
}

//This changes the size of the component by adjusting the radius and width/height;
function changeSize(val) {
    var s = String(val).split(",");
    viz_container.transition().duration(300).style('width', s[0] + 'px').style('height', s[1] + 'px');
    viz.width(s[0]).height(s[1]*.8).update();
}