# -*- coding: utf-8 -*-
import sys
import pprint

from subprocess import Popen, PIPE
from utils.memoize import persistent_memoize
from structures.containers import relationships
from utils.debug import *

RELEX_DIRECTORY = './'
RELEX_VM_OPTS = "-Xmx1024m -Djava.library.path=/usr/lib:/usr/local/lib"
RELEX_CLASSPATH = "-classpath \
engines/relex/bin:\
/home/bluemoon/Downloads/jwnl.jar:\
/usr/local/share/java/jwnl-1.4rc2.jar:\
/usr/local/share/java/jwnl-1.3.3.jar:\
/usr/local/share/java/opennlp-tools-1.4.3.jar:\
/usr/local/share/java/opennlp-tools-1.3.0.jar:\
/usr/local/share/java/maxent-2.5.2.jar:\
/usr/local/share/java/maxent-2.4.0.jar:\
/usr/local/share/java/trove.jar:\
/usr/local/share/java/linkgrammar.jar:\
/usr/share/java/linkgrammar-4.6.0.jar:\
/usr/share/java/commons-logging-1.1.1-SNAPSHOT.jar:\
/usr/share/java/gnu-getopt.jar:\
/usr/share/java/xercesImpl.jar:\
/opt/GATE-5.0/bin/gate.jar:\
/opt/GATE-5.0/lib/jdom.jar:\
/opt/GATE-5.0/lib/jasper-compiler-jdt.jar:\
/opt/GATE-5.0/lib/nekohtml-0.9.5.jar:\
/opt/GATE-5.0/lib/ontotext.jar:\
/opt/GATE-5.0/lib/stax-api-1.0.1.jar:\
/opt/GATE-5.0/lib/PDFBox-0.7.2.jar:\
/opt/GATE-5.0/lib/wstx-lgpl-2.0.6.jar"

class relex:
    @persistent_memoize
    def process(self, sentence):
        output = []
        command = 'java %s %s relex.RelationExtractor -n 1 -f -a -s "%s"' % (RELEX_VM_OPTS, RELEX_CLASSPATH, sentence)
        p = Popen(command, stdout=PIPE, stderr=open('/dev/null', 'w'), shell=True)
        while True:
            o = p.stdout.readline()
            output.append(o)
            if o == '' and p.poll() != None: break
        
        return output

    def _before_and_after(self, List, item):
        if item in List:
            idx = List.index(item)
            before = List[:idx]
            after = List[idx+1:]
            return (before, after)
        else:
            return False
    
    def parse_output(self, input_from):
        #debug(input_from)
        wo_newlines = []
        for x in input_from:
            y = x.split('\n')
            for z in y:
                if z:
                    wo_newlines.append(z)
            
        DEP_STRING   = 'Dependency relations:'
        FRAME_STRING = 'Framing rules applied:'
        ANTE_STRING  = 'Antecedent candidates:'
        
        dependency_rel = self._before_and_after(wo_newlines, DEP_STRING)

        if dependency_rel:
            framing_rules = self._before_and_after(dependency_rel[1], '======')
            dependencies = framing_rules[0]
            frames = framing_rules[1]
            f_ante = self._before_and_after(frames, FRAME_STRING)
            frames = f_ante[0]
            ## and we use our container
            r = relationships(dependencies, frames)
            return r
        
