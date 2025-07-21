from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, AuctionListing, Bid, Comment
from .forms import AuctionListingForm, BidForm, CommentForm, CloseListingForm

CATEGORIES = [
    "Fashion",
    "Toys",
    "Electronics",
    "Home",
    "Books",
    "Sports",
    "Music",
    "Art",
    "Collectibles",
    "Automotive",
    "Jewelry",
    "Health and Beauty",
    "Food and Drink",
    "Travel",
    "Services",
    "Education",
    "Garden & Outdoor",
    "Gaming",
    "Furniture",
    "Pets",
    "Technology",
    "Other"
]

def index(request):
    listings = AuctionListing.objects.filter(is_active=True)
    return render(request, "auctions/index.html", {"listings": listings})

def categories(request):
    return render(request, "auctions/categories.html", {"categories": CATEGORIES})


def listing_category(request, category):
    listings = AuctionListing.objects.filter(category=category, is_active=True)
    return render(request, "auctions/listing_category.html", {"listings": listings, "category": category})


@login_required
def watchlist(request):
    watchlist = request.user.watchlist.all()
    return render(request, "auctions/watchlist.html", {"watchlist": watchlist})


@login_required
def create_listing(request):
    if request.method == "POST":
        form = AuctionListingForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            starting_bid = form.cleaned_data["starting_bid"]
            image_url = form.cleaned_data["image_url"]
            category = form.cleaned_data["category"]
            
            listing = AuctionListing(title=title, description=description, starting_bid=starting_bid, image_url=image_url, category=category, created_by=request.user)
            listing.save()
            return HttpResponseRedirect(reverse("index"))
    else:
        form = AuctionListingForm()

    return render(request, "auctions/create_listing.html", {"form": form})


def listing(request, listing_id):
    listing = get_object_or_404(AuctionListing, pk=listing_id)
    comment_form = CommentForm()
    bid_form = BidForm()
    bids = Bid.objects.filter(listing=listing)
    # Bids sorted by amount in descending order
    bids = bids.order_by("-amount")
    if request.method == "POST":
        if "close_listing" in request.POST:
            if request.user == listing.created_by:
                listing.is_active = False
                listing.save()
                return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
            else:
                return HttpResponseForbidden("You are not authorized to close this listing.")
        elif "place_bid" in request.POST:
            bid_form = BidForm(request.POST)
            if bid_form.is_valid():
                amount = bid_form.cleaned_data["amount"]
                if amount > listing.starting_bid and (listing.highest_bid is None or amount > listing.highest_bid.amount):
                    bid = Bid(amount=amount, listing=listing, bidder=request.user)
                    bid.save()
                    listing.highest_bid_amount = amount
                    listing.save()
                    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
                else:
                    bid_form.add_error("amount", "Bid must be greater than the starting bid and any other bids.")
        elif "add_comment" in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                text = comment_form.cleaned_data["text"]
                comment = Comment(text=text, listing=listing, commenter=request.user)
                comment.save()
                return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
        elif "watchlist_remove" in request.POST:
            request.user.watchlist.remove(listing)
            return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
        elif "watchlist_add" in request.POST:
            request.user.watchlist.add(listing)
            return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "bid_form": bid_form,
        "comment_form": comment_form})


@login_required
def bid(request, listing_id):
    pass


@login_required
def comment(request, listing_id):
    pass


@login_required
def close_listing(request, listing_id):
    pass




def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
