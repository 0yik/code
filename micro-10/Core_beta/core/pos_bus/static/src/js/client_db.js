odoo.define('pos_bus_db', function (require) {

    var db = require('point_of_sale.DB');

    db.include({
        init: function (options) {
            this._super(options);
            this.datas_false = [];
            this.sequence = 1;
        },
        get_datas_false: function () {
            return this.datas_false;
        },
        save_data_false: function (vals) {
            this.sequence += 1
            vals['sequence'] = this.sequence
            this.datas_false.push(vals);
        },
        remove_datas_false: function (sequence) {
            var data_index = _.findIndex(this.datas_false, function (data) {
                if (data) {
                    return data.sequence == sequence;
                }
            });
            if (data_index !== -1) {
                this.datas_false.splice( data_index, 1 );
            }
        }
    });


});