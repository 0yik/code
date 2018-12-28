/*
 * jQuery.hilite_arrow.js - selecting table row using keyboard arrow and action when enter
 *
 * version 0.01 (2010/06/1) 
 * 
 * Dual licensed under the MIT and GPL licenses: 
 *   http://www.opensource.org/licenses/mit-license.php 
 *   http://www.gnu.org/licenses/gpl.html 
 */

/**
 *
 * @example   $("#inputtest").hilite_arrow(
				{tableid:"#mytable",
				 onenter:"myfunction()",
				 hilite:"classname"
				 }
				 );
 * @desc Limit selecting table row using keyboard arrow and action when enter
 *
 * @name hilite_arrow
 * @type jQuery
 * @param Object
 * @cat Plugins/hilite_arrow
 * @return jQuery
 * @author Ahmad Satiri (satiri.a@gmail.com)
 */
 
jQuery.fn.hilite_arrow = function(args,e){

	if (!e) e = window.event;
	var charCode;
	var ctrl=false;
	var shift=false;
	var alt=false;
	
	if(e && e.which){
		charCode = e.which;
	}else if(window.event){
		e = window.event;
		charCode = e.keyCode;
	}		

	var _x = 0;
	var _y = 0;
	
	/*
	if($.browser.msie()){
		var _x = e.clientX;
		var _y = e.clientY;		
	}else{
		var _x = e.pageX;
		var _y = e.pageY;
	}*/
		
	//parameters
	var tableid = args.tableid?args.tableid:null;
	var onenter = args.onenter?args.onenter:null;
	var childlabel = args.childaslabel?args.childaslabel:1;
	var hilite = args.hilite?args.hilite:"selected";
	var other_key = args.other_key?args.other_key:null;
	var stop_at_edge = args.stop_at_edge?args.stop_at_edge:true;
	var divid = args.divid?args.divid:null;
	
	var currentchild = 0;
	var jchild = 0;
	
	this.selected = 0;

	function getCharCode(e){	
		
		if (!e) e = window.event;
		var charCode;
		var ctrl=false;
		var shift=false;
		var alt=false;
	
		if(e && e.which){
			charCode = e.which;
		}else if(window.event){
			e = window.event;
			charCode = e.keyCode;
		}


		_x = e.pageX;
		_y = e.pageY;
	
		
		var result = {"charCode":charCode,"ctrl":ctrl,"alt":alt,"shift":shift,e:e};
		return result;
	}
	
	function getChildSize(){
		var tbody = $(tableid).children(":nth-child(1)");
		var jumlah = 0;		
			
		$(tbody).children().each(function(){
			jumlah++;
		});
		return jumlah;
	}
	
	
	$(this).keyup(function(e){
			
		OcharCode = getCharCode(e);
		charCode = OcharCode.charCode;
		eval(this.other_key);			
		
	});
	
	$(this).keydown(function(e){
			
		OcharCode = getCharCode(e);
		charCode = OcharCode.charCode;
			
		
		if(tableid!=null){
								
				var tbody = $(tableid).children(":nth-child(1)");
				jchild = $(tbody).children().length;
				
				if(tbody.length){				
					if(charCode==37 || charCode==38 || charCode==39 || charCode==40 || charCode==17){	
						
						if(charCode==40){						
							if(stop_at_edge==false){
								if(currentchild==0){
									currentchild=1;
								}else{
									if(currentchild>=jchild){
										currentchild=1;
									}else{
										currentchild++;
									}
								}
							}else
							{
								if(currentchild==0){
									currentchild=1;
								}else{
									if(currentchild>=jchild){
										//currentchild=1;
									}else{
										if(currentchild<jchild){
											currentchild++;
										}
									}
								}								
								
							}
						}
						
						if(charCode==38){
							if(stop_at_edge==false){
								if(currentchild<=1){
									currentchild=4;
								}else{
									currentchild--;
								}						
							}else{
								if(currentchild<=1){
									//currentchild=4;
								}else{
									if(currentchild>1){
										currentchild--;
									}
								}													
							}
						}
										
						$(tbody).children().removeClass(hilite);
						
						//get x column of row
						var h_currentchild = $(tbody).children(":nth-child("+ currentchild +")");						
						$(h_currentchild).addClass(hilite);
						$(this).val($(h_currentchild).children(":nth-child("+ childlabel +")").text());
						
						//scroll to the bottom ?
						var scroll = (parseInt($(h_currentchild).css("height"))*currentchild)-35;
						$(divid).attr("scrollTop",scroll);
						$(divid).scroll();
						this.selected = currentchild;
					
					}else if(charCode==13){
					
						$(divid).css("visibility","hidden");						
						var h_currentchild = $(tbody).children(":nth-child("+ this.selected +")");						
					
						//export id and title to handled outside
						var myid = $(h_currentchild).children(":nth-child("+ childlabel +")").attr("id");
						var mytitle = $(h_currentchild).children(":nth-child("+ childlabel +")").attr("value");
						var myonenter = onenter + "({id:\""+ myid +"\",title:\""+ mytitle +"\"})";
									
						//reset selected			
						this.selected = 0;
						currentchild = 0;
						
						$(this).val("");
						eval(myonenter);		
					}else{
						eval(other_key);
					}

					
				}else{
					$(divid).css("visibility","visible");
					eval(other_key);
				}
				
		}else{
			$(divid).css("visibility","visible");
			eval(other_key);			
		}
	});
};
