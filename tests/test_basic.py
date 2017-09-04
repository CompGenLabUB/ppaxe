# -*- coding: utf-8 -*-
'''
Tests for the main classes of ppaxe
'''
from ppaxe import core
from pycorenlp import StanfordCoreNLP
import json

def test_sentence_separator():
    '''
    Tests if sentence separator works...
    '''
    article = core.Article(pmid="1234", fulltext="""
        To identify roles of Hh signaling in the planarian CNS maintenance, we examined gene expression changes using RNA sequencing of cephalic ganglia following RNAi of hh, ptc, or a control gene (C. elegans unc-22) not present in the planarian genome.
        We developed a dissection technique that allowed cephalic ganglia tissue to be collected from large (>2 cm) S2F1L3F2 sexual strain S. mediterranea animals following a brief acid-based fixation (Figure 1C).
        To test for enrichment using this dissection technique, amputated head fragments collected from CIW4 asexual strain S. mediterranea animals after six control dsRNA feedings were used as a reference library (Figure 1D).
        Head fragments contain cephalic ganglia as well as most major planarian tissue types (Hyman, 1951).
        The magic number is 12.45 for the species S. mediterranea.
        Figure 2.a and 3.B Is the most important.
        S. mediterranea and C. elegans.
        But not (S.mediterranea)
    """)
    article.extract_sentences()
    assert(len(article.sentences) == 8)

def test_stanford_corenlp_server():
    '''
    Tests connection to stanford corenlp server
    '''
    try:
        nlp = StanfordCoreNLP('http://localhost:9000')
        nlp.annotate("HOLA")
        assert(1 == 1)
    except:
        assert("Connection error" == "StanfordCoreNLP")

def test_annotation():
    '''
    Tests if Stanford coreNLP NER works
    '''
    text = "MAPK seems to interact with chloroacetate esterase"
    nlp = StanfordCoreNLP('http://localhost:9000')
    ner_list = list()
    for token in json.loads(nlp.annotate(text))['sentences'][0]['tokens']:
        ner_list.append(token['ner'])
    assert("".join(ner_list) == "POOOOPP")

def test_article_annotation():
    '''
    Tests if article annotation works
    '''
    article_text = """
        MAPK seems to interact with chloroacetate esterase.
        However, MAPK is a better target for peroxydase.
        The thing is, Schmidtea mediterranea is a good model organism because reasons.
        However, cryoglobulin is better.
    """
    article = core.Article(pmid="1234", fulltext=article_text)
    prot_list = list()
    #article.annotate_sentences()
    article.extract_sentences()
    for sentence in article.sentences:
        sentence.annotate()
        for token in sentence.tokens:
            if token['ner'] == "P":
                prot_list.append(token['word'])
    assert(",".join(prot_list) == "MAPK,chloroacetate,esterase,MAPK,peroxydase,cryoglobulin")

def test_get_proteins():
    '''
    Tests the retrieval of candidates
    '''
    text = "However, MAPK is a better target for chloroacetate esterase which is an essential protein for cryoglobulin."
    article = core.Article(pmid="1234", fulltext=text)
    article.extract_sentences()
    for sentence in article.sentences:
        sentence.annotate()
        sentence.get_candidates()
        candidate = str(sentence.candidates[0])
        assert(candidate == "[MAPK] may interact with [chloroacetate esterase]")

def test_token_distance():
    '''
    Tests token distance feature
    '''
    text = "The protein MAPK interacts directly with cryoglobulin which is very interesting."
    article = core.Article(pmid="1234", fulltext=text)
    article.extract_sentences()
    for sentence in article.sentences:
        sentence.annotate()
        sentence.get_candidates()
        candidate = sentence.candidates[0]
        candidate.compute_features()
        assert(candidate.features_todense()[0] == 3)

def test_total_tokens():
    '''
    Tests total tokens
    '''
    text = "The protein MAPK interacts directly with cryoglobulin which is very interesting."
    article = core.Article(pmid="1234", fulltext=text)
    article.extract_sentences()
    for sentence in article.sentences:
        sentence.annotate()
        sentence.get_candidates()
        for candidate in sentence.candidates:
            candidate.compute_features()
            assert(candidate.features_todense()[1] == 12)

def test_verb_features():
    '''
    Tests total number of verbs between proteins
    '''
    text = "The protein MAPK is interacting and activating directly with cryoglobulin which is very interesting."
    article = core.Article(pmid="1234", fulltext=text)
    article.extract_sentences()
    for sentence in article.sentences:
        sentence.annotate()
        sentence.get_candidates()
        for candidate in sentence.candidates:
            candidate.compute_features()
            # Check if it has detected one VBG (interacting) verb and another VBZ (is) verb
            # and verb scores (for now 3 and 5)
            assert(candidate.features_todense()[2:14] == [0, 0, 2, 0, 0, 1, 4, 7, 1, 4, 3, 6])

def test_candidates_multiple_sentences():
    '''
    Tests if multiple sentences in one string work
    '''
    text = "In patients with a complete response to PROT4  , the levels of PROT2  were higher at 24 weeks following PROT4  treatment than that of pre - treatment ( P = 0.04 ) , and the levels of PROT3  decreased markedly at 12 and 24 weeks ( P = 0.02 , 0.03 , respectively ) . mRNA expression positively correlated with the level of PROT55 / Th2 type cytokines in the PROT99 ."
    article = core.Article(pmid="1234", fulltext=text)
    article.extract_sentences()
    total_candidates = list()
    for sentence in article.sentences:
        sentence.get_candidates()
        total_candidates.extend(sentence.candidates)
    assert(total_candidates[-1].prot2.symbol == "PROT99")


