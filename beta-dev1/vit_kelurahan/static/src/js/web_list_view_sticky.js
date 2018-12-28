odoo.define('web.FreezeTableHeader',function (require) {
    "use strict";

    var core = require('web.core');
    var ListView = require('web.ListView');
    var _t = core._t;

    var FreezeTableHeader = ListView.include({
        load_list: function () {
            var self = this;
            var a = self._super.apply(this, arguments);
            var scrollArea = self.$el.parents('.oe-view-manager.oe_view_manager_current').find('.oe-view-manager-content .oe-view-manager-view-list').prevObject.prevObject[0]
            var tables= self.$el.find('table.o_list_view');
            var fieldsviewtype = this.fields_view.type
            if (this.fields_view.type == 'tree'){
                if (this.model == 'vit.kelurahan' || this.model == 'res.country.state' || this.model == 'vit.kota' || this.model == 'vit.kecamatan') {
                     tables.each(function(){
                           $(this).stickyTableHeaders({scrollableArea: scrollArea, leftOffset: scrollArea, "fixedOffset": 1 })
                     });
                }
            }else{
                 tables.each(function(){
                    $(this).stickyTableHeaders({scrollableArea: scrollArea, leftOffset: scrollArea, "fixedOffset": 0 })
                 });
            }
            $(document).ready(function () {
                if ($('.o_main').length > 0) {
                    $(".o_main").scroll(function(evt){
                        var self = this;
                        var header = $(".tableFloatingHeaderOriginal");
                        if (fieldsviewtype == 'tree'){
                            if (header.length > 0) {
                                if ($(".o_main").scrollTop() === 0){
                                    header.css('top', '134.239px');
                                }else if ($(".o_main").scrollTop() > 1 && $(".o_main").scrollTop() < 5){
                                    header.css('top', '131.239px');
                                }else if ($(".o_main").scrollTop() > 5 && $(".o_main").scrollTop() < 10){
                                    header.css('top', '128.239px');
                                }else if ($(".o_main").scrollTop() === 10){
                                    header.css('top', '123.239px');
                                }else if ($(".o_main").scrollTop() > 10 && $(".o_main").scrollTop() < 15){
                                    header.css('top', '121.239px');
                                }else if ($(".o_main").scrollTop() >= 16 && $(".o_main").scrollTop() < 17){
                                    header.css('top', '117.239px');
                                }else if ($(".o_main").scrollTop() > 17 && $(".o_main").scrollTop() < 20){
                                    header.css('top', '112.239px');
                                }else if ($(".o_main").scrollTop() === 20){
                                    header.css('top', '113.239px');
                                }else if ($(".o_main").scrollTop() > 20 && $(".o_main").scrollTop() < 25){
                                    header.css('top', '111.239px');
                                }else if ($(".o_main").scrollTop() > 25 && $(".o_main").scrollTop() < 30){
                                    header.css('top', '107.239px');
                                }else if ($(".o_main").scrollTop() === 30){
                                    header.css('top', '103.239px');
                                }else if ($(".o_main").scrollTop() > 30 && $(".o_main").scrollTop() < 35){
                                    header.css('top', '100.239px');
                                }else if ($(".o_main").scrollTop() > 36 && $(".o_main").scrollTop() < 37){
                                    header.css('top', '97.239px');
                                }else if ($(".o_main").scrollTop() > 35 && $(".o_main").scrollTop() < 41){
                                    header.css('top', '94.239px');
                                }else if ($(".o_main").scrollTop() >= 41 && $(".o_main").scrollTop() < 43){
                                    header.css('top', '91.239px');
                                }else if ($(".o_main").scrollTop() > 41 && $(".o_main").scrollTop() < 45){
                                    header.css('top', '90.239px');
                                }else if ($(".o_main").scrollTop() > 46 && $(".o_main").scrollTop() < 47){
                                    header.css('top', '85.239px');
                                }else if ($(".o_main").scrollTop() > 47 && $(".o_main").scrollTop() < 49){
                                    header.css('top', '85.239px');
                                }else if ($(".o_main").scrollTop() > 45 && $(".o_main").scrollTop() <= 50){
                                    header.css('top', '84.239px');
                                }else if ($(".o_main").scrollTop() > 50 && $(".o_main").scrollTop() < 55){
                                    header.css('top', '80.239px');
                                }else if ($(".o_main").scrollTop() > 55 && $(".o_main").scrollTop() < 60){
                                    header.css('top', '76.239px');
                                }else if ($(".o_main").scrollTop() === 60){
                                    header.css('top', '74.239px');
                                }else if ($(".o_main").scrollTop() > 60 && $(".o_main").scrollTop() < 65){
                                    header.css('top', '71.239px');
                                }else if ($(".o_main").scrollTop() > 65 && $(".o_main").scrollTop() < 70){
                                    header.css('top', '66.239px');
                                }else if ($(".o_main").scrollTop() === 70){
                                    header.css('top', '63.239px');
                                }else if ($(".o_main").scrollTop() > 70 && $(".o_main").scrollTop() < 75){
                                    header.css('top', '60.239px');
                                }else if ($(".o_main").scrollTop() > 75 && $(".o_main").scrollTop() < 80){
                                    header.css('top', '57.239px');
                                }else if ($(".o_main").scrollTop() > 80 && $(".o_main").scrollTop() < 83){
                                    header.css('top', '53.239px');
                                }else if ($(".o_main").scrollTop() >= 83){
                                    header.css('top', '48.239px');
                                }
                            }
                        }
                    });
                }
            });
            return a;
        },
    });
});

