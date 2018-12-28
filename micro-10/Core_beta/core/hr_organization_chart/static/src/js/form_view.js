odoo.define("hr_organization_chart.form_view", function(require) {
    "use strict";

    var FormView = require("web.FormView");
    var Model = require('web.Model');

    FormView.include({

        load_record: function(record) {
            var self = this;
            self._super.apply(this, arguments);
            if (self.model === 'hr.employee') {
                this.append_org_chart(record);
                setInterval(function(){
                 $('a[href="http://getorgchart.com"]').hide();
                }, 0);
            }
            if (self.model === 'hr.department') {
                if(record.manager_id){
                    $("#people").show();
                    new Model('hr.employee').call('read', [[record.manager_id[0]]], { }).then(function (data){
                    self.append_org_chart(data[0]);
                    });
                }else{
                    $("#people").hide();
                }
                setInterval(function(){
                 $('a[href="http://getorgchart.com"]').hide();
                }, 0);
            }
            self.on_form_changed();
        },

        append_org_chart: function(record) {
            var self = this;
            var record_id = record.id;
            var employee = 'employee="' + record_id + '">';
            var $new_div = $('<div id="people" ' + employee);

            var $peopleDiv = self.$el.find('#people');
            var $formSheet = self.$el.find('.o_form_sheet');
            if (!$peopleDiv.length) {
                $peopleDiv = $new_div;
                $peopleDiv.appendTo($formSheet);
            } else if (record_id != $peopleDiv.attr('employee')) {
                $peopleDiv.replaceWith($new_div);
            };
        },

    });
});