from django import forms
from django.contrib.auth.models import User

from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_forms.bootstrap import *

from autofill.models import AutoFill

class AutoFillForm(forms.Form):

    class Meta:
        model = AutoFill
        fields = ('user', 'field', 'value')       
        
    def _query_autofill(self, user_id):
        query = AutoFill.objects.all().filter(user_id=user_id)
        self.saved_settings = {}
        for row in query:
            self.saved_settings[row.field] = row.value
        
            
    def __init__(self, user_id, *args, **kwargs):
        self._query_autofill(user_id)
        offset = 'col-sm-offset-1 col-md-offset-1'
        two_cols = 'col-sm-5 col-md-5 {0}'.format(offset)
        FIELDS = {
            'contact_name':['Contact Name', 'Robert Petit'],
            'contact_email':['Contact Email',
                             'usa300@staphopia.com'],
            'contact_link':['Contact Link',
                            'www.staphopia.com/contact/'],
            'sequencing_center':['Sequencing Center', 
                                 'Emory Integrated Genomics Core'],
            'sequencing_center_link':['Sequencing Center Link',
                                      'eigc.emory.edu'],
            'sequencing_center_location':['Sequencing Center Location',
                                          'Atlanta, GA'],
            'isolation_country':['Isolation Country', 'United States'],
            'isolation_city':['Isolation City', 'Atlanta'],
            'isolation_region':['Isolation Region', 'Georgia'],
            'funding_agency':['Funding Agency', 'NIH'],
            'funding_agency_link':['Funding Agency Link', 'www.nih.gov'],
            'sequencing_libaray_method':['Sequencing Library Method', 
                                         'Standard MinION protocol'],
        }
        
        super(AutoFillForm, self).__init__(*args, **kwargs)
        for id in sorted(FIELDS.iterkeys()):
            value = self.saved_settings[id] if id in self.saved_settings else ''
            attributes = {                    
                'label':FIELDS[id][0],            
                'required':False,
                'widget':forms.TextInput(attrs={'placeholder':FIELDS[id][1],
                                                'value':value}),
            }
            if id.endswith('_email'):
                self.fields[id] = forms.EmailField(**attributes)
            elif id.endswith('_link'):
                self.fields[id] = forms.URLField(**attributes)
            else:
                self.fields[id] = forms.CharField(**attributes)
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.form_id = 'autofill'
        self.helper.form_class = ''
        self.helper.form_action = ''
        self.helper.layout = Layout()
        self.helper.layout.extend(self.fields)
        self.helper[0:6].wrap_together(Div, css_class="row")
        self.helper[1:7].wrap_together(Div, css_class="row")
        self.helper[0].wrap_together(Div, css_class=two_cols)
        self.helper[1].wrap_together(Div, css_class=two_cols)
        self.helper.add_input(Submit('submit', 'Save Changes', css_class=offset))
        self.helper.add_input(Button('cancel', 'Cancel'))
  
    def save(self, user_id, POST, *args, **kwargs):
        results = []
        ignore = ['submit', 'csrfmiddlewaretoken']
        for field, value in POST.items():
            if field not in ignore:
                autofill = AutoFill(user_id=user_id, field=field, value=value)
                try:
                    query = AutoFill.objects.get(user_id=user_id, field=field)
                except AutoFill.DoesNotExist:
                    query = None
                    
                if query:
                    if query.pk:
                        autofill.id=query.pk
                        if not value:
                            results.append(autofill.delete())
                        elif value != query.value:
                            results.append(autofill.save(update_fields=['value']))
                        else:
                            results.append('{0} values are identical, did not update.'.format(field))
                elif value:
                    results.append(autofill.save())
                else:
                    results.append('{0} not in db, did not delete.'.format(field))
        return results
