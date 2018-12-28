odoo.define('mass_mailing_ext.mass_mailing_ext', function (require) {

var session = require('web.session');
var FieldTextHtml = require('web_editor.backend').FieldTextHtml;

FieldTextHtml.include({
    get_url: function (_attr) {
        var src = this.options.editor_url || "/web_editor/field/html";
        var datarecord = this.get_datarecord();

        var attr = {
            'model': this.view.model,
            'field': this.name,
            'res_id': datarecord.id || '',
            'callback': this.callback
        };
        _attr = _attr || {};

        if (this.options['style-inline']) {
            attr.inline_mode = 1;
        }
        if (this.options.snippets) {
            attr.snippets = this.options.snippets;
        }
        if (this.options.template) {
            attr.template = this.options.template;
        }
        if (!this.get("effective_readonly")) {
            attr.enable_editor = 1;
        }
        if (this.field.translate) {
            attr.translatable = 1;
        }
        // Enable the debug mode always
        if (1) {
            attr.debug = session.debug;
        }

        attr.lang = attr.enable_editor ? 'en_US' : this.session.user_context.lang;

        for (var k in _attr) {
            attr[k] = _attr[k];
        }

        if (src.indexOf('?') === -1) {
            src += "?";
        }

        for (var k in attr) {
            if (attr[k] !== null) {
                src += "&"+k+"="+(_.isBoolean(attr[k]) ? +attr[k] : attr[k]);
            }
        }

        delete datarecord[this.name];
        src += "&datarecord="+ encodeURIComponent(JSON.stringify(datarecord));
        return src;
    },
});

});
