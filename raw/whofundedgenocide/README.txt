THE ENTIRE NETWORK - the data behind the map
==========================================
Edition 1

Three tables. Between them they are the map itself rather than a summary of it: the same
9,979 entities and 13,464 links the page draws across 7 boards, resting on 83 source records,
each row carrying the citation it comes from, so that anything here can be taken back to
the register it came from. The same rows come as one JSON document and as a node/edge
pair that Gephi and Cytoscape open without being told anything.

  LICENCE.txt                             1 KB
  datapackage.json                        5 KB
  gephi-edges.csv                       1.9 MB
  gephi-nodes.csv                       1.3 MB
  the-entire-network-entities.csv       3.0 MB
  the-entire-network-links.csv          3.0 MB
  the-entire-network-sources.csv         21 KB
  the-entire-network.json              10.5 MB

Three more files complete the set and are not sized above, because they are written
after it: this README, SHA256SUMS.txt, and the-entire-network.zip, which holds every
file listed here and is the one download to take if you want all of it.

Every CSV here is UTF-8 and begins with a byte-order mark, so that a double-click opens
it correctly in Excel on Windows: without it the Hebrew and the accented names arrive
mangled. Anything else reading these files should open them as utf-8-sig, or simply skip
the first three bytes.

the-entire-network-entities.csv
  One row per entity on the map.
    board, board_title    which board it is on
    column_number, column where it sits in the order the money travels
    entity_id             its id on that board; the address .../map/#<board>/<entity_id>
                          opens it
    kind                  what the board calls that kind of entity
    name, subtitle        as drawn
    what_the_record_says  the sentence the panel shows
    source_ids            space separated, and they resolve in the sources table
    source_urls           the entity's own links, where it has any

the-entire-network-links.csv
  One row per line on the map.
    from_entity_id, to_entity_id  join to the entities table
    what_the_line_says          the class of line, in the board's own words
    money_or_not                "money" where an amount is stated
    measure                     what the record says happened: received, ordered,
                                contracted, a ceiling approved, and so on
    amount_as_filed             as the record states it, with its symbol
    amount                      the same figure as a number
    currency                    its own column, because no two currencies on this map
                                are ever added together and no exchange rate appears in
                                any of these records
    period, label, detail       as the panel shows them
    source_ids                  space separated

the-entire-network-sources.csv
  One row per source cited, per board.
    url        the original, on the issuing authority's own server
    locator    the item, page or reference within it
    sha256     of our copy, where we hold one
    our_copy   the full address of that copy on this site

What these tables do NOT contain
--------------------------------
A ceiling is a maximum that was approved, not money shown to have been spent. An order
is not a payment. A line between two entities is a record that names them together; it is
not an allegation about either. Independent expenditures in the United States are made
by law without coordination with the candidate, and money spent against a candidate is
money spent on advertising, not money the candidate received. A lobbying register
records that a communication took place, not what was said.

Where a register names an organisation but not where its money went, there is an entity
and no link out of it, and the entity says so.

Where a table holds thousands of rows, the large ones are entities of their own and the
rest are counted together in one entity whose own row says how many. The two always add
back up to the published total.

Names of donors, registrants and office holders are reproduced as the public registers
record them, and the websites those registers hold. Where a register writes a name
entirely in capitals, the capitals are lowered so the name can be read - BANKMAN-FRIED
becomes Bankman-Fried - and nothing else about the spelling is touched. A name already
filed in mixed case is left exactly as filed.

Licence
-------
Creative Commons Attribution 4.0 International
https://creativecommons.org/licenses/by/4.0/
See LICENCE.txt. Credit it like this:

  "The Entire Network." Who Funded Genocide. https://whofundedgenocide.com/map/
  Licensed CC BY 4.0. Research in collaboration with Wallface.

Check a file by comparing its SHA-256 with SHA256SUMS.txt:

  sha256sum -c SHA256SUMS.txt          (Linux, macOS, Git Bash)
  Get-FileHash <file> -Algorithm SHA256   (Windows PowerShell)
