odoo.define('stock_card_report.pivot', function (require) {
"use strict";
    var core = require('web.core');
    var session = require('web.session');
    var framework = require('web.framework');
    var crash_manager = require('web.crash_manager');
    var PivotView = require('web.PivotView');

    PivotView.include({
        render_buttons: function ($node) {
            if ($node) {
                this._super($node);
                if (this.model != 'stock.card.report') {
                    this.$buttons.find('.o_pivot_download_pdf').hide();
                }
            }
        },
        on_button_click: function (event) {
            this._super(event);
            var $target = $(event.target);
            if ($target.hasClass('o_pivot_download_pdf')) {
                return this.download_table_pdf();
            }
        },
        download_table_pdf: function () {
            var rows = {}
            var $tbl_trs = this.$el.find('table tr');
            _.each($tbl_trs, function ($ttr, cnt) {
                rows[cnt] = {}
                _.each($ttr.cells, function (cell, cell_index) {
                    var $cell = $(cell);
                    var cell_data = {};
                    cell_data['rowspan'] = $cell.attr('rowspan');
                    cell_data['colspan'] = $cell.attr('colspan');
                    cell_data['style'] = $cell.attr('style');
                    cell_data['text'] = $cell.text();
                    cell_data['is_td'] = $cell.prop('tagName').toLowerCase() == 'td';
                    rows[cnt][cell_index] = cell_data
                })
            })
            session.get_file({
                url: '/web/pivot/export_pdf',
                data: {data: JSON.stringify(rows)},
                complete: framework.unblockUI,
                error: crash_manager.rpc_error.bind(crash_manager)
            });
        },
    });
});