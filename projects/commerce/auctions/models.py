from django.contrib.admin.utils import label_for_field
from django.contrib.auth.models import AbstractUser
from django.db.models.fields.files import ImageField
from django.db import models
from django.db.models.functions.math import Random


CATEGORIES = (
    ("DEFAULT", "Default"),
    ("TECH", "Tech"),
    ("SPORTS", "Sports"),
    ("FURNITURE", "Furniture"),
    ("FASHION", "Fashion"),
    ("TOYS", "Toys"),
    ("HOME", "Home")
)

class User(AbstractUser):
    pass



class Listing(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=100, blank=False)
    desc = models.CharField(max_length=1000, blank=False)
    imageURL = models.URLField(null=False)
    category = models.CharField(choices=CATEGORIES, default=CATEGORIES[0])
    value = models.PositiveIntegerField(null=False)


    def __str__(self):
        return f"{self.title}, Description: {self.desc}, Starting Bid: {self.value}"

class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing_bids", null=True)
    current_bid = models.PositiveIntegerField(null=False)

class WatchList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    listings = models.ManyToManyField(Listing, related_name="watchlist_listings")

    def __str__(self):
        return f"User:{self.user}, listings:{self.listings}" 

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="listing_comments", null=True)
    body = models.TextField(blank=False)
