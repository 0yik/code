odoo.define('pos_in_indonesian.TranslationDataBase', function (require) {
    var Translate = require('web.translation');

    Translate.TranslationDataBase.include({
        load_translations: function(session, modules, lang) {
            if (lang == 'en_US'){
                lang = 'id_ID';
            }
            return this._super(session, modules, lang);
        }
    });
});
