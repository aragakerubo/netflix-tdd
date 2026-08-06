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


def test_visitor_opens_a_title_detail_page(live_server, page):
    from catalog.models import Title

    Title.objects.create(
        name="The Matrix",
        year=1999,
        description="A hacker learns the truth.",
        runtime=136,
        rating="8.7",
    )

    page.goto(live_server.url)
    page.get_by_role("link", name="The Matrix").click()

    page.get_by_role("heading", name="The Matrix (1999)").wait_for()
    page.get_by_text("A hacker learns the truth.").wait_for()


def test_visitor_browses_a_genre_from_a_title(live_server, page):
    from catalog.models import Genre, Title

    action = Genre.objects.create(name="Action")
    matrix = Title.objects.create(
        name="The Matrix",
        year=1999,
        description="A hacker learns the truth.",
        runtime=136,
        rating="8.7",
    )
    matrix.genres.add(action)

    page.goto(live_server.url + matrix.get_absolute_url())
    page.get_by_role("link", name="Action").click()

    page.get_by_role("heading", name="Action").wait_for()
    page.get_by_text("The Matrix").wait_for()
