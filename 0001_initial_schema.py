# Updated 0001_initial_schema.py with PostgreSQL DO block fixes for enum type creation

# Import necessary modules
from django.db import migrations, models

class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='YourModel',
            fields=[
                # Your fields here
            ],
        ),
        # Additional operations
    ]
