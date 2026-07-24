from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django import forms
from django.forms import ModelForm

from .models import User, Listing, CATEGORIES, WatchList, Bid, Comment


class ListingForm(forms.ModelForm):

    class Meta:
        model = Listing
        fields = ('title', 'desc', 'value', 'category', 'imageURL')
        exclude = ('user',)


def index(request):
    openListings = list()
    for l in Listing.objects.all():
        print(l.status.lower())
        if l.status.lower() != "closed":
            openListings.append(l)


    return render(request, "auctions/index.html", {
        "listings": openListings,
        "title": "Active Listings"
    })


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

@login_required(login_url="login")
def create_listing(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        if request.user.is_authenticated:
            if form.is_valid():
                m = form.save(commit=False)
                m.user = request.user
                instance = form.save(commit = False)
                instance.title = form.cleaned_data["title"]
                instance.desc = form.cleaned_data["desc"]
                instance.value = form.cleaned_data["value"]
                if form.cleaned_data["imageURL"] == None:
                    instance.imageURL = "https://upload.wikimedia.org/wikipedia/commons/b/b1/Missing-image-232x150.png"
                form.save()
                return redirect("index")
    else:
        form = ListingForm()
        return render(request, "auctions/new.html", {"form": form},)

def view_listing(request, title):
    listing = Listing.objects.get(title = title)
    category = listing.category

    try:
        watchlist = WatchList.objects.get(user = request.user)
        watchlist_titles = list()

        for i in watchlist.listings.values_list("title"):
            watchlist_titles.append(i[0])
    except:
        watchlist_titles = None

    # try:
    #     bid = Bid.objects.get(user = request.user, listing = listing)
    #     topBidUser = True
    # except:
    #     topBidUser = False

    topBidUser = False
    try:
        if request.user == listing.topBidUser:
            topBidUser = True
    except:
        pass


    try:
        comments = list(Comment.objects.filter(listing = listing))
        comments.reverse()
    except:
        comments = None

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "user": request.user,
        "category": category.title(),
        "watchlist_titles": watchlist_titles,
        "topBidUser": topBidUser,
        "comments": comments,
        "status": listing.status.lower()
    })

def categories(request):
    categories = list()
    for category in CATEGORIES:
        categories.append(category[1])

    return render(request, "auctions/categories.html", {
        "categories": categories
    })

def category_view(request, title):
    categories = Listing.objects.values_list('category')
    listings = Listing.objects.filter(category__iexact = title)
    openListings = list()
    for l in listings:
        if l.status.lower != "closed":
            openListings.append(l)

    return render(request, "auctions/index.html", {
        "title": title,
        "listings": openListings
    })

@login_required(login_url="login")
def addToWatchlist(request):
    if request.method == "POST":
        listing_id = request.POST["listing_id"]
        listing = Listing.objects.get(id=listing_id)
        try:
            watchlist = WatchList.objects.get(user=request.user)
        except:
            watchlist = WatchList.objects.create(user=request.user)

        try:
            watchlist.listings.get(id=listing_id)
            watchlist.listings.remove(listing)
        except:
            watchlist.listings.add(listing)

        return redirect("watchlist")

@login_required(login_url="login")
def watchlist_view(request):
    watchlist = WatchList.objects.get(user=request.user)
    return render(request, "auctions/index.html", {
        "listings": watchlist.listings.all(),
        "title": "Watchlist"
    })

@login_required(login_url="login")
def bid(request):
    if request.method == "POST":
        listing_id = request.POST["listing_id"]
        listing = Listing.objects.get(id=listing_id)
        bid_amount = int(request.POST["bid_amount"])

        if bid_amount > listing.value:
            bid = Bid.objects.create(user=request.user, listing=listing, current_bid=bid_amount)
            listing.value = bid.current_bid
            listing.topBidUser = request.user
            listing.save()
            return redirect("view_listing", title=listing.title)
        #     return render(request, "auctions/listing.html", {
        #         "listing": listing,
        #         "message": "Updated Bid",
        #         "topBidUser": True
        #     })
        else:
            return redirect("invalid_bid_amount", title=listing.title)

@login_required(login_url="login")
def invalid_bid_amount(request, title):
    return render(request, "auctions/invalid_bid_amount.html", {
        "title": title,
    })

@login_required(login_url="login")
def comment(request):
    if request.method == "POST":
        listing_id = request.POST["listing_id"]
        listing = Listing.objects.get(id=listing_id)
        body = request.POST["body"]

        comment = Comment.objects.create(user=request.user, listing=listing, body=body)
        return redirect("view_listing", title=listing.title)

@login_required(login_url="login")
def close_auction_view(request):
    if request.method == "POST":
        listing_id = request.POST["listing_id"]
        listing = Listing.objects.get(id=listing_id)
        if request.user == listing.user:
            print(listing.statusChoices[1][1])
            listing.status = listing.statusChoices[1][1]
            listing.save()
            return redirect("index")
