from django.shortcuts import render, HttpResponse, redirect
from crm import models
# Create your views here.
from crm import forms
from django.db.utils import IntegrityError
import string, random
from django.core.cache import cache
from django.urls import reverse



def index(request):

    return render(request, "index.html")


def customer_list(request):

    return render(request, "sales/customers.html")



def stu_registration(request, enroll_id, random_str):
    '''客户填写报名信息'''
    status = 0
    if cache.get(enroll_id) == random_str:  # 判断url 时否在生效时间内

        enroll_obj = models.Enrollment.objects.get(id=enroll_id)

        if request.method == "POST":

            if request.is_ajax():

                file_obj = request.FILES.get("file")
                print(request.FILES.get("file"))

                return HttpResponse("图片发送完成")

            # print(request.POST)
            customer_form = forms.CustomerForm(request.POST, instance=enroll_obj.customer)

            # print(customer_form.is_valid())
            if customer_form.is_valid():

                # print(customer_form.cleaned_data)
                customer_form.save()
                enroll_obj.contract_agreed = True
                enroll_obj.save()

                return render(request, "sales/stu_registration.html", {"status": 1})
        else:
            if enroll_obj.contract_agreed:
                status = 1
            else:
                status = 0


            customer_form = forms.CustomerForm(instance=enroll_obj.customer)


        return render(request, "sales/stu_registration.html", {"customer_form": customer_form,
                                                               "enroll_obj": enroll_obj,
                                                               "status": status,
                                                               })
    else:
        return HttpResponse("sb 想黑我")

def enrollment(request, customer_id):
    '''销售填写客户报名班级'''
    enroll_form = forms.EnrollmentForm()

    msgs = {}
    customer_obj = models.Customer.objects.get(id=customer_id)
    random_str = "".join(random.sample(string.ascii_lowercase + string.digits, 8))
    if request.method == "POST":
        enroll_form = forms.EnrollmentForm(request.POST)
        if enroll_form.is_valid():

            msg = '''请将此链接发送给客户填写：
            http://127.0.0.1:8000/crm/customer/registration/{enroll_obj_id}/{random_str}/
            '''
            try:
                enroll_form.cleaned_data['customer'] = customer_obj
                print("cleaned_data:", enroll_form.cleaned_data)
                enroll_obj = models.Enrollment.objects.create(**enroll_form.cleaned_data)

                msgs['msg'] = msg.format(enroll_obj_id=enroll_obj.id, random_str=random_str)
                cache.set(enroll_obj.id, random_str, 20)  # 设置客url的生效时间 为20秒

                # print("obj:", enroll_obj)
            except IntegrityError as e:
                enroll_obj = models.Enrollment.objects.get(customer_id=customer_id, enrolled_class_id=enroll_form.cleaned_data['enrolled_class'].id)
                # print("------>obj", obj)

                if enroll_obj.contract_agreed:  # 学生同意合同
                    return redirect(reverse("contract_review", args=(enroll_obj.id,)))
                    # return redirect("/crm/contract_review/%s/"%enroll_obj.id)



                cache.set(enroll_obj.id, random_str, 20)   # 设置客url的生效时间 为20秒
                msgs['msg'] = msg.format(enroll_obj_id=enroll_obj.id, random_str=random_str)
                enroll_form.add_error("__all__", "该用户信息已经存在")



    return render(request, "sales/enrollment.html", {"enroll_form": enroll_form,
                                                     "customer_obj": customer_obj,
                                                     "msgs": msgs,
                                                     })


def contract_review(request, enroll_id):

    enroll_obj = models.Enrollment.objects.get(id=enroll_id)
    enroll_form = forms.EnrollmentForm(instance=enroll_obj)

    coustomer_form = forms.CustomerForm(instance=enroll_obj.customer)
    return render(request, "sales/contract_review.html", {
                                                  "coustomer_form": coustomer_form,
                                                  "enroll_form": enroll_form,
                                                  "enroll_obj": enroll_obj})

def enrollment_rejection(request, enroll_id):
    enroll_obj = models.Enrollment.objects.get(id=enroll_id)
    enroll_obj.contract_agreed = False
    enroll_obj.save()


    return redirect(reverse("enrollment", args=(enroll_obj.customer.id,)))


def payment(request, enroll_id):
    enroll_obj = models.Enrollment.objects.get(id=enroll_id)

    if request.method == "POST":
        payment_form = forms.PaymentForm(request.POST)

        if payment_form.is_valid():
            enroll_obj.customer.status = 1
            enroll_obj.customer.save()
            # print("payment_form.is_valid->", enroll_obj.customer)
            return redirect("/king_admin/crm/customer/")
        else:
            return render(request, "sales/payment.html", {"enroll_obj": enroll_obj,
                                                          "payment_form": payment_form})

    elif request.method == "GET":
        enroll_obj.contract_approved = True
        enroll_obj.save()

        data_obj = {"customer": enroll_obj.customer_id, "course": enroll_obj.enrolled_class.course_id, "consultant": enroll_obj.consultant_id}
        payment_form = forms.PaymentForm(initial=data_obj)

        return render(request, "sales/payment.html", {"enroll_obj": enroll_obj,
                                                     "payment_form": payment_form})


