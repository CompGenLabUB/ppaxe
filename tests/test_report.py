# -*- coding: utf-8 -*-
'''
Tests for the summary/report of the analyses
'''
from ppaxe import core
from pycorenlp import StanfordCoreNLP
import json

def test_summary_totalcount():
    '''
    Tests totalcount of ProtSummary
    '''
    article_text = """
             MAPK seems to interact with chloroacetate esterase.
             However, MAPK is a better target for peroxydase.
             The thing is, Schmidtea mediterranea is a good model organism because reasons.
             However, cryoglobulin is better.
         """
    article = core.Article(pmid="1234", fulltext=article_text)
    article.extract_sentences()
    for sentence in article.sentences:
        sentence.annotate()
        sentence.get_candidates()
    summary = core.ReportSummary([article])
    summary.protsummary.makesummary()
    assert(summary.protsummary.prot_table['MAPK']['totalcount'] == 2)


def test_summary_intcount():
    '''
    Tests int_count of ProtSummary
    '''
    article_text = """
             MAPK seems to interact with chloroacetate esterase.
             However, MAPK is a better target for peroxydase.
             The thing is, Schmidtea mediterranea is a good model organism because reasons.
             However, cryoglobulin is better.
         """
    article = core.Article(pmid="1234", fulltext=article_text)
    article.extract_sentences()
    for sentence in article.sentences:
        sentence.annotate()
        sentence.get_candidates()
        for candidate in sentence.candidates:
            candidate.predict()
    summary = core.ReportSummary([article])
    summary.protsummary.makesummary()
    assert(summary.protsummary.prot_table['MAPK']['int_count']['left'] == 2)


def test_summary_prottable_tomd():
    '''
    Tests int_count of ProtSummary
    '''
    article_text = """
             MAPK seems to interact with chloroacetate esterase.
             However, MAPK is a better target for peroxydase.
             The thing is, Schmidtea mediterranea is a good model organism because reasons.
             However, cryoglobulin is better.
         """
    article = core.Article(pmid="1234", fulltext=article_text)
    article.extract_sentences()
    for sentence in article.sentences:
        sentence.annotate()
        sentence.get_candidates()
        for candidate in sentence.candidates:
            candidate.predict()
    summary = core.ReportSummary([article])
    summary.protsummary.makesummary()
    thetable = summary.protsummary.table_to_md(sorted_by="int_count")
    reftable = (
    """| Protein | Total count | Int. count | Left count | Right count |
| ----- | ----- | ----- | ----- | ----- |
| MAPK | 2 | 2 | 2 | 0 |
| CHLOROACETATE ESTERASE | 1 | 1 | 0 | 1 |
| PEROXYDASE | 1 | 1 | 0 | 1 |
| CRYOGLOBULIN | 1 | 0 | 0 | 0 |
"""
    )
    assert(thetable == reftable)

def test_summary_prottable_tohtml():
    '''
    Tests int_count of ProtSummary
    '''
    article_text = """
             MAPK seems to interact with chloroacetate esterase.
             However, MAPK is a better target for peroxydase.
             The thing is, Schmidtea mediterranea is a good model organism because reasons.
             However, cryoglobulin is better.
         """
    article = core.Article(pmid="1234", fulltext=article_text)
    article.extract_sentences()
    for sentence in article.sentences:
        sentence.annotate()
        sentence.get_candidates()
        for candidate in sentence.candidates:
            candidate.predict()
    summary = core.ReportSummary([article])
    summary.protsummary.makesummary()
    thetable = summary.protsummary.table_to_html(sorted_by="int_count")
    reftable = """<table>
<thead>
<tr>
<th>Protein</th>
<th>Total count</th>
<th>Int. count</th>
<th>Left count</th>
<th>Right count</th>
</tr>
</thead>
<tbody>
<tr>
<td>MAPK</td>
<td>2</td>
<td>2</td>
<td>2</td>
<td>0</td>
</tr>
<tr>
<td>CHLOROACETATE ESTERASE</td>
<td>1</td>
<td>1</td>
<td>0</td>
<td>1</td>
</tr>
<tr>
<td>PEROXYDASE</td>
<td>1</td>
<td>1</td>
<td>0</td>
<td>1</td>
</tr>
<tr>
<td>CRYOGLOBULIN</td>
<td>1</td>
<td>0</td>
<td>0</td>
<td>0</td>
</tr>
</tbody>
</table>"""
    assert(thetable == reftable)

