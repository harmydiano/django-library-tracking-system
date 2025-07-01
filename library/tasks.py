from celery import shared_task
from .models import Loan
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone

@shared_task
def send_loan_notification(loan_id):
    try:
        loan = Loan.objects.get(id=loan_id)
        member_email = loan.member.user.email
        book_title = loan.book.title
        send_mail(
            subject='Book Loaned Successfully',
            message=f'Hello {loan.member.user.username},\n\nYou have successfully loaned "{book_title}".\nPlease return it by the due date.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[member_email],
            fail_silently=False,
        )
    except Loan.DoesNotExist:
        pass

@shared_task
def check_overdue_loans():
    today = timezone.now().date()

    try:

        over_due_loans = Loan.objects.filter(
            due_date__lt= today,
            is_returned = False
        ).select_relate('book', 'member__user')

        for loan in over_due_loans:
            overdue_days = (today - loan.due_date).days

            subject = "Book overdue"
            message = f""" 
                Dear '{loan.member.user.username}', the book 
                '{loan.book.title}
                you 
                borrowed from the library is overdue by '{overdue_days}'
                kindly return the book to the library 
            """
            send_mail(
                subject = subject,
                message = message,
                from_email = settings.DEFAULT_FROM_EMAIL,
                recipient_list = [loan.member.user.email],
                fail_silently = False
            )
    except Exception as e:
        print(f" Error sending mail '{e}' ")