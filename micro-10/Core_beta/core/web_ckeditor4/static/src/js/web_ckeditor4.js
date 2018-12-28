odoo.define('web_ckeditor4', function (require) {
    "use strict";
    var core = require('web.core');
    var session = require('web.session');
    var Model = require('web.DataModel');
    var common = require('web.form_common');
    var base = require('web_editor.base');
    var editor = require('web_editor.editor');
    var backend = require('web_editor.backend');
    var summernote = require('web_editor.summernote');
    var transcoder = require('web_editor.transcoder');
    var _t = core._t;
    var QWeb = core.qweb;
    var ckeditor_addFunction_org = CKEDITOR.tools.addFunction;
    //this is a quite complicated way to kind of monkey patch the private
    //method onDomReady of ckeditor's plugin wysiwigarea, which causes problems
    //when the editor is about to be destroyed but because of OpenERP's
    //architecture updated one last time with its current value
    CKEDITOR.tools.addFunction = function (fn, scope) {
        if (scope && scope._ && scope._.attrChanges && scope._.detach) {
            var scope_reference = scope;
            return ckeditor_addFunction_org(function () {
                var self = this,
                    self_arguments = arguments;
                setTimeout(function () {
                    if (self.editor) {
                        fn.apply(self, self_arguments);
                    }
                }, 0);
            }, scope);
        }
        return ckeditor_addFunction_org(fn, scope);
    };
    var ckeditor_setTimeout_org = CKEDITOR.tools.setTimeout,
        ckeditor_timeouts = {};
    //we need to collect timeouts in order to cancel them to avoid errors on
    //cleaning up
    CKEDITOR.tools.setTimeout = function (func, milliseconds, scope, args, ownerWindow) {
        if (scope && scope.editor && scope.editor.status == 'destroyed') {
            return 0;
        }
        var result = ckeditor_setTimeout_org.apply(this, arguments);
        if (!ckeditor_timeouts[scope]) {
            ckeditor_timeouts[scope] = [];
        }
        ckeditor_timeouts[scope].push(result);
        return result;
    }

    CKEDITOR.on('dialogDefinition', function (e) {
        _.each(e.data.definition.contents, function (element) {
            if (!element || element.filebrowser != 'uploadButton') {
                return
            }
            _.each(element.elements, function (element) {
                if (!element.onClick || element.type != 'fileButton') {
                    return
                }
                var onClick_org = element.onClick;
                element.onClick = function (e1) {
                    onClick_org.apply(this, arguments);
                    _.each(jQuery('#' + this.domId).closest('table')
                            .find('iframe').contents().find(':file')
                            .get(0).files,
                        function (file) {
                            var reader = new FileReader();
                            reader.onload = function (load_event) {
                                CKEDITOR.tools.callFunction(
                                    e.editor._.filebrowserFn,
                                    load_event.target.result,
                                    '');
                            }
                            reader.readAsDataURL(file);
                        });
                    return false;
                }
            });
        });
    });

    var widget = common.AbstractField.extend(common.ReinitializeFieldMixin);

    function filter_html(value, ckeditor_filter, ckeditor_writer) {
        var fragment = CKEDITOR.htmlParser.fragment.fromHtml(value);
        ckeditor_filter.applyTo(fragment);
        ckeditor_writer.reset();
        fragment.writeHtml(ckeditor_writer);
        return ckeditor_writer.getHtml();
    };

    var default_ckeditor_filter = new CKEDITOR.filter(
        {
            '*': {
                attributes: 'href,src,style,alt,width,height,dir',
                styles: '*',
                classes: '*',
            },
            'html head title meta style body p div span a h1 h2 h3 h4 h5 img br hr table tr th td ul ol li dd dt strong pre b i': true,
        });
    var default_ckeditor_writer = new CKEDITOR.htmlParser.basicWriter();

    var FieldTextHtmlSimple = widget.extend({
        template: 'FieldTextHTMLCkeditor',
        ckeditor_config: {
            removePlugins: 'iframe,flash,forms,smiley,pagebreak,stylescombo',
            filebrowserImageUploadUrl: 'dummy',
            extraPlugins: 'filebrowser,pastebase64',
            entities_additional: '',
        },
        ckeditor_filter: default_ckeditor_filter,
        ckeditor_writer: default_ckeditor_writer,

        start: function () {
            var def = this._super.apply(this, arguments);
            CKEDITOR.lang.load(this.session.user_context.lang.split('_')[0], 'en', function () {
            });
            this.$content.trigger('mouseup');
            return def;
        },
        initialize_content: function () {
            this._super.apply(this, arguments);
            this.$textarea = this.$("textarea").val(this.get('value') || "<p><br/></p>");
            this.$content = $();
            var self = this;
            if (!this.$textarea) {
                return;
            }
            if (this.get("effective_readonly")) {
                this.$content = $('<div class="o_readonly"/>');
            } else {
                this.editor = CKEDITOR.replace(this.$textarea.get(0),
                _.extend(
                    {
                        language: this.session.user_context.lang.split('_')[0],
                        on: {
                            'change': function () {
                                self.store_dom_value();
                            },
                        },
                    },
                    this.ckeditor_config));
            }
        },
        store_dom_value: function () {
            this.internal_set_value(this.editor ? this.editor.getData() : this.web.parse_value(this.get('value'), this));
        },
        filter_html: function (value) {
            return filter_html(value, this.ckeditor_filter, this.ckeditor_writer);
        },
        render_value: function () {
            if (this.get("effective_readonly")) {
                this.$el.html(this.filter_html(this.get('value')));
            }
            else {
                if (this.editor) {
                    var self = this;
                    if (this.editor.status != 'ready') {
                        var instanceReady = function () {
                            self.editor.setData(self.get('value') || '');
                            self.editor.removeListener('instanceReady', instanceReady);
                        };
                        this.editor.on('instanceReady', instanceReady);
                    }
                    else {
                        self.editor.setData(self.get('value') || '');
                    }
                }
            }
        },
        undelegateEvents: function () {
            this._cleanup_editor();
            return this._super.apply(this, arguments);
        },
        _cleanup_editor: function () {
            if (this.editor) {
                this.editor._.editable = null;
                this.editor.destroy(true);
                if (ckeditor_timeouts[this.editor]) {
                    _.each(ckeditor_timeouts[this.editor], function (timeout) {
                        clearTimeout(timeout);
                    });
                    delete ckeditor_timeouts[this.editor];
                }
                this.editor = null;
            }
        },
        destroy: function () {
            this.destroy_content();
            this._super();
        },
        destroy_content: function () {
            this._cleanup_editor();
        }

    });
    core.form_widget_registry
        .add('html', FieldTextHtmlSimple);
    return {
        FieldTextHtmlSimple: FieldTextHtmlSimple,
    };

})