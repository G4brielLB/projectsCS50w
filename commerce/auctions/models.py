from django.contrib.auth.models import AbstractUser
from django.db import models

CATEGORY_CHOICES = [
    ("Fashion", "Fashion"),
    ("Toys", "Toys"),
    ("Electronics", "Electronics"),
    ("Home", "Home"),
    ("Books", "Books"),
    ("Sports", "Sports"),
    ("Music", "Music"),
    ("Art", "Art"),
    ("Collectibles", "Collectibles"),
    ("Automotive", "Automotive"),
    ("Jewelry", "Jewelry"),
    ("Health and Beauty", "Health and Beauty"),
    ("Food and Drink", "Food and Drink"),
    ("Travel", "Travel"),
    ("Services", "Services"),
    ("Education", "Education"),
    ("Garden & Outdoor", "Garden & Outdoor"),
    ("Gaming", "Gaming"),
    ("Furniture", "Furniture"),
    ("Pets", "Pets"),
    ("Technology", "Technology"),
    ("Other", "Other")
]

class User(AbstractUser):
    watchlist = models.ManyToManyField("AuctionListing", blank=True, related_name="watchlisted_by")

class AuctionListing(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(blank=True)
    category = models.CharField(max_length=64, choices=CATEGORY_CHOICES, default="Other")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.category})"
    
    @property
    def highest_bid(self):
        # Return the Bid object with the highest amount for this listing
        return self.bids.order_by("-amount").first()

class Bid(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="bids")
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.amount} by {self.bidder} for {self.listing}"

class Comment(models.Model):
    text = models.TextField()
    listing = models.ForeignKey(AuctionListing, on_delete=models.CASCADE, related_name="comments")
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.commenter} commented on {self.listing}"
