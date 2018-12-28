$(document).ready(function(){
    $('#search-menu').on('keyup', function(e){
        var searchTerm = $(this).val().toLowerCase();
        $('.oe_application_menu_placeholder li').each(function(){

            if ($(this).filter('[data-search-term *= ' + searchTerm + ']').length > 0 || searchTerm.length < 1) {
                $(this).show();
                $(this).addClass('active_search');
            } else {
                $(this).hide();
                $(this).removeClass('active_search');
            }
        });

        if(e.which == 13){//Enter key pressed
            $(this).next('ul').find('li.active_search a').first().trigger("click");//Trigger search button click event
        }
    });
	
	// coded by anand on 28 nov 2017 for more than 6 menu items shows in More menu.
	$('li.more_menu').hover(function(){
		$(this).find('ul').addClass('more_submenu');
		$(this).find('a.dropdown-toggle > span').removeClass('caret');
		$(this).find('a.dropdown-toggle > span').addClass('caret-right');
	},function(){
    	$(this).find('ul').removeClass('more_submenu');
		$(this).find('a.dropdown-toggle > span').removeClass('caret-right');
		$(this).find('a.dropdown-toggle > span').addClass('caret');
	});
	// code finished
});



$.ctrl = function(key, callback, args) {
    $(document).keydown(function(e) {
        if(!args) args=[]; // IE barks when args is null
        if((e.keyCode == key.charCodeAt(0) || e.keyCode == key) && e.altKey) {
            callback.apply(this, args);
        }
    });        
};

// //ctrl + A  Edit Record
$.ctrl('65', function() {
    // $('.o_form_button_edit').each(function() {
    //     if($(this).parents('div:hidden').length == 0){
    //         $(this).trigger('click');
    //     }
    // });
    if ($('th.o_list_record_selector').length != 0){
        $('th.o_list_record_selector .o_checkbox').find('input').trigger('click');
    }
});

//ctrl + X  Export Record
$.ctrl('88', function() {
    $('.dropdown-menu li a').each(function() {
        if($(this).data('index') == 0 && $(this).data('section') == 'other' && $(this).text().trim() == 'Export'){
            $(this).trigger('click');
        }
    });
});

//ctrl + I  Import Record
$.ctrl('73', function() {
    $('.o_button_import').each(function() {
        if($(this).parents('div:hidden').length == 0){
            $(this).trigger('click');
        }
    });
});

//Alt + Y Open Calendar (the calendar module)
$.ctrl('89', function() {
    $('a.oe_menu_leaf').each(function() {
        if($(this).data('menu-name') == 'Calendar'){
            $(this).trigger('click');
        }
    });
});

//Alt + T Open Calendar View
$.ctrl('84', function() {
    $('button.fa-calendar').each(function() {
        if($(this).data('original-title') == 'Calendar'){
            $(this).trigger('click');
        }
    });
});

//Alt + F On Focus Search view
$.ctrl('107', function() {
    $('input.o_searchview_input').each(function() {
        $(this).focus();
    });
});

//Alt + J Open advanced search & open add custo
$.ctrl('74', function() {
    $('.o_searchview_more').trigger('click');
    $('.fa-filter').trigger('click');
    $('.o_add_filter').each(function() {
        $(this).trigger('click');
    });
});

//ctrl + Q (Query) Toggle Advanced Search
$.ctrl('81', function() {
    $('.o_filters_menu li').each(function() {
        if ($(this).hasClass('unselected')){
            $('li.unselected a').trigger('click');
            $(this).removeClass('unselected');
            $('.fa-filter').trigger('click');
        }else if ($(this).hasClass('selected')){
            $('.fa-filter').trigger('click');
            $(this).addClass('unselected');
            $('.o_facet_remove').trigger('click');
        }
    });
});

//Alt + U Change tree view to Unlimited 
$.ctrl('85', function() {
    var total_u = '1-'+$('span.o_pager_limit').text();
    if (total_u){
        $('.o_cp_pager span.o_pager_value').trigger('click');
        $('.o_cp_pager span.o_pager_value').find('input').val(total_u)
        var e = jQuery.Event("keydown");
        e.which = 13;
        e.keyCode = 13;
        $('.o_cp_pager span.o_pager_value').find('input').trigger(e);
    }
});

//Alt + H Remove All Filter From Searchbar 
$.ctrl('72', function() {
    $('div.fa-remove').each(function() {
        $(this).trigger('click');
    });
    $('div.fa-remove').each(function() {
        $(this).trigger('click');
    });
});

