import babel.messages.pofile
import base64
import csv
import datetime
import functools
import glob
import hashlib
import imghdr
import itertools
import jinja2
import json
import logging
import operator
import os
import re
import sys
import time
import werkzeug.utils
import werkzeug.wrappers
import zlib
from xml.etree import ElementTree
from cStringIO import StringIO
from odoo.addons.web.controllers.main import Binary
from odoo.addons.web.controllers.main import Database
import odoo
import odoo.modules.registry
from odoo.api import call_kw, Environment
from odoo.modules import get_resource_path
from odoo.tools import topological_sort
from odoo.tools.translate import _
from odoo.tools.misc import str2bool, xlwt
from odoo import http
from odoo.http import content_disposition, dispatch_rpc, request, \
					  serialize_exception as _serialize_exception
from odoo.exceptions import AccessError
from odoo.models import check_method_name
def binary_content(xmlid=None, model='ir.attachment', id=None, field='datas', unique=False, filename=None, filename_field='datas_fname', download=False, mimetype=None, default_mimetype='application/octet-stream', env=None):
	return request.registry['ir.http'].binary_content(
		xmlid=xmlid, model=model, id=id, field=field, unique=unique, filename=filename, filename_field=filename_field,
		download=download, mimetype=mimetype, default_mimetype=default_mimetype, env=env)
class Binary(Binary):

	def puzzle(self, image='puzzle.png'):
		addons_path = http.addons_manifest['hm_system']['addons_path']
		return open(os.path.join(addons_path, 'hm_system', 'static', 'src', 'img', image), 'rb').read()

	def placeholder(self, image='placeholder.png'):
		addons_path = http.addons_manifest['web']['addons_path']
		return open(os.path.join(addons_path, 'web', 'static', 'src', 'img', image), 'rb').read()

	@http.route(['/web/image',
		'/web/image/<string:xmlid>',
		'/web/image/<string:xmlid>/<string:filename>',
		'/web/image/<string:xmlid>/<int:width>x<int:height>',
		'/web/image/<string:xmlid>/<int:width>x<int:height>/<string:filename>',
		'/web/image/<string:model>/<int:id>/<string:field>',
		'/web/image/<string:model>/<int:id>/<string:field>/<string:filename>',
		'/web/image/<string:model>/<int:id>/<string:field>/<int:width>x<int:height>',
		'/web/image/<string:model>/<int:id>/<string:field>/<int:width>x<int:height>/<string:filename>',
		'/web/image/<int:id>',
		'/web/image/<int:id>/<string:filename>',
		'/web/image/<int:id>/<int:width>x<int:height>',
		'/web/image/<int:id>/<int:width>x<int:height>/<string:filename>',
		'/web/image/<int:id>-<string:unique>',
		'/web/image/<int:id>-<string:unique>/<string:filename>',
		'/web/image/<int:id>-<string:unique>/<int:width>x<int:height>',
		'/web/image/<int:id>-<string:unique>/<int:width>x<int:height>/<string:filename>'], type='http', auth="public")
	def content_image(self, xmlid=None, model='ir.attachment', id=None, field='datas', filename_field='datas_fname', unique=None, filename=None, mimetype=None, download=None, width=0, height=0):
		status, headers, content = binary_content(xmlid=xmlid, model=model, id=id, field=field, unique=unique, filename=filename, filename_field=filename_field, download=download, mimetype=mimetype, default_mimetype='image/png')
		if status == 304:
			return werkzeug.wrappers.Response(status=304, headers=headers)
		elif status == 301:
			return werkzeug.utils.redirect(content, code=301)
		elif status != 200 and download:
			return request.not_found()

		if content and (width or height):
			# resize maximum 500*500
			if width > 500:
				width = 500
			if height > 500:
				height = 500
			content = odoo.tools.image_resize_image(base64_source=content, size=(width or None, height or None), encoding='base64', filetype='PNG')
			# resize force png as filetype
			headers = self.force_contenttype(headers, contenttype='image/png')
		if content:
			image_base64 = base64.b64decode(content)
		else:
			if model == 'ir.ui.menu':
				image_base64 = self.puzzle(image='puzzle.png')  # could return (contenttype, content) in master
			else:
				image_base64 = self.placeholder(image='placeholder.png')
			headers = self.force_contenttype(headers, contenttype='image/png')

		headers.append(('Content-Length', len(image_base64)))
		response = request.make_response(image_base64, headers)
		response.status_code = status
		return response

	@http.route([
		'/web/binary/company_logo',
		'/logo',
		'/logo.png',
	], type='http', auth="none", cors="*")
	def company_logo(self, dbname=None, **kw):
		imgname = 'logo'
		imgext = '.png'
		placeholder = functools.partial(get_resource_path, 'hm_system', 'static', 'src', 'img')
		uid = None
		if request.session.db:
			dbname = request.session.db
			uid = request.session.uid
		elif dbname is None:
			dbname = db_monodb()

		if not uid:
			uid = odoo.SUPERUSER_ID

		if not dbname:
			response = http.send_file(placeholder(imgname + imgext))
		else:
			try:
				# create an empty registry
				registry = odoo.modules.registry.Registry(dbname)
				with registry.cursor() as cr:
					cr.execute("""SELECT c.logo_web, c.write_date
									FROM res_users u
							   LEFT JOIN res_company c
									  ON c.id = u.company_id
								   WHERE u.id = %s
							   """, (uid,))
					row = cr.fetchone()
					if row and row[0]:
						image_base64 = str(row[0]).decode('base64')
						image_data = StringIO(image_base64)
						imgext = '.' + (imghdr.what(None, h=image_base64) or 'png')
						response = http.send_file(image_data, filename=imgname + imgext, mtime=row[1])
					else:
						response = http.send_file(placeholder('nologo.png'))
			except Exception:
				response = http.send_file(placeholder(imgname + imgext))

		return response

class Database(Database):

   	def _render_template(self, **d):
   	    d.setdefault('manage',True)
   	    d['insecure'] = odoo.tools.config['admin_passwd'] == 'admin'
   	    d['list_db'] = odoo.tools.config['list_db']
   	    d['langs'] = odoo.service.db.exp_list_lang()
   	    d['countries'] = odoo.service.db.exp_list_countries()
   	    # databases list
   	    d['databases'] = []
   	    try:
   	        d['databases'] = http.db_list()
   	    except odoo.exceptions.AccessDenied:
   	        monodb = db_monodb()
   	        if monodb:
   	            d['databases'] = [monodb]
   	    loader = jinja2.PackageLoader('openerp.addons.hm_system', "views")
   	    env = jinja2.Environment(loader=loader, autoescape=True)
   	    return env.get_template("database_manager.html").render(d)

   	@http.route('/web/database/selector', type='http', auth="none")
   	def selector(self, **kw):
   	    return self._render_template(manage=False)

   	@http.route('/web/database/manager', type='http', auth="none")
   	def manager(self, **kw):
   	    return self._render_template()