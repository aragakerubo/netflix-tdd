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


def test_editor_adds_a_title_through_the_admin(live_server, page, django_user_model):
    django_user_model.objects.create_superuser(username="editor", password="pass12345")

    # Sign in to the Django admin.
    page.goto(live_server.url + "/admin/")
    page.get_by_label("Username:").fill("editor")
    page.get_by_label("Password:").fill("pass12345")
    page.get_by_role("button", name="Log in").click()

    # Add a title.
    page.goto(live_server.url + "/admin/catalog/title/add/")
    page.get_by_label("Name:").fill("The Matrix")
    page.get_by_role("button", name="Save", exact=True).click()

    # It now appears on the public home page.
    page.goto(live_server.url)
    page.get_by_role("link", name="The Matrix").wait_for()


def test_visitor_logs_in_and_sees_a_logout_control(
    live_server, page, django_user_model
):
    django_user_model.objects.create_user(username="cinephile", password="pass12345")

    page.goto(live_server.url + "/accounts/login/")
    page.get_by_label("Username:").fill("cinephile")
    page.get_by_label("Password:").fill("pass12345")
    page.get_by_role("button", name="Log in").click()

    # Back on the site, the header now offers a way out.
    page.get_by_role("button", name="Log out").wait_for()


def test_visitor_plays_a_trailer_from_the_detail_page(live_server, page):
    from catalog.models import Title

    matrix = Title.objects.create(
        name="The Matrix",
        year=1999,
        description="A hacker learns the truth.",
        trailer_key="trailer456",
    )

    page.goto(live_server.url + matrix.get_absolute_url())
    page.get_by_role("link", name="Play trailer").click()

    # The player page loads with the embedded video.
    page.wait_for_url("**/watch/")
    player = page.locator("iframe")
    player.wait_for()


def test_user_saves_a_title_to_their_list(live_server, page, django_user_model):
    from catalog.models import Title

    django_user_model.objects.create_user(username="saver", password="pass12345")
    matrix = Title.objects.create(name="The Matrix", year=1999)

    page.goto(live_server.url + "/accounts/login/")
    page.get_by_label("Username:").fill("saver")
    page.get_by_label("Password:").fill("pass12345")
    page.get_by_role("button", name="Log in").click()

    page.goto(live_server.url + matrix.get_absolute_url())
    page.get_by_role("button", name="Add to My List").click()

    # The button flips to remove, and the title shows on My List.
    page.get_by_role("button", name="Remove from My List").wait_for()
    page.get_by_role("link", name="My List").click()
    page.get_by_role("link", name="The Matrix").wait_for()
