$(document).ready(function() {
    $('.slideshow').cycle({
        fx: 'fade' // choose your transition type, ex: fade, scrollUp, shuffle, etc...
    });
});


/* Other functions */
function showHide(){
    //create an object reference to the div containing images
    var oImageDiv=document.getElementById('myimageDiv')
    //set display to inline if currently none, otherwise to none
    oImageDiv.style.display=(oImageDiv.style.display=='none')?'inline':'none'
}

function ScrollableTable (tableEl, tableHeight, tableWidth) {
 
	this.initIEengine = function () {
 
		this.containerEl.style.overflowY = 'auto';
		if (this.tableEl.parentElement.clientHeight - this.tableEl.offsetHeight < 0) {
			this.tableEl.style.width = this.newWidth - this.scrollWidth +'px';
		} else {
			this.containerEl.style.overflowY = 'hidden';
			this.tableEl.style.width = this.newWidth +'px';
		}
 
		if (this.thead) {
			var trs = this.thead.getElementsByTagName('tr');
			for (x=0; x<trs.length; x++) {
				trs[x].style.position ='relative';
				trs[x].style.setExpression("top",  "this.parentElement.parentElement.parentElement.scrollTop + 'px'");
			}
		}
 
		if (this.tfoot) {
			var trs = this.tfoot.getElementsByTagName('tr');
			for (x=0; x<trs.length; x++) {
				trs[x].style.position ='relative';
				trs[x].style.setExpression("bottom",  "(this.parentElement.parentElement.offsetHeight - this.parentElement.parentElement.parentElement.clientHeight - this.parentElement.parentElement.parentElement.scrollTop) + 'px'");
			}
		}
 
		eval("window.attachEvent('onresize', function () { document.getElementById('" + this.tableEl.id + "').style.visibility = 'hidden'; document.getElementById('" + this.tableEl.id + "').style.visibility = 'visible'; } )");
	};
 
 
	this.initFFengine = function () {
		this.containerEl.style.overflow = 'hidden';
		this.tableEl.style.width = this.newWidth + 'px';
 
		var headHeight = (this.thead) ? this.thead.clientHeight : 0;
		var footHeight = (this.tfoot) ? this.tfoot.clientHeight : 0;
		var bodyHeight = this.tbody.clientHeight;
		var trs = this.tbody.getElementsByTagName('tr');
		if (bodyHeight >= (this.newHeight - (headHeight + footHeight))) {
			this.tbody.style.overflow = '-moz-scrollbars-vertical';
			for (x=0; x<trs.length; x++) {
				var tds = trs[x].getElementsByTagName('td');
				tds[tds.length-1].style.paddingRight += this.scrollWidth + 'px';
			}
		} else {
			this.tbody.style.overflow = '-moz-scrollbars-none';
		}
 
		var cellSpacing = (this.tableEl.offsetHeight - (this.tbody.clientHeight + headHeight + footHeight)) / 4;
		this.tbody.style.height = (this.newHeight - (headHeight + cellSpacing * 2) - (footHeight + cellSpacing * 2)) + 'px';
 
	};
 
	this.tableEl = tableEl;
	this.scrollWidth = 16;
 
	this.originalHeight = this.tableEl.clientHeight;
	this.originalWidth = this.tableEl.clientWidth;
 
	this.newHeight = parseInt(tableHeight);
	this.newWidth = tableWidth ? parseInt(tableWidth) : this.originalWidth;
 
	this.tableEl.style.height = 'auto';
	this.tableEl.removeAttribute('height');
 
	this.containerEl = this.tableEl.parentNode.insertBefore(document.createElement('div'), this.tableEl);
	this.containerEl.appendChild(this.tableEl);
	this.containerEl.style.height = this.newHeight + 'px';
	this.containerEl.style.width = this.newWidth + 'px';
 
 
	var thead = this.tableEl.getElementsByTagName('thead');
	this.thead = (thead[0]) ? thead[0] : null;
 
	var tfoot = this.tableEl.getElementsByTagName('tfoot');
	this.tfoot = (tfoot[0]) ? tfoot[0] : null;
 
	var tbody = this.tableEl.getElementsByTagName('tbody');
	this.tbody = (tbody[0]) ? tbody[0] : null;
 
	if (!this.tbody) return;
 
	if (document.all && document.getElementById && !window.opera) this.initIEengine();
	if (!document.all && document.getElementById && !window.opera) this.initFFengine();
 
 
}


