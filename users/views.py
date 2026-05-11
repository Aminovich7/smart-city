from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Operator

@login_required
def operator_dashboard(request):
    try:
        operator = request.user.operator
    except Operator.DoesNotExist:
        messages.error(request, "Siz operator emassiz!")
        return redirect('login')

    context = {
        'operator': operator,  #operatorlar
        'department': operator.department, #operatorning bo'limi
        'incidents_count': operator.assigned_incidents_count, #operator vazifalar soni
    }
    return render(request, 'dashboard/operator.html', context)


@login_required
def assign_task_to_me(request):
    if hasattr(request.user, 'operator'):
        operator = request.user.operator
        operator.assigned_incidents_count += 1
        operator.save()
        messages.success(request, "Yang vazifa Muavfaqiyatli biriktirldi!")
    else:
        messages.error(request, "Faqat operator vazifani qabul qiladi")
    
    return redirect('operator_dashboard')
    
@login_required
def complete_task(request):
    try:
        operator = request.user.operator
        if operator.assigned_incidents_count > 0:
            operator.assigned_incidents_count -= 1
            operator.save()
            messages.success(request, "Vazifa yakunlandi!")
        else:
            messages.warning(request, "Sizda joriy vazifalar mavjud emas.")
        return redirect('operator_dashboard')
    except Operator.DoesNotExist:
        messages.error(request, "Siz operator emassiz.!")
        return redirect('home')
    


@login_required
def department_colleagues(request):
    try:
        user_operator = request.user.operator
        colleagues = Operator.objects.filter(
            department=user_operator.department
        ).exclude(id=user_operator.id)
        
        return render(request, 'dashboard/colleagues.html', {
            'colleagues': colleagues,
            'department': user_operator.department
        })
    except Operator.DoesNotExist:
        messages.error(request, "Siz operator emassiz.!")
        return redirect('home')