//Alt + K Open Kanban
$.ctrl('75', function() {
    if ($('.o_cp_switch_kanban').length != 0){
        $('o_cp_switch_kanban').trigger('click');
    }
});

//cAlt + N Open App Drawer 
$.ctrl('78', function() {
    if ($('.app-drawer-icon-open').length != 0){
        $('.app-drawer-icon-open').trigger('click');
    }
});

//ctrl + B Open Progress bar 
$.ctrl('66', function() {
    if ($('a#planner_pdf_open').length != 0){
        $('a#planner_pdf_open').trigger('click');
    }
});

//ctrl + Alt + Duplicate Current Record
$.ctrl('68', function() {
    console.log('ddd')
    $('.dropdown-menu li a').each(function() {
        if($(this).data('section') == 'other' && $(this).text().trim() == 'Duplicate'){
            $(this).trigger('click');
        }
    });
    $('button.o_dropdown_toggler_btn').each(function() {
        if($(this).text().trim() == 'Action'){
            $(this).find('.dropdown-menu li a').each(function() {
                if($(this).text().trim() == 'Duplicate'){
                    $(this).trigger('click');
                }
            });
        }
    });
});

//Alt + M Click on More button
$.ctrl('77', function() {
    $('button.o_dropdown_toggler_btn').each(function() {
        if($(this).text().trim() == 'Action'){
            $(this).parents('div.o_dropdown').addClass('open');
        }
    });
});

//Alt + P Click on Print button
$.ctrl('80', function() {
    $('button.o_dropdown_toggler_btn').each(function() {
        if($(this).text().trim() == 'Print'){
            $(this).parents('div.o_dropdown').addClass('open');
        }
    });
});

// Alt Key + Z : Back to Previous Page 
$.ctrl('90', function() {
    $('ol.breadcrumb li.active').each(function() {
        if($(this).prev('li')){
            $(this).prev('li').trigger('click');
        }
    });
});

// Ctrl Key + > : Next Record
$.ctrl('39', function() {
    if ($('button.o_pager_next').length != 0){
        $('button.o_pager_next').trigger('click');
    }
});

// Ctrl Key + < : Previous Record
$.ctrl('37', function() {
    if ($('button.o_pager_previous').length != 0){
        $('button.o_pager_previous').trigger('click');
    }
});

// Ctrl Key + G : Open Graph View
$.ctrl('71', function() {
    if ($('.o_cp_switch_graph').length != 0){
        $('.o_cp_switch_graph').trigger('click');
    }
});

// Ctrl + alt + R : Open Pivot View
$.ctrl('87', function() {
    if ($('.o_pivot_flip_button').length != 0){
        $('.o_pivot_flip_button').trigger('click');
    }
    if ($('.o_pivot_expand_button').length != 0){
        $('.o_pivot_expand_button').trigger('click');
    }
});

// Ctrl + alt + w : Click on Expand Pivot View
$.ctrl('82', function() {
    if ($('.o_cp_switch_pivot').length != 0){
        $('.o_cp_switch_pivot').trigger('click');
    }
});

// alt + v : Click on Expand Pivot View
$.ctrl('86', function() {
    if ($('.o_pivot_download').length != 0){
        $('.o_pivot_download').trigger('click');
    }
});

//alt + Delete : Delete Record
$.ctrl('46', function() {
    $('button.o_dropdown_toggler_btn').each(function() {
        if($(this).text().trim() == 'Action'){
            $(this).next().find('li a').each(function() {
                if ( $(this).text().trim() == 'Delete'){
                    $(this).trigger('click');    
                }
            });
        } 
    });
});

// Ctrl + Alt + U : Activate Developer Mode
$.ctrl('85', function() {
    window.location = $.param.querystring( window.location.href, '?debug=');
});


