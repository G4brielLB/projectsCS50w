from django import forms

from .models import AuctionListing, Bid, Comment

class AuctionListingForm(forms.ModelForm):
    class Meta:
        model = AuctionListing
        fields = ["title", "description", "starting_bid", "image_url", "category"]

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ["amount"]
        # Dollar sign as label suffix
        labels = {"amount": "Amount ($)"}

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]

class CloseListingForm(forms.Form):
    confirm_close = forms.BooleanField(label="Confirm close listing", required=True)