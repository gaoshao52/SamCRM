

def table_filter(request, admin_class):
    filer_condition = {}
    for k, v in request.GET.items():
        if k == "page":
            continue
        if v:
            filer_condition[k] = v

    return admin_class.model.objects.filter(**filer_condition), filer_condition