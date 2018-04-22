from django.forms import forms, ModelForm


def create_model_form(request, admin_class):
    '''动态生成model form'''

    class Meta:
        model = admin_class.model
        fields = "__all__"

    attrs = {"Meta": Meta}

    _model_form_class = type("DynamicModelForm", (ModelForm,), attrs)

    return _model_form_class