def test_interaction_list():
    '''
    Tests if GraphSummary.makesummary() creates the interaction list correctly
    '''
    article_text = """
             MAPK seems to interact with MAPK4.
             However, Mapk4 interacts directly with MAPK.
             CPP3 is a molecular target of Akt3.
             AKT3 is also known to interact with CPP3.
         """
    article = core.Article(pmid="1234", fulltext=article_text)
    article.extract_sentences()
    for sentence in article.sentences:
        sentence.annotate()
        sentence.get_candidates()
        for candidate in sentence.candidates:
            candidate.predict()
    summary = core.ReportSummary([article])
    summary.graphsummary.makesummary()
    assert(
        len(summary.graphsummary.interactions) == 4 and
        summary.graphsummary.uniqinteractions_count == 2
    )


def test_interaction_table_md():
    '''
    Tests the markdown of the interactions table
    '''
    article_text = """
             MAPK seems to interact with MAPK4.
             However, Mapk4 interacts directly with MAPK.
             CPP3 is a molecular target of Akt3.
             AKT3 is also known to interact with CPP3.
         """
    article = core.Article(pmid="1234", fulltext=article_text)
    article.extract_sentences()
    for sentence in article.sentences:
        sentence.annotate()
        sentence.get_candidates()
        for candidate in sentence.candidates:
            candidate.predict()
    summary = core.ReportSummary([article])
    summary.graphsummary.makesummary()
    reftable = """<table>
<thead>
<tr>
<th>Confidence</th>
<th>Protein (A)</th>
<th>Protein (B)</th>
<th>Off.symbol (A)</th>
<th>Off.symbol (B)</th>
<th>PMid</th>
<th>Sentence</th>
</tr>
</thead>
<tbody>
<tr>
<td>0.844</td>
<td>Mapk4</td>
<td>MAPK</td>
<td>MAPK4</td>
<td>MAPK</td>
<td><a href="https://www.ncbi.nlm.nih.gov/pubmed/?term=1234">1234</a></td>
<td>However , <span class="prot"> Mapk4 </span> <span class="verb">interacts</span> directly with <span class="prot"> MAPK </span> .</td>
</tr>
<tr>
<td>0.796</td>
<td>CPP3</td>
<td>Akt3</td>
<td>CPP3</td>
<td>AKT3</td>
<td><a href="https://www.ncbi.nlm.nih.gov/pubmed/?term=1234">1234</a></td>
<td><span class="prot"> CPP3 </span> <span class="verb">is</span> a molecular target of <span class="prot"> Akt3 </span> .</td>
</tr>
<tr>
<td>0.744</td>
<td>MAPK</td>
<td>MAPK4</td>
<td>MAPK</td>
<td>MAPK4</td>
<td><a href="https://www.ncbi.nlm.nih.gov/pubmed/?term=1234">1234</a></td>
<td><span class="prot"> MAPK </span> <span class="verb">seems</span> to <span class="verb">interact</span> with <span class="prot"> MAPK4 </span> .</td>
</tr>
<tr>
<td>0.714</td>
<td>AKT3</td>
<td>CPP3</td>
<td>AKT3</td>
<td>CPP3</td>
<td><a href="https://www.ncbi.nlm.nih.gov/pubmed/?term=1234">1234</a></td>
<td><span class="prot"> AKT3 </span> <span class="verb">is</span> also <span class="verb">known</span> to <span class="verb">interact</span> with <span class="prot"> CPP3 </span> .</td>
</tr>
</tbody>
</table>"""
    htmltable = summary.graphsummary.table_to_html()
    assert(htmltable == reftable)

def test_simple_report():
    '''
    Test first version of report
    '''
    article_text = """
             MAPK seems to interact with MAPK4.
             However, Mapk4 interacts directly with MAPK.
             CPP3 is a molecular target of Akt3.
             AKT3 is also known to interact with CPP3.
             Upon association with the destruction complex, GSK3β phosphorylates β-catenin, thus priming it for ubiquitination by β-TRCP and degradation by the proteasome.
             Tankyrase recognizes its substrate proteins through the multiple ankyrin repeat cluster domains for PARylation and is involved in telomere homeostasis and in other biological events such as mitosis.
             p70S6K and 4E-BP1 are regulated by the mTORC1 complex.
             More research into this area will help guide the research community in understanding the role that PKG plays in modulating Wnt / β-catenin signaling.
         """
    article = core.Article(pmid="28615517", fulltext=article_text)
    article.extract_sentences()
    for sentence in article.sentences:
        sentence.annotate()
        sentence.get_candidates()
        for candidate in sentence.candidates:
            candidate.predict()
    summary = core.ReportSummary([article])
    summary.make_report()