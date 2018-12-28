odoo.define('livechat_ext.im_livechat', function (require) {
"use strict";

var im_livechat = require('im_livechat.im_livechat');
var bus = require('bus.bus').bus;
var core = require('web.core');
var session = require('web.session');
var time = require('web.time');
var utils = require('web.utils');
var ChatWindow = require('livechat_ext.ChatWindow'); // including the new inherited Window

var _t = core._t;
var QWeb = core.qweb;

var _super_live_chat_button = im_livechat.LivechatButton.prototype;

_super_live_chat_button.load_qweb_template = function(){
    // Adding new Qweb template to live chat window
    var xml_files = ['/mail/static/src/xml/chat_window.xml',
                     '/mail/static/src/xml/thread.xml',
                     '/im_livechat/static/src/xml/im_livechat.xml',
                     '/livechat_ext/static/src/xml/chat_window_ext.xml'];
    var defs = _.map(xml_files, function (tmpl) {
        return session.rpc('/web/proxy/load', {path: tmpl}).then(function (xml) {
            QWeb.add_template(xml);
        });
    });
    return $.when.apply($, defs);
};

_super_live_chat_button.open_chat_window = function (channel) {
    var self = this;
    var options = {
        display_stars: false,
        placeholder: this.options.input_placeholder || "",
    };
    var is_folded = (channel.state === 'folded');
    this.chat_window = new ChatWindow(this, channel.id, channel.display_start_page, channel.name, is_folded, channel.message_unread_counter, options);
    this.chat_window.appendTo($('body')).then(function () {
        self.chat_window.$el.css({right: 0, bottom: 0});
        self.$el.hide();
    });
    this.chat_window.on("close_chat_session", this, function () {
        var input_disabled = this.chat_window.$(".o_chat_composer input").prop('disabled');
        var ask_fb = !input_disabled && _.find(this.messages, function (msg) {
            return msg.id !== '_welcome';
        });
        if (ask_fb) {
            this.chat_window.toggle_fold(false);
            this.ask_feedback();
        } else {
            this.close_chat();
        }
    });
    this.chat_window.on("post_message", this, function (message) {
        self.send_message(message).fail(function (error, e) {
            e.preventDefault();
            return self.send_message(message); // try again just in case
        });
    });
    this.chat_window.on("fold_channel", this, function () {
        this.channel.state = (this.channel.state === 'open') ? 'folded' : 'open';
        // toggle by clicking the chat box header
        var startpage = document.getElementById('chat-start-page');
        if (startpage !== null)
        {
            if (this.channel.state == 'open')
            startpage.style.display  = 'block';
            else
            startpage.style.display = 'none';
        }
        utils.set_cookie('im_livechat_session', JSON.stringify(this.channel), 60*60);
    });
    this.chat_window.thread.$el.on("scroll", null, _.debounce(function () {
        if (self.chat_window.thread.is_at_bottom()) {
            self.chat_window.update_unread(0);
        }
    }, 100));
    this.chat_window.on("start_page_done", this, function () {
        self.render_messages();
    });
    // reloading the screen
    var startpage = document.getElementById('chat-start-page');
    if (startpage !== null)
    {
        if (this.channel.state == 'open')
        startpage.style.display  = 'block';
        else
        startpage.style.display = 'none';
    }
};

_super_live_chat_button.add_message = function (data, options) {
    var msg = {
        id: data.id,
        attachment_ids: data.attachment_ids,
        author_id: data.author_id,
        body: data.body,
        date: moment(time.str_to_datetime(data.date)),
        is_needaction: false,
        is_note: data.is_note,
        customer_email_data: []
    };

    // Compute displayed author name or email
    msg.displayed_author = msg.author_id && msg.author_id[1] || data.email_from || this.options.default_username;

    // Compute the avatar_url
    msg.avatar_src = this.server_url;
    if (msg.author_id && msg.author_id[0]) {
        msg.avatar_src += "/web/image/res.partner/" + msg.author_id[0] + "/image_small";
    } else {
        msg.avatar_src += "/mail/static/src/img/smiley/avatar.jpg";
    }

    if (options && options.prepend) {
        this.messages.unshift(msg);
    } else {
        this.messages.push(msg);
    }
};

});