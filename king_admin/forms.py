from django.forms import forms, ModelForm
from django.forms import ValidationError
from django.utils.translation import ugettext as _


def create_model_form(request, admin_class):
    '''动态生成model form'''

    def __new__(cls, *args, **kwargs):   # 动态添加属性
        # cls.base_fields['qq'].widget.attrs["class"] = "form-control"
        for field_name, field_obj in cls.base_fields.items():
            field_obj.widget.attrs["class"] = "form-control"

            # disable field for web

            if not hasattr(admin_class, "is_add_form"):  # add form
                if field_name in admin_class.readonly_fields:
                    field_obj.widget.attrs["disabled"] = "disabled"

            # field validation
            if hasattr(admin_class, "clean_%s"%field_name):
                field_clean_func = getattr(admin_class, "clean_%s"%field_name)
                setattr(cls, "clean_%s"%field_name, field_clean_func)



        return ModelForm.__new__(cls)

    def default_clean(self):
        '''给所有的form添加一个clean验证'''
        # print("------running default clean", self)

        error_list = []
        if self.instance.id:
            for field in admin_class.readonly_fields:
                field_val = getattr(self.instance, field)  # value in db


                if hasattr(field_val, "select_related"): # m2m
                    m2m_obj = getattr(field_val, "select_related")()
                    m2m_values = [i[0] for i in m2m_obj.values_list("id")]
                    set_m2m_values = set(m2m_values)

                    field_val_from_frontend = self.cleaned_data[field]  # in web
                    field_val_from_frontend_list = [i[0] for i in field_val_from_frontend.values_list("id")]
                    set_field_val_from_frontend = set(field_val_from_frontend_list)

                    if set_m2m_values != set_field_val_from_frontend:
                        # error_list.append(ValidationError(
                        #     _('Field %(field)s is readonly'),
                        #     code="invalid",
                        #     params={
                        #         'field': field,
                        #     }
                        # ))
                        self.add_error(field, "readonly")

                    continue

                field_val_from_frontend = self.cleaned_data[field] # in web

                if field_val != field_val_from_frontend:
                    error_list.append(ValidationError(
                        _('Field %(field)s is readonly, value must be %(val)s'),
                        code="invalid",
                        params={
                            'field': field,
                            'val': field_val,
                        }
                    ))

        # readonly_table check
        if admin_class.readonly_table:
            raise ValidationError(
                        _('Table is readonly, cannot be modified or added'),
                        code="invalid",
                    )

        # 用户自定制的验证
        self.ValidationError = ValidationError
        response = admin_class.default_form_validation(self)
        if response:
            error_list.append(response)

        if error_list:
            raise ValidationError(error_list)




    class Meta:
        model = admin_class.model
        fields = "__all__"
        exclude = admin_class.modelform_exclude_fields

    attrs = {"Meta": Meta}

    _model_form_class = type("DynamicModelForm", (ModelForm,), attrs)

    setattr(_model_form_class, "__new__", __new__)  # 添加__new__方法
    setattr(_model_form_class, "clean", default_clean)
    return _model_form_class
