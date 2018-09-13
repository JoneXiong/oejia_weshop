# coding=utf-8

import logging
import datetime

import psycopg2
from odoo import models, fields, api
from odoo import exceptions
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class CustomModel:

    _formatted_name = None
    _formatted_name_fields = []
    _rec_name = None

    @api.multi
    def name_get(self):
        """ name_get() -> [(id, name), ...]

        Returns a textual representation for the records in ``self``.
        By default this is the value of the ``display_name`` field.

        :return: list of pairs ``(id, text_repr)`` for each records
        :rtype: list(tuple)
        """
        result = []
        name = self._rec_name
        if self._formatted_name and self._formatted_name_fields:
            for record in self:
                convert_to_display_name_list = []
                for each_field in self._formatted_name_fields:
                    convert_to_display_name_list.append(self._fields[each_field].convert_to_display_name(
                        record[each_field], record))
                result.append((record.id, self._formatted_name.format(*convert_to_display_name_list)))
        else:
            if name in self._fields:
                convert = self._fields[name].convert_to_display_name
                for record in self:
                    result.append((record.id, convert(record[name], record)))
            else:
                for record in self:
                    result.append((record.id, "%s,%s" % (record._name, record.id)))

        return result

    @api.model
    def load(self, fields, data):
        """
        Attempts to load the data matrix, and returns a list of ids (or
        ``False`` if there was an error and no id could be generated) and a
        list of messages.

        The ids are those of the records created and saved (in database), in
        the same order they were extracted from the file. They can be passed
        directly to :meth:`~read`

        :param fields: list of fields to import, at the same index as the corresponding data
        :type fields: list(str)
        :param data: row-major matrix of data to import
        :type data: list(list(str))
        :returns: {ids: list(int)|False, messages: [Message]}
        """
        # determine values of mode, current_module and noupdate
        mode = self._context.get('mode', 'init')
        current_module = self._context.get('module', '')
        noupdate = self._context.get('noupdate', False)

        # add current module in context for the conversion of xml ids
        self = self.with_context(_import_current_module=current_module)

        cr = self._cr
        cr.execute('SAVEPOINT model_load')

        fields = map(models.fix_import_export_id_paths, fields)
        fg = self.fields_get()

        ids, messages = [], []
        ModelData = self.env['ir.model.data']
        ModelData.clear_caches()
        extracted = self._extract_records(fields, data, log=messages.append)
        converted = self._convert_records(extracted, log=messages.append)
        for id, xid, record, info in converted:
            try:
                cr.execute('SAVEPOINT model_load_save')
            except psycopg2.InternalError as e:
                # broken transaction, exit and hope the source error was
                # already logged
                if not any(message['type'] == 'error' for message in messages):
                    messages.append(dict(info, type='error', message=u"Unknown database error: '%s'" % e))
                break
            try:
                ids.append(ModelData._update(self._name, current_module, record, mode=mode,
                                             xml_id=xid, noupdate=noupdate, res_id=id))
                cr.execute('RELEASE SAVEPOINT model_load_save')
            except psycopg2.Warning as e:
                messages.append(dict(info, type='warning', message=str(e)))
                cr.execute('ROLLBACK TO SAVEPOINT model_load_save')
            except psycopg2.Error as e:
                messages.append(dict(info, type='error', **models.PGERROR_TO_OE[e.pgcode](self, fg, info, e)))
                # Failed to write, log to messages, rollback savepoint (to
                # avoid broken transaction) and keep going
                cr.execute('ROLLBACK TO SAVEPOINT model_load_save')
            # -*- 增加ValidationError类型的异常捕获用于显示自定义的验证错误 -*-
            except exceptions.ValidationError as e:
                messages.append(dict(info, type='error', message=e.name))
                # Failed for some reason, perhaps due to invalid data supplied,
                # rollback savepoint and keep going
                cr.execute('ROLLBACK TO SAVEPOINT model_load_save')
            except Exception as e:
                message = (_('Unknown error during import:') + ' %s: %s' % (type(e), unicode(e)))
                moreinfo = _('Resolve other errors first')
                messages.append(dict(info, type='error', message=message, moreinfo=moreinfo))
                # Failed for some reason, perhaps due to invalid data supplied,
                # rollback savepoint and keep going
                cr.execute('ROLLBACK TO SAVEPOINT model_load_save')
        if any(message['type'] == 'error' for message in messages):
            cr.execute('ROLLBACK TO SAVEPOINT model_load')
            ids = False

        if ids and self._context.get('defer_parent_store_computation'):
            self._parent_store_compute()

        return {'ids': ids, 'messages': messages}

    @api.model
    def batch_create(self, vals_list):
        """
        注意！这个批量创建只适用于没有使用inherit继承其他模型的模型
        :param vals_list:
        :return:
        """
        # low-level implementation of batch_create()
        if not vals_list:
            return False

        if self.is_transient():
            self._transient_vacuum()

        query_list = []
        query_args = []

        for vals in vals_list:
            # data of parent records to create or update, by model
            tocreate = {
                parent_model: {'id': vals.pop(parent_field, None)}
                for parent_model, parent_field in self._inherits.iteritems()
            }

            # list of column assignments defined as tuples like:
            #   (column_name, format_string, column_value)
            #   (column_name, sql_formula)
            # Those tuples will be used by the string formatting for the INSERT
            # statement below.
            updates = [
                ('id', "nextval('%s')" % self._sequence),
            ]

            upd_todo = []
            unknown_fields = []
            protected_fields = []
            for name, val in vals.items():
                field = self._fields.get(name)
                if not field:
                    unknown_fields.append(name)
                    del vals[name]
                elif field.inherited:
                    tocreate[field.related_field.model_name][name] = val
                    del vals[name]
                elif not field.store:
                    del vals[name]
                elif field.inverse:
                    protected_fields.append(field)
            if unknown_fields:
                _logger.warning('No such field(s) in model %s: %s.', self._name, ', '.join(unknown_fields))

            # create or update parent records
            for parent_model, parent_vals in tocreate.iteritems():
                parent_id = parent_vals.pop('id')
                if not parent_id:
                    parent_id = self.env[parent_model].create(parent_vals).id
                else:
                    self.env[parent_model].browse(parent_id).write(parent_vals)
                updates.append((self._inherits[parent_model], '%s', parent_id))

            # set boolean fields to False by default (to make search more powerful)
            for name, field in self._fields.iteritems():
                if field.type == 'boolean' and field.store and name not in vals:
                    vals[name] = False

            # determine SQL values
            for name, val in vals.iteritems():
                field = self._fields[name]
                if field.store and field.column_type:
                    updates.append((name, field.column_format, field.convert_to_column(val, self)))
                else:
                    upd_todo.append(name)

                if hasattr(field, 'selection') and val:
                    self._check_selection_field_value(name, val)

            if self._log_access:
                updates.append(('create_uid', '%s', self._uid))
                updates.append(('write_uid', '%s', self._uid))
                updates.append(('create_date', "(now() at time zone 'UTC')"))
                updates.append(('write_date', "(now() at time zone 'UTC')"))

            # insert a row for this record
            query = """INSERT INTO "%s" (%s) VALUES(%s) RETURNING id""" % (
                self._table,
                ', '.join('"%s"' % u[0] for u in updates),
                ', '.join(u[1] for u in updates),
            )
            query_list.append(query)
            query_args += [u[2] for u in updates if len(u) > 2]

        cr = self._cr
        cr.execute(';\n'.join(query_list) + ';', query_args)

        # from now on, self is the new record
        # id_new, = cr.fetchone()

        id_new_list = [r[0] for r in cr.fetchall()]
        # vals_dict = dict(zip(id_new_list, vals_list))

        self.check_access_rule('create')
        self.create_workflow()
        return id_new_list

    @api.model
    def merge(self, unique_fields, records, do_nothing=False):
        if not unique_fields:
            raise exceptions.ValidationError("unique_fields can't be None")

        record_fields = set(self._fields.keys()) & set(records[0].keys())
        fields = [f for f in record_fields if f not in unique_fields + ['__last_update', 'display_name', 'id']]
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if do_nothing:
            query = u'INSERT INTO {}{} VALUES {} ON conflict{} DO NOTHING;'.format(
                self._table,
                str(tuple(unique_fields + fields + ['create_uid', 'create_date', 'write_uid', 'write_date'])).replace(
                    '\'', '"'),
                str(tuple(["{%s}" % f for f in unique_fields + fields] +
                          [self.env.uid, now, self.env.uid, now])).replace("'{", '{').replace("}'", '}'),
                str(tuple(unique_fields)).replace('\'', '"'))
        else:
            query = u'INSERT INTO {}{} VALUES {} ON conflict{} DO UPDATE SET {};'.format(
                self._table,
                str(tuple(unique_fields + fields + ['create_uid', 'create_date', 'write_uid', 'write_date'])).replace(
                    '\'', '"'),
                str(tuple(["{%s}" % f for f in unique_fields + fields] +
                          [self.env.uid, now, self.env.uid, now])).replace("'{", '{').replace("}'", '}'),
                str(tuple(unique_fields)).replace('\'', '"'),
                ','.join(["%s={%s}" % (f, f) for f in fields]) + ', write_uid={}, write_date=\'{}\''.format(
                    self.env.uid, now))

        queries = u'\n'.join(
            [query.format(**{k: self.escape_srting(v) for k, v in r.iteritems()}) for r in records]).replace(',)', ')')
        cr = self._cr
        cr.execute(queries)

    def escape_srting(self, arg):
        if arg is None or arg is False:
            return 'Null'
        if isinstance(arg, int):
            return arg

        if isinstance(arg, float):
            return arg

        if isinstance(arg, basestring):
            return '\'%s\'' % arg.replace("'", "''")

        return '\'%s\'' % str(arg)

    @api.multi
    def to_dict(self, fields=None, exclude=None):
        """
        :param fields: list 
        :param exclude: list
        :return: 
        """
        exclude = exclude if exclude is not None else []

        if not fields:
            fields = [f for f in self._fields.keys() if
                      f not in models.MAGIC_COLUMNS + ['__last_update', 'display_name'] + exclude]

        record_dict_list = []
        for each_record in self:
            record_dict = {
                f: each_record.__getattribute__(f) if not isinstance(each_record.__getattribute__(f), models.Model)
                else each_record.get_relative_field_val(f)
                for f in fields}
            record_dict_list.append(record_dict)

        return record_dict_list

    def get_relative_field_val(self, field):
        if isinstance(self._fields[field], fields.Many2one):
            return self.__getattribute__(field).id
        else:
            return self.__getattribute__(field).ids



