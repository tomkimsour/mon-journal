def make_paper(
    arxiv_id,
    title="A paper",
    abstract="",
    subjects="Robotics (cs.RO)",
    primary_cat="cs.RO",
    section="new",
    authors=None,
    **extra,
):
    authors = authors if authors is not None else ["Ada Lovelace", "Alan Turing"]
    paper = {
        "arxiv_id": arxiv_id,
        "title": title,
        "authors": authors,
        "subjects": subjects,
        "primary_cat": primary_cat,
        "section": section,
        "abstract": abstract,
    }
    paper.update(extra)
    return paper


def make_listing(category, papers, date="2026-10-06"):
    return {"category": category, "date": date, "papers": papers}