$.ctrl('49', function() {
    $('ul.oe_secondary_menu.navbar-nav:visible li:eq( 2 )').each(function(){
        $(this).find('a').trigger('click');
    });
});
$.ctrl('50', function() {
    if ($('ul.oe_secondary_menu.navbar-nav:visible li a.dropdown-toggle:eq(0)')){
        $('ul.oe_secondary_menu.navbar-nav:visible li a.dropdown-toggle:eq(0)').trigger('click');    
    }
});
$.ctrl('51', function() {
    if ($('ul.oe_secondary_menu.navbar-nav:visible li a.dropdown-toggle:eq(1)')){
        $('ul.oe_secondary_menu.navbar-nav:visible li a.dropdown-toggle:eq(1)').trigger('click');    
    }
});
$.ctrl('52', function() {
    if ($('ul.oe_secondary_menu.navbar-nav:visible li a.dropdown-toggle:eq(2)')){
        $('ul.oe_secondary_menu.navbar-nav:visible li a.dropdown-toggle:eq(2)').trigger('click');    
    }
});
$.ctrl('53', function() {
    if ($('ul.oe_secondary_menu.navbar-nav:visible li a.dropdown-toggle:eq(3)')){
        $('ul.oe_secondary_menu.navbar-nav:visible li a.dropdown-toggle:eq(3)').trigger('click');    
    }
});
$.ctrl('54', function() {
    if ($('ul.oe_secondary_menu.navbar-nav:visible li a.dropdown-toggle:eq(4)')){
        $('ul.oe_secondary_menu.navbar-nav:visible li a.dropdown-toggle:eq(4)').trigger('click');    
    }
});
$.ctrl('55', function() {
    if ($('ul.oe_secondary_menu.navbar-nav:visible li a.dropdown-toggle:eq(5)')){
        $('ul.oe_secondary_menu.navbar-nav:visible li a.dropdown-toggle:eq(5)').trigger('click');    
    }
});
$.ctrl('56', function() {
    if ($('ul.oe_secondary_menu.navbar-nav:visible li a.dropdown-toggle:eq(6)')){
        $('ul.oe_secondary_menu.navbar-nav:visible li a.dropdown-toggle:eq(6)').trigger('click');    
    }
});
$.ctrl('57', function() {
    if ($('ul.oe_secondary_menu.navbar-nav:visible li a.dropdown-toggle:eq(7)')){
        $('ul.oe_secondary_menu.navbar-nav:visible li a.dropdown-toggle:eq(7)').trigger('click');    
    }
});