def test_get_pos_annotation():
    '''
    Tests the method get_token_pos()
    '''
    text = "The protein MAPK14 seems to interact with MAPK12."
    article = core.Article(pmid="1234", fulltext=text)
    article.extract_sentences()
    for sentence in article.sentences:
        sentence.annotate()
        sentence.get_candidates()
        assert(sentence.candidates[0]._InteractionCandidate__get_token_pos(mode="between") == "NN,VBZ,TO,VB,IN,NN")

def test_sentence_to_html():
    '''
    Tests if sentence to html works
    '''
    text = "The transcription factor of THOC2 seems to be interacting with the nuclear receptor protein 2."
    article = core.Article(pmid="1234", fulltext=text)
    article.extract_sentences()
    for sentence in article.sentences:
        sentence.annotate()
        sentence.get_candidates()
        assert(sentence.to_html() == "The transcription factor of <prot> THOC2 </prot> seems to be interacting with the <prot> nuclear receptor protein 2 </prot> .")

def get_pos_count():
    '''
    Tests pos count feature
    '''
    text = "The protein MAPK14 seems to interact with MAPK12."
    article = core.Article(pmid="1234", fulltext=text)
    article.extract_sentences()
    for sentence in article.sentences:
        sentence.annotate()
        sentence.get_candidates()
        for candidate in sentence.candidates:
            candidate.compute_features()
            assert(candidate.features_todense()[85] == 1)

def test_prot_count():
    '''
    Tests if prot count features work
    '''
    text = "MAPK13 seems to be directly correlated with MAPK12, which would mean that MAPK13 depends on the expression of MAPK13 and MAPK12."
    article = core.Article(pmid="1234", fulltext=text)
    article.extract_sentences()
    for sentence in article.sentences:
        sentence.annotate()
        sentence.get_candidates()
        #print(",,".join([token['word'] for token in sentence.tokens]))
        second_candidate = sentence.candidates[1]
        second_candidate.compute_features()
        last_candidate   = sentence.candidates[-1]
        last_candidate.compute_features()
        '''
        Assert that:
        [MAPK13] seems to be directly correlated with MAPK12, which would mean that [MAPK13]
            - MAPK13 only appears two times
            - etc.
        (...) [MAPK13] and [MAPK12].
            - MAPK12 appears 2 times
            - etc.
        '''

        assert(
            second_candidate.features_todense()[112] == 2 and
            second_candidate.features_todense()[113] == 2 and
            second_candidate.features_todense()[114] == 3 and
            second_candidate.features_todense()[115] == 3 and
            last_candidate.features_todense()[112] == 1   and
            last_candidate.features_todense()[113] == 1   and
            last_candidate.features_todense()[114] == 3   and
            last_candidate.features_todense()[115] == 2
        )

def test_keyword_count():
    '''
    Tests if keyword count features work
    '''
    text = "PROT12 interacts interacts and acetylates PROT1."
    article = core.Article(pmid="1234", fulltext=text)
    article.extract_sentences()
    for sentence in article.sentences:
        sentence.annotate()
        sentence.get_candidates()
        sentence.candidates[0].compute_features()
        '''
        Assert that Interact == 2 and Acetylate == 1
        '''
        assert(
            sentence.candidates[0].features_todense()[150] == 2 and
            sentence.candidates[0].features_todense()[116] == 1
        )

def test_prediction():
    '''
    Tests if the prediction works
    '''
    text = "PROT12 interacts with PROT2."
    article = core.Article(pmid="1234", fulltext=text)
    article.extract_sentences()
    for sentence in article.sentences:
        sentence.annotate()
        sentence.get_candidates()
        sentence.candidates[0].compute_features()
        sentence.candidates[0].predict()
        assert(sentence.candidates[0].votes == 0.882)

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
    summary = core.ReportSummary([article])
    summary.protsummary.makesummary()
    thetable = summary.protsummary.table_to_md(sorted_by="int_count")
    reftable = ("| PROT_SYMBOL | TOTAL_COUNT | INT_COUNT | LEFT_COUNT | RIGHT_COUNT | \n" +
               "|-----|-----|-----|-----|-----|\n" +
               "| MAPK | 2 | 2 | 2 | 0  |\n" +
               "| CHLOROACETATE ESTERASE | 1 | 1 | 0 | 1  |\n" +
               "| PEROXYDASE | 1 | 1 | 0 | 1  |\n" +
               "| CRYOGLOBULIN | 1 | 0 | 0 | 0  |")
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
    summary = core.ReportSummary([article])
    summary.protsummary.makesummary()
    thetable = summary.protsummary.table_to_html(sorted_by="int_count")
    reftable = """<table>
<thead>
<tr>
<th>PROT_SYMBOL</th>
<th>TOTAL_COUNT</th>
<th>INT_COUNT</th>
<th>LEFT_COUNT</th>
<th>RIGHT_COUNT</th>
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
        summary.graphsummary.uniqinteractions == 2
    )
