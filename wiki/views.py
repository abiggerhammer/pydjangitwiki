# Create your views here.
from django.http import HttpResponse, Http404
from django.template import TemplateDoesNotExist
from django.views.generic.simple import direct_to_template
import django.shortcuts #render_to_response
#import wiki.models
import git
import os.path
from django.conf import settings
import string #for pathIsFile()
import copy

#def about_pages(request, page):
#    try:
#        return direct_to_template(request, template="about/%s.html" % page)
#    except TemplateDoesNotExist:
#        raise Http404()

# TODO: download a single page (not in a compressed archive)
# django request objects: http://docs.djangoproject.com/en/dev/ref/request-response/)

def pop_path(path2):
    '''
    if path is super/star/destroyer, then pop_path will return star/destroyer
    '''
    if (path2.count("/") == 0): return ""
    pieces = string.split(path2, "/")
    pieces.reverse()
    pieces.pop()
    pieces.reverse()
    return string.join(pieces, "/")

def children(path="",sha="",depth=-1,gitpath=""):
    '''
    find all trees and pages and combine them into a dict

    depth=-1 means infinite depth. 
    '''
    if path == "" and gitpath == "": return {}
    if not gitpath: gitpath = settings.REPO_DIR
    repo = git.Repo(gitpath)
    files = repo.tree().items()
    returndict = {}
    for each in files:
        if type(each[1]) == git.tree.Tree:
            #it's a folder
            returndict = dict(returndict, **{str(each[1].name):each[1]})
            if depth<0 or depth>0:
                returndict = dict(returndict, **children(path=pop_path(copy.copy(path)),sha=sha,depth=depth-1))
        elif type(each[1]) == git.blob.Blob:
            #it's a file
            returndict = dict(returndict, **{str(each[1].name):each[1]})
    return returndict

def find(path="",sha="",depth=-1):
    #find resource in repo by path and commit SHA, return it.
    #FIXME: SHA
    if not path: path = "/"
    if path == "/":
        repo = git.Repo(settings.REPO_DIR)
        mytree = repo.tree().items()
        #mydict = mytree.__dict__["_contents"]
        #mydict.keys()
        return mytree
    objects = children(path=path,sha=sha,depth=depth)
    if objects.has_key(path):
        return objects[path]
    else:
        return False #path not found
    pass

def pathExists(path="",sha="",gitrepo=""):
    '''
    return True if the path exists
    return False if the path does not exist
    '''
    #FIXME: handle SHAs
    #TODO: refactor into recursive method
    if type(gitrepo) == git.repo.Repo:
        repo = gitrepo
    else:
        repo = git.Repo(settings.REPO_DIR)
    tree = repo.tree()
    mykeys = tree.keys()
    if string.count(path, "/") > 0:
        pieces = string.split(path, "/")
        for each in pieces:
            mykeys = tree.keys()
            somedict = tree.__dict__["_contents"]
            if not somedict.has_key(each):
                return False
            if type(somedict[each]) == git.tree.Tree:
                tree = somedict[each]
        return True #it exists
    else:
        #check if it exists in /
        somedict = tree.__dict__["_contents"]
        if somedict.has_key(path):
            return True #has it
        else:
            return False #not there

def pathIsFile(path="",sha="",gitrepo=""):
    '''
    return True if the path is a file
    return False if the path is a path (folder or directory)
    return False if the path does not exist (is not a file nor a dir)
    '''
    #FIXME: handle SHAs
    #TODO: refactor into recursive method
    if not gitrepo or type(gitrepo)==type("hi"): gitrepo = settings.REPO_DIR
    if type(gitrepo) == git.repo.Repo:
        repo = gitrepo
    else:
        repo = git.Repo(gitrepo)
    tree = repo.tree()
    mykeys = tree.keys() #or else it doesn't work wtf
    if (string.count(path, "/") > 0):
        pieces = string.split(path, "/")
        for each in pieces:
            #set tree to the tree with name 'each'
            #if there is no tree with name 'each',
            #then check if there's a file (git.blob.Blob)
            #with that name.
            mykeys = tree.keys() #or else it doesn't work wtf
            somedict = tree.__dict__["_contents"]
            if somedict.has_key(each):
                #if it's a file, return.
                if type(somedict[each]) == git.blob.Blob:
                    return True #it's a file
                if type(somedict[each]) == git.tree.Tree:
                    #this gets tricky.
                    tree = somedict[each]
        #it's not a file.
        return False #it's a dir, folder or tree
    else:
        #either a file or a directory in /
        somedict = tree.__dict__["_contents"]
        if somedict.has_key(path):
            if type(somedict[path]) == git.blob.Blob:
                return True #it's a file.
            elif type(somedict[path]) == git.tree.Tree:
                return False #it's a dir, folder or tree.
        else:
            return False #file or path not found

