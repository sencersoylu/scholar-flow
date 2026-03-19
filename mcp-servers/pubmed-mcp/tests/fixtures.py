"""Shared test constants for PubMed MCP server tests."""

SAMPLE_ESEARCH_RESPONSE = """<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE eSearchResult PUBLIC "-//NLM//DTD esearch 20060131//EN" "https://eutils.ncbi.nlm.nih.gov/eutils/dtd/20060131/esearch.dtd">
<eSearchResult>
    <Count>1500</Count>
    <RetMax>2</RetMax>
    <RetStart>0</RetStart>
    <IdList>
        <Id>38000001</Id>
        <Id>38000002</Id>
    </IdList>
</eSearchResult>"""

SAMPLE_EFETCH_RESPONSE = """<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE PubmedArticleSet PUBLIC "-//NLM//DTD PubMedArticle, 1st January 2024//EN" "https://dtd.nlm.nih.gov/ncbi/pubmed/out/pubmed_240101.dtd">
<PubmedArticleSet>
    <PubmedArticle>
        <MedlineCitation>
            <PMID>38000001</PMID>
            <Article>
                <ArticleTitle>Effect of Exercise on Type 2 Diabetes</ArticleTitle>
                <Abstract>
                    <AbstractText>Background: Exercise improves glycemic control.</AbstractText>
                </Abstract>
                <AuthorList>
                    <Author>
                        <LastName>Smith</LastName>
                        <Initials>J</Initials>
                    </Author>
                    <Author>
                        <LastName>Doe</LastName>
                        <Initials>A</Initials>
                    </Author>
                </AuthorList>
                <Journal>
                    <Title>JAMA</Title>
                </Journal>
                <ArticleDate>
                    <Year>2024</Year>
                </ArticleDate>
            </Article>
            <MeshHeadingList>
                <MeshHeading>
                    <DescriptorName>Diabetes Mellitus, Type 2</DescriptorName>
                </MeshHeading>
                <MeshHeading>
                    <DescriptorName>Exercise</DescriptorName>
                </MeshHeading>
            </MeshHeadingList>
        </MedlineCitation>
        <PubmedData>
            <ArticleIdList>
                <ArticleId IdType="doi">10.1001/jama.2024.1234</ArticleId>
                <ArticleId IdType="pubmed">38000001</ArticleId>
            </ArticleIdList>
        </PubmedData>
    </PubmedArticle>
</PubmedArticleSet>"""

SAMPLE_MESH_RESPONSE = """<?xml version="1.0" encoding="UTF-8" ?>
<eSearchResult>
    <Count>5</Count>
    <RetMax>5</RetMax>
    <IdList>
        <Id>68003924</Id>
    </IdList>
    <TranslationSet>
        <Translation>
            <From>diabetes</From>
            <To>"Diabetes Mellitus"[MeSH Terms]</To>
        </Translation>
    </TranslationSet>
</eSearchResult>"""
