# accounts/management/__init__.py
# (empty file)

# accounts/management/commands/__init__.py
# (empty file)

# accounts/management/commands/populate_security_questions.py
from django.core.management.base import BaseCommand
from accounts.models import SecurityQuestion

class Command(BaseCommand):
    help = 'Populate database with default security questions'
    
    def handle(self, *args, **options):
        questions = [
            "What was the name of your first pet?",
            "What is your mother's maiden name?",
            "What city were you born in?",
            "What was the name of your elementary school?",
            "What is your favorite movie?",
            "What was the make of your first car?",
            "What is the name of the street you grew up on?",
            "What was your childhood nickname?",
            "What is your favorite book?",
            "What was the name of your first boss?",
        ]
        
        created_count = 0
        for question_text in questions:
            question, created = SecurityQuestion.objects.get_or_create(
                question=question_text,
                defaults={'is_active': True}
            )
            if created:
                created_count += 1
                self.stdout.write(f"Created: {question_text}")
            else:
                self.stdout.write(f"Already exists: {question_text}")
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} new security questions'
            )
        )