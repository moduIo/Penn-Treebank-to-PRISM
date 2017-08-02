# extract.py:  Extract a grammar, with frequency counts, from a corpus.
# The extracted grammar is written into two files:
#  *.pos, for the POS tags, which are the pre-terminal symbols of the grammar
#  *.full, productions for all non-termimals except those in POS tags
# Currently, -NONE- is treated as a POS tag (should be epsilon).

# We also extract sentences -- both tagged as well as those comprising only of POS tags.
# This is done as we read a tree.  Leaves are terminals; one level above are POS tags.
# Sentences collected this way are output to two files:
#  *.tagged:  tagged sentences in the form of (tag/terminal)
#  *_sentences.P:    sentences with tags alone, in Prolog readable form.  (omitting -NONE-)


import sys
import time

def tree(f):
    s = ''
    for x in f:
        if (x == '' or x.isspace()):
            if (s != ''):
                yield s
                s = ''
        else:
            s = s + x
    if (s != ''):
        yield s

productions = {}
xbar_productions = {}
terminals = []
postag = []
sentence = []

def add_production(lhs, rhs):
    global productions
    
    add_to_bag(productions, (lhs, rhs))

def add_xbar_production(lhs, rhs):
    global xbar_productions

    if len(rhs) <= 2:
        add_to_bag(xbar_productions, (lhs, rhs))
    else:
        xbar = lhs+'-XBAR'

        r12 = rhs[:2]  # first two elements (note: original len >= 3)
        add_to_bag(xbar_productions, (xbar, r12))

        for r2 in rhs[2:-1]:
            nrhs = [xbar, r2]
            add_to_bag(xbar_productions, (xbar, nrhs))

        rl = rhs[len(rhs)-1] # last element
        add_to_bag(xbar_productions, (lhs, [xbar, rl]))

def add_to_bag(bag, record):
    key = str(record)
    if key in bag:
        (count, p) = bag[key]
        count +=1
        bag[key] = (count, p)
    else:
        bag[key] = (1, record)

def add_terminal(s):
    global terminals
    
    if s in terminals:
        return
    else:
        terminals.append(s)

        
def parse_tree(w, i, n):
    global sentence
    # returns (root, j) where root is the root symbol and j is the last index parsed
    root = None
    if ((i+1 < n) and w[i] == '('):
        root = w[i+1]
        (rhs, j) = parse_treeseq(w, i+2, n)
        if (j == (i+3)):
            t = rhs[0]
            sentence.append( (root, t) )
        add_production(root, rhs)
        add_xbar_production(root, rhs)
        return (root, j)
    elif ((i < n) and w[i] != ')'):
        # terminal symbol?
        root = "'" + w[i] + "'"
        add_terminal(root)
        return (root, i)
    else:
        raise Exception('production generation')

def parse_treeseq(w, i, n):
    # returns (rs, j) where rs sequence of symbols and j is the last index parsed
    if ((i<n) and w[i] == ')'):
        return ([], i)
    else:
        (t,j) = parse_tree(w, i, n)
        (rest, k) = parse_treeseq(w, j+1, n)
        return ([t]+rest, k)

def analyze():
    global postag
    # find possible POS tags
    postag = []
    nonterminals = []
    # these are lhs symbols of productions with a single terminal symbol on the rhs.
    for k in productions:
        (_, (l, r)) = productions[k]
        if (l not in nonterminals):
            nonterminals.append(l)
        if (len(r) == 1) and (r[0] in terminals):
            if (l not in postag):
                postag.append(l)
    # Now check if a postag symbol also occurs in a production whose rhs is not a singleton terminal
    for k in productions:
        (_, (l, r)) = productions[k]
        if (len(r) == 1) and (r[0] in terminals):
            continue
        else:
            if (l in postag):
                print l + ' also appears on lhs of ' + k

    nnt = len(nonterminals)
    npos = len(postag)
    nspec = 0
    for s in nonterminals:
        if s not in postag:
            if '-' in s:
                nspec += 1 
    print "Found %d total nonterminal symbols" % nnt
    print "Found %d POS tags" % npos
    print "Number of base NT symbols = %d" % (nnt - npos - nspec)

def print_grammar(basename):
    global postag
    posfile = basename + '.pos'
    fullfile = basename + '.full'
    xbarfile = basename + '_xbar.P'
    postagfile = basename + '_postags.P'

    with open(posfile, 'w') as fout:
        for k in productions:
            (c, (l, r)) = productions[k]
            if l in postag:
                fout.write('%d: %s-->%s\n' % (c, l, str(r)))
    
    with open(fullfile, 'w') as fout:
        for k in productions:
            (c, (l, r)) = productions[k]
            if l not in postag:
                fout.write('%d: %s-->%s\n' % (c, l, str(r)))

    with open(postagfile, 'w') as fout:
        for l in postag:
            if l != "-NONE-":
                fout.write("terminal('%s').\n" % quote(l))

    with open(xbarfile, 'w') as fout:
        counts = {}
        for k in xbar_productions:
            (c, (l,_)) = xbar_productions[k]
            if l in counts:
                counts[l] += c
            else:
                counts[l] = c
            
        for k in xbar_productions:
            (c, (l, r)) = xbar_productions[k]
            rq = [quote(t) for t in r]
            if l not in postag:
                fout.write("production('%s', %s, %g).\n" % (l, str(rq), (c*1.0/counts[l])))

def quote(s):
    s = s.replace("'", "\\'")
    return s
    
def print_sentences(basename, sentences):
    taggedfile = basename + '.tagged'
    sentencefile = basename + '_sentences.P'

    with open(taggedfile, 'w') as fout:
        for s in sentences:
            for (t,w) in s:
                fout.write('%s/%s ' % (t,w))
            fout.write('\n')
    
    with open(sentencefile, 'w') as fout:
        i = 0
        for s in sentences:
            t = [quote(x) for (x,_) in s if x!= '-NONE-']
            fout.write('sentence(%d, %s).\n' % (i, t))
            i += 1
    
    
def process(fromfile):
    global postag, sentence
    sentences=[]
    
    (basename, _, _) = fromfile.partition('.')        
    fin = open(fromfile, 'r')
    n = 0
    c0 = time.clock()
    for x in tree(fin):
        w = x.replace('(', ' ( ').replace(')', ' ) ').split()
        sentence=[]
        parse_tree(w, 0, len(w))
        sentences.append(sentence)
        n += 1
    fin.close()
    c1 = time.clock()
    print 'Reading and processsing took %g seconds' % (c1-c0)
    print '============== Grammar =================='
    print str(n) + ' trees processed\n'
    c0 = time.clock()
    analyze()
    c1 = time.clock()
    print "Analysis took %g seconds" % (c1-c0)
    #    print postag
    mpos = 0
    mnonpos = 0
    units = 0
    empties = 0
    for k in productions:
        (c, (l, r)) = productions[k]
        if (l not in postag):
            mnonpos += 1
            if (len(r) == 1):
                units += 1
            if (len(r) == 0):
                empties += 1
        else:
            mpos += 1
    print str(mpos) + ' preterminal rules found'
    print str(mnonpos) + ' non preterminal rules found'
    print str(empties) + ' epsilon rules found'
    print str(units) + ' unit rules found'
    print str(len(terminals)) + ' terminal symbols found'

    print_grammar(basename)
    print_sentences(basename, sentences)
    

if (len(sys.argv) != 2):
    print 'Usage: python extract inputfile'
    sys.exit(0)
    
process(sys.argv[1])

