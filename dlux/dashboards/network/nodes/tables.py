# Copyright 2014 Hewlett-Packard Development Company, L.P.
#
# Author: Endre Karlson <endre.karlson@hp.com>
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
from django.core import urlresolvers
from django.utils.translation import ugettext_lazy as _

from horizon import forms
from horizon import tables

from dlux.api import get_client
from dlux.dashboards.network.nodes import get_node
from dlux.utils.filters import keys_as_id

STATES = {0: 'DOWN', 1: 'UP'}


def get_node_link(datum):
    view = "horizon:network:nodes:detail"
    if datum.id:
        link = urlresolvers.reverse(view, args=(datum.type, datum.id,))
    else:
        link = None
    return link


class UpdateCell(tables.UpdateAction):
    def update_cell(self, request, datum, obj_id, cell_name, new_cell_value):
        client = get_client(request)
        node_id, node_type = obj_id.split('#')
        client.nodes.create_property(
            node_type, node_id, cell_name, new_cell_value)


class UpdateRow(tables.Row):
    ajax = True

    def get_data(self, request, string):
        node_id, node_type = string.split('#')

        return get_node(request, node_type, node_id)


class NodesTable(tables.DataTable):
    needs_form_wrapper = True
    id = tables.Column(
        'id', verbose_name=_('Identifier'), link=get_node_link)
    type = tables.Column('type', verbose_name=_('Type'))
    description = tables.Column(
        lambda i: i.description,
        verbose_name=_('Description'),
        form_field=forms.CharField(required=True, widget=forms.Textarea()),
        update_action=UpdateCell)
    mac_address = tables.Column(
        lambda i: i.properties['macAddress']['value'],
        verbose_name=_('Mac Address'))

    class Meta:
        name = 'nodes'
        verbose_name = _('Nodes')
        row_class = UpdateRow

    def get_object_id(self, datum):
        return keys_as_id(datum, keys=['id', 'type'])


class ConnectorTable(tables.DataTable):
    id = tables.Column(
        lambda i: i.nodeconnector['id'],
        verbose_name=_('Identifier'))
    type = tables.Column(
        lambda i: i.nodeconnector['type'],
        verbose_name=_('Type'))
    name = tables.Column(
        lambda i: i.properties['name']['value'],
        verbose_name=_('Name'))
    state = tables.Column(
        lambda i: STATES[i.properties['state']['value']],
        verbose_name=_('State'))

    class Meta:
        name = 'connectortable'
        verbose_name = _('Connectors')

    def get_object_id(self, datum):
        data = datum.nodeconnector
        node = keys_as_id(data['node'], keys=['id', 'type'])
        connector = keys_as_id(data, keys=['id', 'type'])
        return '%s#%s' % (node, connector)
