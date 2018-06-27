#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# author: Gao Shao Yang

from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import login, authenticate, logout
from django.urls import reverse

def acc_login(request):
    '''登陆'''
    errors = {}
    if request.method == "POST":
        _email = request.POST.get("email")
        _password = request.POST.get("password")

        user = authenticate(username=_email, password=_password)  # 认证用户名，密码，返回对象

        print("auth res:", user)

        if user:
            login(request, user)  # 将该用户存到session中
            next_url = request.GET.get("next", "/")
            return redirect(next_url)
        else:
            errors["error"] = "错误的用户名或密码"


    return render(request, "login.html", {"errors": errors})


def acc_logout(request):
    '''注销'''
    logout(request)

    return redirect(reverse("acc_login"))