/////////////////////////////////// /gray out

function grayOut(vis, options, extra) {
  // Pass true to gray out screen, false to ungray
  // options are optional.  This is a JSON object with the following (optional) properties
  // opacity:0-100         // Lower number = less grayout higher = more of a blackout 
  // zindex: #             // HTML elements with a higher zindex appear on top of the gray out
  // bgcolor: (#xxxxxx)    // Standard RGB Hex color code
  // grayOut(true, {'zindex':'50', 'bgcolor':'#0000FF', 'opacity':'70'});
  // Because options is JSON opacity/zindex/bgcolor are all optional and can appear
  // in any order.  Pass only the properties you need to set.
  var options = options || {}; 
  var zindex = options.zindex || 50;
  var opacity = options.opacity || 70;
  var opaque = (opacity / 100);
  var bgcolor = options.bgcolor || '#000000';
  var dark=document.getElementById('darkenScreenObject');
  if (!dark) {
    // The dark layer doesn't exist, it's never been created.  So we'll
    // create it here and apply some basic styles.
    // If you are getting errors in IE see: http://support.microsoft.com/default.aspx/kb/927917
    var tbody = document.getElementsByTagName("body")[0];
    var tnode = document.createElement('div');           // Create the layer.
        tnode.style.position='absolute';                 // Position absolutely
        tnode.style.top='0px';                           // In the top
        tnode.style.left='0px';                          // Left corner of the page		
        tnode.style.overflow='hidden';                   // Try to avoid making scroll bars            
        tnode.style.display='none';                      // Start out Hidden
        tnode.id='darkenScreenObject';                   // Name it so we can find it later
		
	//var msgnode = document.createElement('div');           // Create the box layer.
    var msgnode = document.getElementById('box');
		msgnode.style.position='fixed';                 // Position fixed
        msgnode.style.display='none';                      // Start out Hidden
        msgnode.id='box';                   				// Name it so we can find it later
		// give it a size and align it to center
		//msgnode.style.width = "300px";
		//msgnode.style.height = "300px";
		msgnode.style.marginLeft= "-150px";      
		msgnode.style.marginTop= "-150px"; 
		msgnode.style.textAlign = 'center';
		msgnode.style.top= "50%";                           // In the top	
		msgnode.style.left="50%";                          // Left corner of the page	
	tbody.appendChild(msgnode);                            // Add it to the grey screen
    tbody.appendChild(tnode);                            // Add it to the web page
    dark=document.getElementById('darkenScreenObject');  // Get the object.
  }
  if (vis) {
    // Calculate the page width and height 
    if( document.body && ( document.body.scrollWidth || document.body.scrollHeight ) ) {
        var pageWidth = document.body.scrollWidth+'px';
        var pageHeight = document.body.scrollHeight+'px';
    } else if( document.body.offsetWidth ) {
      var pageWidth = document.body.offsetWidth+'px';
      var pageHeight = document.body.offsetHeight+'px';
    } else {
       var pageWidth='100%';
       var pageHeight='100%';
    }   
    //set the shader to cover the entire page and make it visible.
    dark.style.opacity=opaque;                      
    dark.style.MozOpacity=opaque;                   
    dark.style.filter='alpha(opacity='+opacity+')'; 
    dark.style.zIndex=zindex;        
    dark.style.backgroundColor=bgcolor;  
    dark.style.width= pageWidth;
    dark.style.height= pageHeight;
    dark.style.display='block';  
	if(extra == 'Y')
		document.body.style.overflow =  'hidden';
		
	document.getElementById("box").style.zIndex = zindex+10;
	//document.getElementById("box").style.border = "#000 solid 1px";
	document.getElementById("box").style.display = "block";
		
 
	//document.getElementById("box").onclick = function() //attach a event handler to hide both div
	//{
	//	dark.style.display="none";
	//	document.getElementById("box").style.display = "none";
	//	document.body.style.overflow = 'auto';
	//	
	//}
	//document.getElementById("box").style.backgroundColor="#FFF";  
	//document.getElementById("box").innerHTML = "This is a box. Click me to exit effect.";
	//document.getElementById("box").innerHTML = '<img src="/static/style/img/loading2.gif" />';
    //document.getElementById("box").style.backgroundImage="url(/static/style/img/loading2.gif)";
  } else {
     dark.style.display='none';
  }
}

//document.getElementById("box").style.display = "none";
