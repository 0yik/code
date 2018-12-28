from odoo.report import report_sxw
from string import digits


class Parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(Parser, self).__init__(cr, uid, name, context)
        self.context = context
        self.tarif = ""
        self.matrix = {}
        self.total_bruto = 0.00
        self.localcontext.update({
            'get_npwp_wajib_pajak': self._get_npwp_wajib_pajak,
            'get_npwp_pemotong_pajak': self._get_npwp_pemotong_pajak,
            'get_nama_wajib_pajak': self._get_nama_wajib_pajak,
            'get_nama_pemotong_pajak': self._get_nama_pemotong_pajak,
            'get_alamat_wajib_pajak': self._get_alamat_wajib_pajak,
            'compute_matrix_line': self._compute_matrix_line,
            'get_matrix_line': self._get_matrix_line,
            'get_total_bruto': self._get_total_bruto,
            'get_terbilang': self._get_terbilang
        })

    def _get_npwp_wajib_pajak(self, object, index):
        npwp_wajib_pajak = object.wajib_pajak_id.commercial_partner_id.vat
        if npwp_wajib_pajak:
            convert = ''.join(c for c in npwp_wajib_pajak if c in digits)
            if len(convert) > index:
                result = convert[index]
            else:
                result = ""
        else:
            self.tarif = "v"
            result = ""
        return result

    def _get_npwp_pemotong_pajak(self, object, index):
        npwp_pemotong_pajak =\
            object.pemotong_pajak_id.commercial_partner_id.vat
        if npwp_pemotong_pajak:
            convert = ''.join(c for c in npwp_pemotong_pajak if c in digits)
            if len(convert) > index:
                result = convert[index]
            else:
                result = ""
        else:
            result = ""
        return result

    def _get_nama_wajib_pajak(self, object, index):
        nama_wajib_pajak =\
            object.wajib_pajak_id.commercial_partner_id.name
        title_wajib_pajak =\
            object.wajib_pajak_id.commercial_partner_id.title.name
        if title_wajib_pajak:
            wajib_pajak =\
                " ".join([title_wajib_pajak, nama_wajib_pajak])
        else:
            wajib_pajak = nama_wajib_pajak
        if wajib_pajak:
            if len(wajib_pajak) > index:
                result = wajib_pajak[index]
            else:
                result = ""
        else:
            result = ""
        return result

    def _get_nama_pemotong_pajak(self, object, index):
        nama_pemotong_pajak =\
            object.pemotong_pajak_id.commercial_partner_id.name
        title_pemotong_pajak =\
            object.pemotong_pajak_id.commercial_partner_id.title.name
        if title_pemotong_pajak:
            pemotong_pajak =\
                " ".join([title_pemotong_pajak, nama_pemotong_pajak])
        else:
            pemotong_pajak = nama_pemotong_pajak
        if pemotong_pajak:
            if len(pemotong_pajak) > index:
                result = pemotong_pajak[index]
            else:
                result = ""
        else:
            result = ""
        return result

    def _get_alamat_wajib_pajak(self, object, index):
        alamat_wajib_pajak =\
            object.wajib_pajak_id.commercial_partner_id.street
        if alamat_wajib_pajak:
            if len(alamat_wajib_pajak) > index:
                result = alamat_wajib_pajak[index]
            else:
                result = ""
        else:
            result = ""
        return result

    def _compute_matrix_line(self, line_ids):
        value = {}
        if line_ids:
            for line in line_ids:
                self.total_bruto += line.amount
                val_tarif_persen =\
                    (line.tax_id.amount * 100)
                value = {
                    'bruto': line.amount,
                    'tarif': self.tarif,
                    'pph_dipotong': line.amount_tax,
                    'tax_code_name': line.name,
                    'tarif_persen': str(val_tarif_persen) + "%",
                }
                self.matrix[line.sequence] = value

    def _get_matrix_line(self, sequence):
        return self.matrix.get(sequence, {})

    def _get_total_bruto(self):
        if self.total_bruto > 0:
            result = self.total_bruto
        else:
            result = ""
        return result

    def _get_terbilang(self, value):
        obj_amount2text = self.pool.get('base.amount_to_text')
        obj_res_lang = self.pool.get('res.lang')
        obj_res_currency = self.pool.get('res.currency')
        criteria_lang = [('code', '=', 'id_ID')]
        criteria_curr = [('name', '=', 'IDR')]

        lang_id = obj_res_lang.search(self.cr, self.uid, criteria_lang)
        lang = obj_res_lang.browse(self.cr, self.uid, lang_id)

        currency_id = obj_res_currency.search(self.cr, self.uid, criteria_curr)
        currency = obj_res_currency.browse(self.cr, self.uid, currency_id)

        if currency:
            result = obj_amount2text.get(
                self.cr,
                self.uid,
                value,
                currency,
                lang
            )
        else:
            result = '-'
        return result
