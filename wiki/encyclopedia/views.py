import random
import markdown2
from django.shortcuts import render, redirect
from django.urls import reverse

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def wiki(request, title):
    if util.get_entry(title) is None:
        return render(request, "encyclopedia/error.html", {
            "error": "The requested page was not found."
        })
    entry = util.get_entry(title)
    # Convert the entry to HTML
    entry = markdown2.markdown(entry)
    return render(request, "encyclopedia/wiki.html", {
        "entry": entry,
        "title": title
    })

def search(request):
    query = request.GET.get('q')
    entries = util.list_entries()
    # Turn the query and entries to lowercase for case-insensitive search
    query = query.title()
    # If the query is an exact match for an entry, redirect to that entry by wiki view
    entry = util.get_entry(query)
    if entry is not None:
        return redirect(reverse('wiki', args=[query]))
    # If the query is not an exact match for an entry, display a list of entries that have the query as a substring
    queries = []
    for entry in entries:
        if query.lower() in entry.lower():
            queries.append(entry)
    return render(request, "encyclopedia/search.html", {
        "queries": queries
    })

def create_new_page(request):
    if request.method == "POST":
        title = request.POST.get('title')
        content = request.POST.get('content')
        entries = util.list_entries()
        if title in entries:
            return render(request, "encyclopedia/error.html", {
                "error": "The page already exists."
            })
        util.save_entry(title, content)
        # Redirect to the new page
        return redirect(reverse('wiki', args=[title]))
    return render(request, "encyclopedia/create_new_page.html")

def random_page(request):
    entries = util.list_entries()
    random_entry = random.choice(entries)
    return redirect(reverse('wiki', args=[random_entry]))

def edit_page(request, title):
    entry = util.get_entry(title)
    if entry is None:
        return render(request, "encyclopedia/error.html", {
            "error": "The requested page was not found."
        })
    if request.method == "POST":
        content = request.POST.get('content')
        util.save_entry(title, content)
        # Redirect to the edited page
        return redirect(reverse('wiki', args=[title]))
    return render(request, "encyclopedia/edit_page.html", {
        "title": title,
        "entry": entry
    })
