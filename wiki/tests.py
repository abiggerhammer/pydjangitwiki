#!/usr/bin/python
import unittest
import git
import copy
import pydjangitwiki.wiki.views
import pydjangitwiki.urls
#import django.test.client

def find_urls(methodname="index"):
    '''
    return all RegexURLPattern objects that call a certain method
    '''
    patterns = pydjangitwiki.urls.urlpatterns
    returnlist = []
    for pat in patterns:
        if pat.callback.__name__ == methodname:
            #see also: pat.callback.__module__
            returnlist.append(pat)
    return returnlist

def resolve(regexes=[],validpatterns=[]):
    returndict = {}
    for each in regexes:
        for pattern in validpatterns:
            if not each.resolve(pattern) == None:
                if not returndict.has_key(pattern):
                    returndict[pattern] = [each]
                else:
                    returndict[pattern].append(each)
    return returndict

class TestURLs(unittest.TestCase):
    def test_index(self):
        #pydjangitwiki.urls.urlpatterns that should return 'pydjangitwiki.wiki.views.index'
        #note: some of these patterns are handled by 'view' which then calls index()
        #validpatterns = ["/", "", "/folder-name/", "folder-name"]
        validpatterns = [""]
        regexes = find_urls(methodname="index")
        testresults = resolve(regexes=regexes,validpatterns=validpatterns)
        self.assertTrue(len(testresults) == len(validpatterns))
        return
    def test_edit(self):
        validpatterns = [
                            "edit/",
                            "edit",
                            "home/something/something/edit",
                            "home/something/something/edit/",
                        ]
        regexes = find_urls(methodname="edit")
        testresults = resolve(regexes=regexes,validpatterns=validpatterns)
        self.assertTrue(len(testresults) == len(validpatterns))
        return
    def test_archive(self):
        validpatterns = [
                            "archive/", #or is this a dir?
                            "archive",
                            "home/something/something/archive", #or is this a file?
                            "home/something/something/archive/", #or is this a dir?
                            "/archive", #or is this a file?
                            "/archive/", #or is this a dir?
                        ]
        regexes = find_urls(methodname="archive")
        testresults = resolve(regexes=regexes,validpatterns=validpatterns)
        self.assertTrue(len(testresults) == len(validpatterns))
        return
    def test_history(self):
        validpatterns = [
                            "history",
                            "/history", #or is this a file?
                            "/history/", #or is this a dir?
                            "history/", #or is this a dir?
                            "some/path/here/history",
                            "some/path/here/history/", #or is this a dir?
                        ]
        regexes = find_urls(methodname="history")
        testresults = resolve(regexes=regexes,validpatterns=validpatterns)
        self.assertTrue(len(testresults) == len(validpatterns))
        return
    def test_upload(self):
        validpatterns = [
                            "upload",
                            "some/path/to/a/file/upload",
                            #"some/path/to/a/dir/upload", #should this be invalid?
                        ]
        regexes = find_urls(methodname="upload")
        testresults = resolve(regexes=regexes,validpatterns=validpatterns)
        self.assertTrue(len(testresults) == len(validpatterns))
        return
    def test_new(self):
        validpatterns = [
                            "new",
                            "some/path/to/a/dir/file/new",
                        ]
        regexes = find_urls(methodname="new")
        testresults = resolve(regexes=regexes,validpatterns=validpatterns)
        self.assertTrue(len(testresults) == len(validpatterns))
        return
    def test_changelog(self):
        validpatterns = [
                            "changelog.rss",
                            "some/path/to/a/dir/file/changelog.rss",
                        ]
        regexes = find_urls(methodname="changelog")
        testresults = resolve(regexes=regexes,validpatterns=validpatterns)
        self.assertTrue(len(testresults) == len(validpatterns))
        return
    def test_view(self):
        validpatterns = [
                            "some/path/to/a/file",
                            "some/path/to/a/dir/", #should redirect to index() however
                            "some/path/to/a/file/SHA_HERE",
                        ]
        regexes = find_urls(methodname="view")
        testresults = resolve(regexes=regexes,validpatterns=validpatterns)
        self.assertTrue(len(testresults) == len(validpatterns))
        return
    def test_render(self):
        #not sure if we care about this hack of a function
        #it should be rewritten anyway
        pass

class TestViews(unittest.TestCase):
    def test_pop_path(self):
       path = "super/star/destroyer"
       self.assertTrue(pydjangitwiki.wiki.views.pop_path(path)=="star/destroyer")
       path ="/super/star/destroyer"
       #print pydjangitwiki.wiki.views.pop_path(path)
       self.assertTrue(pydjangitwiki.wiki.views.pop_path(path)=="star/destroyer")
       path = "one/two/three/four/"
       self.assertTrue(pydjangitwiki.wiki.views.pop_path(copy.copy(path))=="two/three/four/")
       popped = pydjangitwiki.wiki.views.pop_path(copy.copy(path))
       popped2 = pydjangitwiki.wiki.views.pop_path(copy.copy(popped))
       self.assertTrue(popped2=="three/four/")
    def test_children(self):
        #find all tree items and combine them into a dict
        #depth=-1 means infinite depth
        
        #make a repo, add files, commit, etc.
        #then check to see if those files are there
        #see git.Repo.init_bare(path,mkdir=True)

        #now make a repo, add files, commit, add folders, etc.
        #then check to see if those files & folders are there

        pass
    def test_find(self):
        pass
    def test_pathExists(self):
        pass
    def test_pathIsFile(self):
        pass
    def test_index(self):
        pass
    def test_edit(self):
        pass
    def test_archive(self):
        pass
    def test_history(self):
        pass
    def test_upload(self):
        pass
    def test_new(self):
        pass
    def test_changelog(self):
        pass
    def test_view(self):
        pass
    def test_render(self):
        #not sure if this needs to be tested
        #it's kind of a hack in the first place
        pass

if __name__ == '__main__':
    unittest.main()