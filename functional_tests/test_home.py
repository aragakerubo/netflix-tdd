def test_visitor_searches_for_a_title(live_server, page):
    # live_server provides a transactional DB, so rows created here through the
    # ORM are visible to the server thread that Playwright drives.
    from catalog.models import Title

    Title.objects.create(name="The Matrix", year=1999)
    Title.objects.create(name="Inception", year=2010)

    page.goto(live_server.url)
    page.get_by_placeholder("Search titles").fill("matrix")
    page.get_by_role("button", name="Search").click()

    # The matching title appears and the other one does not.
    page.get_by_text("The Matrix").wait_for()
    assert page.get_by_text("Inception").count() == 0