def index(request,path="",sha="",repodir=""):
    #show the index for a given path at a given sha id
    #check if the path is a path and not a file
    #if it is a file, show the view method
    pathcheck = pathExists(path=path,sha=sha)
    pathfilecheck = pathIsFile(path=path,sha=sha)
    if pathcheck and pathfilecheck:
        return view(request,path=path,sha=sha)
    if not pathcheck and path:
        return new(request,path=path)
    if repodir == "":
        repo = git.Repo(settings.REPO_DIR)
    if type(repodir) == git.repo.Repo:
        repo = repodir
    if type(repodir) == type("") and not (repodir == ""):
        repo = git.Repo(repodir)
    commits = repo.commits(start=sha or 'master', max_count=1, path=path)
    if len(commits) > 0: head = commits[0]
    else: raise Http404 #oh boy
    #if sha == "" or not sha: head = commits[0]
    #else: #index view into the past
    #    print "for great justice!\n\n\n"
    #    for commit in commits:
    #        if commit.id == sha:
    #            head = commit
    #            print "the commit object is ", commit
    #print "sha is ", head.id, " and sha was: ", sha
    
    #FIXME: use find() and pathExists() and children() and pathIsFile() here
    #files = head.tree.items()
    files = find(path=path,sha=sha,depth=1)
    if len(files) == 1 and not (type(files) == type([])): files = files.items() #oopsies

    data_for_index = [] #start with nothing
    folders_for_index = []
    for each in files:
        toinsert = {}
        myblob = each[1]
        if type(myblob) == git.tree.Tree:
            mytree = myblob
            toinsert['name'] = mytree.name
            files2 = mytree.items()
            toinsert['id'] = mytree.id
            folders_for_index.append(toinsert)
            #add this folder (not expanded) (FIXME)
        else: #just add it
            thethingy = myblob.basename
            #if string.count("/",path) == 1:
            #    thethingy = myblob.basename
            #else:
            thethingy = repo.git.git_dir + "/" + myblob.basename
            thecommit = myblob.blame(repo,commit=sha or 'master',file=thethingy)[0][0]
            toinsert['author'] = thecommit.committer.name
            toinsert['author_email'] = thecommit.committer.email
            toinsert['id'] = head.id #thecommit.id
            toinsert['date'] = thecommit.authored_date
            toinsert['message'] = thecommit.message
            toinsert['filename'] = myblob.basename
            data_for_index.append(toinsert)
    return django.shortcuts.render_to_response("index.html", locals())

def edit(request, path="", sha=""):
    '''
    edit a page. if there are POST variables, these will be taken as the contents of the edit.

    the "sha" named parameter is for which version of the file to edit
    TODO: proper branching support
    '''
    if request.method == 'GET':
        #display edit form
        pass
    elif request.method == 'POST':
        #commit modifications
        pass
    return django.shortcuts.render_to_response("edit.html", locals())

def archive(request,path="",sha=""):
    '''
    download a zip archive of the current path
    
    (the archive must have the full path (inside of it) so that it is not a tarbomb)

    #git archive --format=zip --prefix=SITE_NAME/ HEAD:THE_DIRECTORY_HERE/ > archive.zip
    '''
    repo = git.Repo(settings.REPO_DIR)
    mycommit = repo.commit(id=sha or 'master',path=path) #er, test this
    mytree = mycommit.tree()
    myitems = mytree.items()
    #now what about the path?
    #cases:
    #1) it's a file
    #2) it's a folder
    return django.shortcuts.render_to_response("archive.html", locals())

