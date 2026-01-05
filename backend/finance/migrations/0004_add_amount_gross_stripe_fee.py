# Generated manually for Fee-Aware Financial Segregation
# Date: 2025-01-05

from django.db import migrations, models
from django.core.validators import MinValueValidator
from decimal import Decimal


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0003_alter_escrowcontract_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='wallettransaction',
            name='amount_gross',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                help_text='Montant brut (avant frais Stripe)',
                max_digits=12,
                null=True,
                validators=[MinValueValidator(Decimal('0.01'))]
            ),
        ),
        migrations.AddField(
            model_name='wallettransaction',
            name='stripe_fee',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                default=Decimal('0'),
                help_text='Part des frais Stripe allouée à cette transaction (proportionnelle)',
                max_digits=12,
                null=True,
                validators=[MinValueValidator(Decimal('0'))]
            ),
        ),
    ]
