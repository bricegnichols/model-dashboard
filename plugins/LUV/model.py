import urlparse

import Pyro4
from flask import request, render_template, redirect
from flask_wtf import Form
from wtforms import validators, StringField, SelectField, SubmitField

from plugins.plugin import Plugin
from plugins.pluginmount import ModelPlugin
from server import forms
from plugins.LUV.luv_config import luv_config_dict

name =     'LUV'
script   = 'plugins/LUV/luv.script'
snapshot = 'plugins/LUV/luv-snapshot.bat'
standard_form_fields = ['project','notes','tag','node', 'submit']

def view_luv_launcher(cls):
    form = LuvLauncherForm()
    # specialform = SpecialForm(form)
    if request.method == 'POST':
        if form.validate():
            # Parse host, so we can build an update URL on the other side
            host_url = urlparse.urlparse(request.url)
            host = host_url.hostname
            if host_url.port: host += ":"+str(host_url.port)

            # Set non-standard plugin form fields
            plugin_inputs = {}
            for field_name, field_value in form.data.iteritems():
                if field_name not in standard_form_fields:
                    plugin_inputs[field_name] = field_value

            tool = Plugin(form.data)
            tool.set_plugin(name=name,
                            script=script,
                            snapshot=snapshot,
                            host=host,
                            plugin_inputs=plugin_inputs)

            # spawn model and redirect to the main index
            tool.run_model(form, config=luv_config_dict)
            return redirect('/')

        else:
            print "invalid form is invalid."

    # if a GET (or any other method) we'll create a blank form
    else:
        form = LuvLauncherForm()

    return render_template('luv.html', user=None, form=form)



class LuvLauncherForm(Form):
    project       = StringField('Project', [validators.InputRequired(), validators.Length(max=50)])

    notes         = StringField('Run notes', [validators.Length(max=512)])

    tag           = StringField('Git Repo tag', [validators.Length(max=512)])

    qc_run_base   = StringField('Comparison Run: Base Name', [validators.Length(max=512)])    

    qc_run_scen   = StringField('Comparison Run: Scenario Name', [validators.Length(max=512)])  

    node          = SelectField(label='Run on', validators=[forms.verify_node_is_free])

    submit        = SubmitField('Start Run')

    # add node dropdown items
    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

        # get list of nodes from nameserver, but don't list nameserver itself
        try:
            all_nodes = Pyro4.locateNS().list().keys()
        except:
            all_nodes = ['Nameserver not found']

        self.node.choices = [(x, x) for x in all_nodes if 'NameServer' not in x]

class Luv(ModelPlugin):
    """ PSRC SoundCast activity-based model plugin """
    title = 'LUV'
    description = "LUV Summaries"
    image = 'img/urbansim.png'
    url = 'http://www.queue-project.org'
    form = LuvLauncherForm
    dbtable = None
    launcher = view_luv_launcher