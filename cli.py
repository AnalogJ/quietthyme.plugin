#!/usr/bin/env python
# vim:fileencoding=UTF-8:ts=4:sw=4:sta:et:sts=4:ai
__license__   = 'GPL v3'
__copyright__ = '2011, Jason Kulatunga <jason@quietthyme.com>'
__docformat__ = 'restructuredtext en'

from optparse import OptionParser

def main(argv,usage=None):

    if not usage:
        # read in args, anything starting with -- will be treated as --<varible>=<value>
        usage = "usage: python %prog"
    optparser = OptionParser(usage+''' [options] <input epub> [<input epub>...]
Given list of epubs will be merged together into one new epub.
''')

    optparser.add_option("-o", "--output", dest="outputopt", default="merge.epub",
                         help="Set OUTPUT file, Default: merge.epub", metavar="OUTPUT")
    optparser.add_option("-t", "--title", dest="titleopt", default=None,
                         help="Use TITLE as the metadata title.  Default: '<first epub title> Anthology'", metavar="TITLE")
    optparser.add_option("-d", "--description", dest="descopt", default=None,
                         help="Use DESC as the metadata description.  Default: '<epub title> by <author>' for each epub.", metavar="DESC")
    optparser.add_option("-a", "--author",
                         action="append", dest="authoropts", default=[],
                         help="Use AUTHOR as a metadata author, multiple authors may be given, Default: <All authors from epubs>", metavar="AUTHOR")
    optparser.add_option("-g", "--tag",
                         action="append", dest="tagopts", default=[],
                         help="Include TAG as dc:subject tag, multiple tags may be given, Default: None", metavar="TAG")
    optparser.add_option("-l", "--language",
                         action="append", dest="languageopts", default=[],
                         help="Include LANG as dc:language tag, multiple languages may be given, Default: en", metavar="LANG")
    optparser.add_option("-n", "--no-titles-in-toc",
                         action="store_false", dest="titlenavpoints", default=True,
                         help="Default is to put an entry in the TOC for each epub, nesting each epub's chapters under it.",)
    optparser.add_option("-f", "--flatten-toc",
                         action="store_true", dest="flattentoc",
                         help="Flatten TOC down to one level only.",)
    optparser.add_option("-c", "--cover", dest="coveropt", default=None,
                         help="Path to a jpg to use as cover image.", metavar="COVER")
    optparser.add_option("-k", "--keep-meta",
                         action="store_true", dest="keepmeta",
                         help="Keep original metadata files in merged epub.  Use for UnMerging.",)
    optparser.add_option("-s", "--source", dest="sourceopt", default=None,
                         help="Include URL as dc:source and dc:identifier(opf:scheme=URL).", metavar="URL")

    optparser.add_option("-u", "--unmerge",
                         action="store_true", dest="unmerge",
                         help="UnMerge an existing epub that was created by merging with --keep-meta.",)
    optparser.add_option("-D", "--outputdir", dest="outputdir", default=".",
                         help="Set output directory for unmerge, Default: (current dir)", metavar="OUTPUTDIR")

    (options, args) = optparser.parse_args(argv)

    if not args:
        optparser.print_help()
        return
