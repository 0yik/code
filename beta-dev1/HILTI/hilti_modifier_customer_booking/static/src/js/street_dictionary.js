//odoo.define('hilti_booking_map.hilti_booking_map', function (require) {
//    "use strict";
	var map, geocode, mm;
	
	window.onload = function(e){ 
		var opts = {
			zoom: 11,
			center: new GeoPoint(103.83050972046, 1.304787132947),
			enableDefaultLogo: false,
			showCopyright: false
		};
		map = new SD.genmap.Map(document.getElementById('map'), opts);
		console.log('rrrrrrrrrrrr', map)
		map.addLogo("/hilti_modifier_customer_booking/static/src/img/sd.jpg", {width:130, height:40}, SD.POSITION_BOTTOM_LEFT, "www.streetdirectory.com");
		
		var navControl = new CompleteMapControl();
		map.addControl(navControl); 
		navControl.setDisplay(0,false);
		
		geocode = new SDGeocode(map);
		geocode.removeMouseClick();
		
		EventManager.add(map, 'mousedown', function(e) {
			if (SD.util.getMouseButton(e) == 'RIGHT') {
				var px = map.fromLatLngToCanvasPixel(map.viewportInfo.lastCursorLatLon);
				var x = map.viewportInfo.lastCursorLatLon.lon.toString().substr(0, 10);
				var y = map.viewportInfo.lastCursorLatLon.lat.toString().substr(0, 8);
				
				map.infoWindow.open(px, 
									"Is this your location ?" + 
									" <br><input type='button' value='Yes' onclick='saveLongLat(" + x + "," + y + ");map.infoWindow.close();' />" + 
									" <input type='button' value='No' onclick='map.infoWindow.close();'>");
				
				map.infoWindow.visible = false;
				map.infoWindow.marker = null;
			}
		});		
	}
	
	function saveLongLat(x,y){
		$("#longlat").html(x + "," + y);
	}
    	
	function set_data(json) {
		if(mm != undefined) mm.clear();
		
		$("#ttl").html(0);
		$("#info").show();
		
		if(json == null) { $("#datatableInfo").children(":nth-child(1)").empty();return; }
		if(json.length == 0) { $("#datatableInfo").children(":nth-child(1)").empty();return; }
		
		$("#datatableInfo").css("width","280px");
		$("#datatableInfo").children("tbody").remove();
		
		var tbody = document.createElement("tbody");
		var no = 1;
		for (var i=0; i<json.length; i++) {
			var trow = $("<tr>"), rec = json[i];
			var c = no % 2 == 0 ? "ticked" : "unticked";
			$(trow).addClass(c);
			
			if (rec.x && rec.y)
			{				
				var icon = new SD.genmap.MarkerImage({
					image : "/hilti_modifier_customer_booking/static/src/img/openrice_icon.png",
					title : rec.t,
					iconSize : new Size(15, 15),
					iconAnchor : new Point(7, 15),
					infoWindowAnchor : new Point(5, 0)
				});
				
				mm = new SD.genmap.MarkerStaticManager({map:map});
				
				if (rec.x && rec.y){
					var geo = new GeoPoint(parseFloat(rec.x), parseFloat(rec.y));
					var marker = mm.add({
						position: geo,
						map: map,
						icon: icon
					});
				}			
			
				var c = no % 2 == 0 ? "ticked" : "unticked";
				if(!rec.a || rec.a == 'undefined') rec.a = '';
				
				var a = (rec.a == undefined) ? '' : rec.a;
				var ctn = "<strong>" + rec.t + "</strong><br>" + a;
				var td = $("<td>");
				$(td).addClass("datarow");
				
				var myid = escape("geo_" + rec.x + "_" + rec.y) ;
				var mytitle = escape("title_" + rec.t + "_" + rec.a);
				var myvalue = escape("title_" + rec.t + "_" + rec.a);
				
				$(td).attr("id",myid);
				$(td).attr("value", mytitle);
				
				$(td).html(ctn).data("col", 1).appendTo(trow);
				if (rec.x && rec.y)	assignClickEvent(trow, marker, rec);
				no++;
			}			
			trow.appendTo(tbody);
		}		
		$("#datatableInfo").append(tbody);
		
		$("#ccid").html($("#categorylist").val());
		$("#ttl").html(no-1);
	}
	
	function assignClickEvent(row, marker, rec) {
		row.click(function(){			
			$("#info").css("display","none");
			
			var tbody = $("#datatableInfo").children(":nth-child(1)");
			$(tbody).children().removeClass("selected");
			
			
			var address_array = rec.a.split('(S)');
			$("#address").val(address_array[0]);
			$("#postal_code").val(address_array[1]).focus();
			map.setCenter(marker.position, map.zoom);
			map.infoWindow.open(marker, rec.a);
		});
	}

	function search(region, keyword) {
		$("#info").hide();
		
		gc = SDGeocode.SG;
		if(region == 'ID')
			gc = SDGeocode.ID;
		else if(region == 'MY')
			gc = SDGeocode.MY;
		else if(region == 'PH')
			gc = SDGeocode.PH;
		
		var searchOption = {
			"q": keyword, 
			"limit": 20, 
			"ctype": 1
		};
		geocode.requestData(gc, searchOption);
	}

	function enter_handle(obj) {
		if(obj.id) {			
			var rec = unescape(obj.id).split("_");
			var title = unescape(obj.title).split("_");
			
			var icon = new SD.genmap.MarkerImage({
				image : "/hilti_modifier_customer_booking/static/src/img/openrice_icon.png",
				title : title[0] ,
				iconSize : new Size(15, 15),
				iconAnchor : new Point(7, 15),
				infoWindowAnchor : new Point(5, 0)
			});
			
			mm = new SD.genmap.MarkerStaticManager({map:map});
			
			var geo = new GeoPoint(parseFloat(rec[1]), parseFloat(rec[2]));
			var marker = mm.add({
				position: geo,
				map: map,
				icon: icon
			});
			
			map.setCenter(marker.position, map.zoom);
			map.infoWindow.open(marker, title[1]);
		}
	}
	
	function suggest() {
		setTimeout(
		function() {
			var keyword = $("#address").val();
			if(keyword.length > 0) {
				search('SG', keyword);
			}
			else {
				$("#datatableInfo").empty();
			}
		},
		1000);
	}
	
	
	$(document).ready(function(){
		$("#address").hilite_arrow({
			tableid:"#datatableInfo",
			onenter:"enter_handle",
			hilite:"selected",
			other_key:"suggest()",
			divid:"#info"
		});
	})
//});	