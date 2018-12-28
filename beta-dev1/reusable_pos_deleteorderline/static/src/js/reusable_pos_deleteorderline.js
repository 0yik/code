odoo.define('reusable_pos_deleteorderline.reusable_pos_deleteorderline', function(require) {
"use strict";

var Chrome = require('point_of_sale.chrome');

// Delete key bind up, delete selected orderline
Chrome.Chrome.include({
    disable_backpace_back: function() {
       var self = this;
       $(document).on("keydown", function (e) {
           if (e.which === 8 && !$(e.target).is("input, textarea")) {
               e.preventDefault();
           }
           else if (e.which == 46) {
                if (self.pos.gui.get_current_screen() == 'products') {
                    self.pos.gui.screen_instances['products'].order_widget.set_value('remove');
                }
           }
       });
    },
});

});