def history(request,path="",sha=""):
    '''
    return the history for a given path (commits)

    "sha" determines the latest version to show (not necessary but useful for paging, etc.)

    should work for /history, some-dir/history, and some-file/history
    '''
    #display: id, committer.author, committer.author_email, date, message
    if not pathExists(path=path,sha=sha):
        raise Http404
    #see: http://adl.serveftp.org:4567/history
    #see: adl /var/www/git-wiki/lib/wiki/resource.rb
    repo = git.Repo(settings.REPO_DIR)
    log = repo.log(commit=sha or 'master',path=path)
    history_data = []
    for commit in log:
        toadd = {}
        toadd["commit_id"] = commit.id
        toadd["author"] = commit.author.name
        toadd["author_email"] = commit.author.email
        toadd["date"] = commit.committed_date
        toadd["message"] = commit.summary
        history_data.append(toadd)
    return django.shortcuts.render_to_response("history.html", locals())

def diff(request, path="", sha1="", sha2=""):
    '''
    display the diff between two commits (SHA strings)

    to select them, use the history view.
    '''
    if not pathExists(path=path,sha=sha1) or not pathExists(path=path,sha=sha2):
        #that commit doesn't exist!
        raise Http404
    repo = git.Repo(settings.REPO_DIR)
    diff = repo.diff(a=sha1,b=sha2,paths=[path])
    return django.shortcuts.render_to_response("diff.html", locals())

def upload(request, path=""):
    '''
    upload a file
    '''
    if request.method == 'GET':
        #display the form
        pass
    elif request.method == 'POST':
        #upload file
        pass
    return django.shortcuts.render_to_response("upload.html", locals())

def new(request,path="",sha=""):
    '''
    make a new file/page at the given "path"

    TODO: implement branching given the "sha" named parameter
    '''
    if request.method == 'GET':
        #show the form
        pass
    elif request.method == 'POST':
        #add content to repo
        pass
    return django.shortcuts.render_to_response("new.html", locals())

def changelog(request,path="",sha=""):
    '''
    display the RSS changelog for this path

    TODO: display the RSS changelog for all changes since sha="sha" (optional)
    '''
    return django.shortcuts.render_to_response("changelog.rss", locals())

def view(request,path="",sha="master"):
    '''
    view the path/file/page at a given commit

    note: if it's a folder, return the index view.
    '''
    print "************* ///// IN VIEW /////// **************"
    #check if the path is a path or if the path is a file
    #if the path is a file, continue
    #otherwise, return the index view
    if path:
        if not pathIsFile(path=path,sha=sha):
            return index(request,path=path,sha=sha)
    repo = git.Repo(settings.REPO_DIR)
    commits = repo.commits(start=sha,max_count=1)
    head = commits[0]
    files = head.tree.items()
    returncontents = ""
    for each in files:
        myblob = each[1]
        filename = myblob.name
        print "// IN FILES! myblob = ", myblob
        print "each = ", each
        print "path = ", path

        if filename == path:
            #we have a match
            contents = myblob.data
            returncontents = contents
            break
    return django.shortcuts.render_to_response("view.html", locals())

def render(request, file="", filename=""):
    '''
    render - meant for displaying some of the static images for the template
    
    this is a terrible hack.
    (see urls.py)
    '''
    if not filename and not (file == ""):
        if (file.rfind("css") > 0):
            return django.shortcuts.render_to_response(file,locals(),mimetype="text/css")
        elif (file.rfind("js") > 0):
            return django.shortcuts.render_to_response(file,locals(),mimetype="text/js")
    elif not filename == "":
        fp = open(os.path.join(os.path.realpath(os.path.curdir),("templates/pydjangitwiki-static/static/images/%s.png" % (filename))))
        blah = fp.read()
        return HttpResponse(blah,mimetype="image/png")
