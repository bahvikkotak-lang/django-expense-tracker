from django.shortcuts import render, redirect, get_object_or_404
from .models import Transaction
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.db.models import Sum
from django.db.models.functions import TruncMonth


# ---------------- HOME ----------------
@login_required
def home(request):

    if request.method == "POST":
        title = request.POST.get("title")
        amount = request.POST.get("amount")
        t_type = request.POST.get("type")

        if title and amount:
            Transaction.objects.create(
                user=request.user,
                title=title,
                amount=float(amount),
                transaction_type=t_type
            )
        return redirect('home')

    transactions = Transaction.objects.filter(user=request.user).order_by('-date')

    income = transactions.filter(transaction_type='income').aggregate(Sum('amount'))['amount__sum'] or 0
    expense = transactions.filter(transaction_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
    balance = income - expense

    # Monthly summary
    monthly_data = (
        transactions
        .annotate(month=TruncMonth('date'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('-month')
    )

    context = {
        'transactions': transactions,
        'income': income,
        'expense': expense,
        'balance': balance,
        'monthly_data': monthly_data,
    }

    return render(request, 'tracker/home.html', context)


# ---------------- DELETE ----------------
@login_required
def delete_transaction(request, id):
    transaction = get_object_or_404(Transaction, id=id, user=request.user)
    transaction.delete()
    return redirect('home')


# ---------------- EDIT ----------------
@login_required
def edit_transaction(request, id):
    transaction = get_object_or_404(Transaction, id=id, user=request.user)

    if request.method == "POST":
        transaction.title = request.POST.get("title")
        transaction.amount = float(request.POST.get("amount"))
        transaction.transaction_type = request.POST.get("type")
        transaction.save()
        return redirect('home')

    return render(request, 'tracker/edit.html', {'transaction': transaction})



# ---------------- REGISTER ----------------
def register_view(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()

    return render(request, 'tracker/register.html', {'form': form})
