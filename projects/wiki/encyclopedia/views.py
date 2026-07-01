# from django import forms
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
from django.shortcuts import redirect, render

from markdown2 import Markdown
import random

from . import util

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, title):
    entry = util.get_entry(title)
    if entry != None:
        markdowner = Markdown()
        html = markdowner.convert(entry)
        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "html": html
        })
    else:
        # return HttpResponse(f"<h1>404</h1> <br> <h2>No entry named {title} returned</h2>")
        return render(request, "encyclopedia/failed.html", {
            "type": "missing entry",
            "title": title
        })


def search(request):
    q = request.GET.get("q")
    entry = util.get_entry(q)
    if entry != None: 
        return redirect("entry", title=q)
    else:
        return redirect("all", q=q)

def all(request, q):
    matches = []
    for e in util.list_entries():
        next = False
        for c in range(len(e)):
            if next:
                break
            for i in range(len(q)):
                if e[c + i].lower() != q[i].lower():
                    break
                elif i+1 == len(q):
                    matches.append(e)
                    next = True
                    break
    return render(request, "encyclopedia/all.html", {
        "entries": matches
    })

def newPage(request):
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        if title in util.list_entries():
            return render(request, "encyclopedia/failed.html", {
                "type": "already exists",
                "title": title
            })

        util.save_entry(title, content)
        return redirect("entry", title=title)
    else:
        return render(request, "encyclopedia/newPage.html")


def edit(request):
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        util.save_entry(title, content)
        return redirect("entry", title=title)
    title = request.GET.get("title")
    entry = util.get_entry(title)
    if entry != None:
        return render(request, "encyclopedia/edit.html", {
            "title": title,
            "content": entry
        })

def randomEntry(request):
    entries = util.list_entries()
    index = random.randrange(0, len(entries))
    return redirect("entry", title=entries[index])

