from django.db.models.signals import post_save

from users.models import Item, Transaction




def create_transation(sender ,instance , created , **kwargs):
    print(instance.prev_quantity)
    if created :
        activity,pre= 'C',0
    else:
        activity= 'U'
        pre=instance.prev_quantity

    if activity =='C' or instance.quantity - pre != 0: 
        Transaction.objects.create(
            user = instance.folder.user,
            item= instance,
            qty_change = (instance.quantity - pre ) ,
            activity = activity,
        )

        

post_save.connect(create_transation, sender = Item )

