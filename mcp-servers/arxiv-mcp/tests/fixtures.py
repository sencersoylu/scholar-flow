"""Shared test constants for arXiv MCP server tests."""

SAMPLE_ARXIV_RESPONSE = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:opensearch="http://a9.com/-/spec/opensearch/1.1/"
      xmlns:arxiv="http://arxiv.org/schemas/atom">
  <opensearch:totalResults>150</opensearch:totalResults>
  <opensearch:startIndex>0</opensearch:startIndex>
  <opensearch:itemsPerPage>2</opensearch:itemsPerPage>
  <entry>
    <id>http://arxiv.org/abs/2401.12345v2</id>
    <updated>2024-02-01T00:00:00Z</updated>
    <published>2024-01-15T00:00:00Z</published>
    <title>Attention Is All You Need Revisited</title>
    <summary>We revisit the transformer architecture and propose improvements.</summary>
    <author><name>John Smith</name></author>
    <author><name>Alice Doe</name></author>
    <arxiv:doi>10.1234/example</arxiv:doi>
    <link href="http://arxiv.org/abs/2401.12345v2" rel="alternate" type="text/html"/>
    <link href="http://arxiv.org/pdf/2401.12345v2" title="pdf" rel="related" type="application/pdf"/>
    <arxiv:primary_category term="cs.CL"/>
    <category term="cs.CL"/>
    <category term="cs.AI"/>
  </entry>
</feed>"""

SAMPLE_ARXIV_SINGLE = """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:arxiv="http://arxiv.org/schemas/atom">
  <entry>
    <id>http://arxiv.org/abs/2401.12345v2</id>
    <updated>2024-02-01T00:00:00Z</updated>
    <published>2024-01-15T00:00:00Z</published>
    <title>Attention Is All You Need Revisited</title>
    <summary>We revisit the transformer architecture and propose improvements.</summary>
    <author><name>John Smith</name></author>
    <author><name>Alice Doe</name></author>
    <arxiv:doi>10.1234/example</arxiv:doi>
    <link href="http://arxiv.org/abs/2401.12345v2" rel="alternate" type="text/html"/>
    <link href="http://arxiv.org/pdf/2401.12345v2" title="pdf" rel="related" type="application/pdf"/>
    <category term="cs.CL"/>
    <category term="cs.AI"/>
  </entry>
</feed>"""
