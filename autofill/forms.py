from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import *
from crispy_forms.bootstrap import *

from autofill.models import AutoFill
from autofill.forms_constants import *

class AutoFillForm(forms.Form):
        
    def _query_autofill(self, user_id):
        query = AutoFill.objects.all().filter(user_id=user_id)
        self.saved_settings = {}
        for row in query:
            if row.field in FIELDS:
                self.saved_settings[row.field] = row.value
        
            
    def __init__(self, user_id, *args, **kwargs):
        self._query_autofill(user_id)
        super(AutoFillForm, self).__init__(*args, **kwargs)
        for id in FIELD_ORDER:
            value = self.saved_settings[id] if id in self.saved_settings else ''
            widget_attrs = {
                'placeholder':FIELDS[id][1],
                'value':value,
            }
            attributes = {                    
                'label':FIELDS[id][0],            
                'required':False,
            }
            
            if id.endswith('_email'):
                attributes['widget'] = forms.EmailInput(attrs=widget_attrs)
                self.fields[id] = forms.EmailField(**attributes)
            elif id.endswith('_link'):
                attributes['widget'] = forms.URLInput(attrs=widget_attrs)
                self.fields[id] = forms.URLField(**attributes)
            else:
                attributes['widget'] = forms.TextInput(attrs=widget_attrs)
                self.fields[id] = forms.CharField(**attributes)
                
        self.helper = FormHelper()
        self.helper.form_method = 'POST'
        self.helper.form_id = 'autofill'
        self.helper.form_class = ''
        self.helper.form_action = ''
        self.helper.layout = Layout()

        # TODO figure out why len() is not working, I have to manually set 
        #      values to get it to work
        self.helper.layout.extend(self.fields)
        self.helper.layout.insert(0, 'Project Information')
        self.helper[0:8].wrap_together(Tab)
        self.helper.layout.insert(1, 'Publication Information')
        self.helper[1:4].wrap_together(Tab)
        self.helper.layout.insert(2, 'Organism Information')
        self.helper[2:6].wrap_together(Tab)
        
        self.helper[0:3].wrap_together(TabHolder)
        self.helper.add_input(Submit('submit', 'Save Changes'))
  
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