odoo.define('hm_system.hm_system', function (require) {
    "use strict";

var bus = require('bus.bus').bus;
var core = require('web.core');
var Model = require('web.Model');
var CalendarView = require('web_calendar.CalendarView');
var data = require('web.data');
var Dialog = require('web.Dialog');
var SystrayMenu = require('web.SystrayMenu');
var WebClient = require('web.WebClient');
var weblient = require('web.web_client');
var widgets = require('web_calendar.widgets');
var Widget = require('web.Widget');
var UserMenu = require('web.UserMenu');
var Menu = require('web.Menu');
var _t = core._t;
var _lt = core._lt;
var QWeb = core.qweb;

    UserMenu.include({
        on_menu_support: function () {
            window.open('https://support.hashmicro.com', '_blank');
        },
        on_menu_hashmicro: function () {
            window.open('https://www.hashmicro.com', '_blank');
        },
    });

    WebClient.include({
        _title_changed: function() {
            var parts = _.sortBy(_.keys(this.get("title_part")), function(x) { return x; });
            var tmp = "";
            _.each(parts, function(part) {
                var str = this.get("title_part")[part];
                if (str == 'Odoo'){
                    str = 'EQUIP ERP'
                }
                if (str) {
                    tmp = tmp ? tmp + " - " + str : str;
                }

            }, this);
            document.title = tmp;
        },
    });

    CalendarView.include({
        get_fc_init_options: function () {
            var result = this._super();
            result.defaultView = 'month'
            return result
        },
    });


    var PlannerDialogPdf = Widget.extend({
        template: "PlannerDialogPdf",
        init: function(parent, plannerpdf) {
            this._super(parent);
            this.menu_pdf = plannerpdf;
        },
        start: function() {
            var self = this;
            this.$('.o_currently_shown_page').text(this.menu_pdf.name);
            this.$('.modal-header').after(QWeb.render('PlannerContentPdf', {'menu_pdf':this.menu_pdf}));
            return this._super.apply(this, arguments)
        },
    });

    var PlannerLauncherPDf = Widget.extend({
        sequence: 100, // force it to be the left-most item in the systray to prevent flickering as it is not displayed in all apps
        template: "PlannerLauncherPDf",
        init: function(parent) {
            this._super(parent);
        },
        start: function() {
            var self = this;
            core.bus.on("change_menu_section", self, self.on_menu_clicked);

            var res =  self._super.apply(this, arguments).then(function() {
                self.$el.on('click', self, self.show_dialog.bind(self));
            });
            return res;
        },
        on_menu_clicked: function(menu_id) {
            var menu_pdf1 = '';
            var self = this;
            if (menu_id){
                (new Model('web.planner.pdf')).query().all().then(function(res) {
                    _.each(res, function(plannerpdf){
                        if (parseInt(plannerpdf.menu_get_id[0]) == parseInt(menu_id)){
                            menu_pdf1 = plannerpdf;                       
                            $('.navbar-right li.planner_pdf').removeClass('hidden');
                            self.setup(plannerpdf);
                        }
                    });
                });
                if (!menu_pdf1){
                    $('.navbar-right li.planner_pdf').addClass('hidden');
                }
            }
        },
        setup: function(menu_pdf) {
            var self = this;

            this.menu_pdf = menu_pdf;
            if (this.dialog) {
                this.dialog.$el.modal('hide');
                this.dialog.destroy();
            }
            this.dialog = new PlannerDialogPdf(this, menu_pdf);
            this.dialog.appendTo($('<div>'));

        },
        show_dialog: function() {
            this.dialog.$el.appendTo(weblient.$el);
            this.dialog.$el.modal('show');
        },
    });

    SystrayMenu.Items.push(PlannerLauncherPDf);

    return {
        PlannerDialogPdf: PlannerDialogPdf,
        PlannerLauncherPDf: PlannerLauncherPDf,
    };
    // Menu.include({
    //     on_change_top_menu: function(menu_id, needaction) {
    //         console.log('Click....',$(this), menu_id)
    //         var menu_pdf = '';
    //         if (menu_id){
    //             (new Model('web.planner.pdf')).query().all().then(function(res) {
    //                 _.each(res, function(plannerpdf){
    //                     console.log('ssss',plannerpdf)
    //                     if (plannerpdf.menu_get_id[0] == menu_id){
    //                         menu_pdf = plannerpdf
    //                         $('.navbar-right.o_menu_systray li.planner_pdf').removeClass('hidden');
    //                     }else{
    //                         console.log('>>>',$('.navbar-right.o_menu_systray li.planner_pdf'));
    //                         $('.navbar-right.o_menu_systray li.planner_pdf').addClass('hidden');
    //                     }
    //                 });
    //             }).then(function() {
                    
    //                 // $('.navbar-right.o_menu_systray li.planner_pdf a').click(function(ev){
    //                 //     ev.preventDefault();
    //                 //     console.log('>>SSSs',menu_pdf);
    //                 //     var dialog = new Dialog(this, {
    //                 //         size: 'medium',
    //                 //         $content: $('<div>', {
    //                 //             // html: QWeb.render('PlannerDialogPdf', {'menu_pdf':menu_pdf}),
    //                 //         }),
    //                 //         title: _t(menu_pdf.name),
    //                 //     }).open();
    //                 // });
    //             });
    //         }
    //         this._super.apply(this, arguments);
    //     },
    // });



    // PlannerDialog.include({
    //     init: function(parent, planner) {
    //         this._super.apply(this, arguments)
    //         this.pages = [];
    //         var page_pdf = [];
    //     },
    //     render_menu: function() {
    //         var menu = $.parseHTML(this._super.apply(this, arguments));
    //         var menu_pdf = [];
    //         var self = this;
    //         (new Model('web.planner.pdf')).query().all().then(function(res) {
    //             _.each(res, function(plannerpdf){
    //                 menu_pdf.push(plannerpdf);
    //             });
    //         }).then(function() {
    //             $.each( menu_pdf, function( i, el ) {
    //               menu[ 1 ].innerHTML = QWeb.render('PlannerMenuPdf', {'menu_pdf':menu_pdf});
    //             });
    //         });

    //         setTimeout(function(){
                
    //         }, 2000);
    //         return menu
    //     },
    //     _display_page: function(page_id) {
    //         var page = this._find_page_by_id(page_id);
    //         if (page){
    //             return this._super.apply(this, arguments)
    //         }else{
    //             if (this.currently_shown_page) {
    //                 $(this.currently_shown_page.dom).removeClass('show');
    //             }
    //             var page = '';
                
    //             (new Model('web.planner.pdf')).query().all().then(function(res) {
    //                 _.each(res, function(plannerpage){
    //                     if(String(plannerpage.iname) == String(page_id)){
    //                         page = plannerpage;
    //                     }
    //                 });
    //             });

    //             setTimeout(function(){
    //                 $('div#container_pdf').remove();
    //                 $('div.o_planner_content_wrapper').append(QWeb.render('PlannerMenupage', {page:page,html_cont:$.parseHTML(page.tooltip_planner)[0].innerHTML}));
    //             }, 1000);
                
    //         }
    //     },
    // });



});
