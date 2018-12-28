odoo.define('modifier_honos_theme.ccm_website_editor_js', function(require) {
	'use strict';

    var ajax = require('web.ajax');
    var core = require('web.core');
    var website = require('website.website');
    var qweb = core.qweb;
    var _t = core._t;
    var options = require('web_editor.snippets.options');

    ajax.loadXML('/modifier_honos_theme/static/src/xml/ccm_theme.xml', qweb);

    options.registry.featured_categories = options.Class.extend({

        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("hidden");
            this.$target.find('.oe_multi_category_slider').empty();
            if (!editMode) {
                self.$el.find(".oe_multi_category_slider").on("click", _.bind(self.multi_category_slider, self));
            }
        },

        drop_and_build_snippet: function() {
            var self = this;
            this._super();
            if (this.multi_category_slider()) {
                this.multi_category_slider().fail(function() {
                    self.editor.on_remove();
                });
            }
        },

        clean_for_save: function() {
            $('.oe_multi_category_slider').empty();
        },

        multi_category_slider: function(type, value) {
            var self = this;
            if (type == "click" || type == undefined) {
                self.$modal = $(qweb.render("modifier_honos_theme.multi_featured_category_slider_block"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $slider_type = self.$modal.find("#slider_type");
                var $category_slider_cancel = self.$modal.find("#cancel");
                var $snippnet_submit = self.$modal.find("#multi_tabs_submit");
                
                ajax.jsonRpc('modifier_honos_theme/product_get_options', 'call', {}).done(function(res) {
                    $("select[id='slider_type'] option").remove();
                    _.each(res, function(y) {
                        $("select[id='slider_type']").append($('<option>', {
                            value: y["id"],
                            text: y["name"]
                        }));
                    });
                });

                $snippnet_submit.on('click', function() {
                    self.$target.attr('data-multi-cat-slider-type', $slider_type.val());
                    self.$target.attr('data-multi-cat-slider-id', 'multi-cat-myowl-' + $slider_type.val());
                    if ($('select#slider_type').find(":selected").text()) {
                        var type = '';
                        type = _t($('select#slider_type').find(":selected").text());
                    } else {
                        var type = '';
                        type = _t("Multi Category Slider");
                    }
                    self.$target.empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="fancy"> ' + type + '</h3>\
                                                    </div>\
                                                </div>');
                    console.log("finallly check value", self.$target.attr('data-multi-cat-slider-type'));
                });
                $category_slider_cancel.on('click', function() {
                    self.editor.on_remove($.Event("click"))
                })
            } else {
                return;
            }
        },
    });
    
    // for new arrival snippet options code
    options.registry.new_arrival = options.Class.extend({

        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("hidden");
            this.$target.find('.oe_multi_arrival_slider').empty();
            if (!editMode) {
                self.$el.find(".oe_multi_arrival_slider").on("click", _.bind(self.multi_arrival_slider, self));
            }
        },

        drop_and_build_snippet: function() {
            var self = this;
            this._super();
            if (this.multi_arrival_slider()) {
                this.multi_arrival_slider().fail(function() {
                    self.editor.on_remove();
                });
            }
        },

        clean_for_save: function() {
            $('.oe_multi_arrival_slider').empty();
        },

        multi_arrival_slider: function(type, value) {
            var self = this;
            if (type == "click" || type == undefined) {
                self.$modal = $(qweb.render("modifier_honos_theme.multi_featured_new_arrival_slider_block"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $slider_type = self.$modal.find("#slider_arrival_type");
                var $category_slider_cancel = self.$modal.find("#cancel");
                var $snippnet_submit = self.$modal.find("#multi_tabs_arrival_submit");
                
                ajax.jsonRpc('modifier_honos_theme/new_arrival_get_options', 'call', {}).done(function(res) {
                    $("select[id='slider_arrival_type'] option").remove();
                    _.each(res, function(y) {
                        $("select[id='slider_arrival_type']").append($('<option>', {
                            value: y["id"],
                            text: y["name"]
                        }));
                    });
                });

                $snippnet_submit.on('click', function() {
                    self.$target.attr('data-multi-arrival-slider-type', $slider_type.val());
                    self.$target.attr('data-multi-arrival-slider-id', 'multi-arrival-myowl-' + $slider_type.val());
                    if ($('select#slider_arrival_type').find(":selected").text()) {
                        var type = '';
                        type = _t($('select#slider_arrival_type').find(":selected").text());
                    } else {
                        var type = '';
                        type = _t("Multi New Arrival Products Slider");
                    }
                    self.$target.empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="fancy"> ' + type + '</h3>\
                                                    </div>\
                                                </div>');
                });
                $category_slider_cancel.on('click', function() {
                    self.editor.on_remove($.Event("click"))
                })
            } else {
                return;
            }
        },
    });
});