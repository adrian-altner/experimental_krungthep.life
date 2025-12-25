from django.core.exceptions import ValidationError
from django.test import RequestFactory, TestCase
from wagtail.models import Page

from home.models import HomePage
from poi.models import POICategory, POIFeature, POIIndexPage, POIPage


class POIAppTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.root = Page.get_first_root_node()
        self.home = HomePage(title="Home", slug="home")
        self.root.add_child(instance=self.home)
        self.home.save_revision().publish()

        self.index = POIIndexPage(title="Places", slug="places")
        self.home.add_child(instance=self.index)
        self.index.save_revision().publish()

        self.category_food = POICategory.objects.create(title="Restaurant", slug="restaurant")
        self.category_cafe = POICategory.objects.create(title="Cafe", slug="cafe")
        self.feature_wifi = POIFeature.objects.create(title="WiFi", slug="wifi")

    def _create_poi(self, title, category, **kwargs):
        page = POIPage(
            title=title,
            slug=title.lower().replace(" ", "-"),
            category=category,
            short_description="Short description",
            **kwargs,
        )
        self.index.add_child(instance=page)
        return page

    def test_page_type_restrictions(self):
        self.assertTrue(POIIndexPage.can_create_at(self.home))
        self.assertFalse(POIPage.can_create_at(self.home))
        self.assertTrue(POIPage.can_create_at(self.index))

    def test_snippets_can_be_created(self):
        self.assertEqual(POICategory.objects.count(), 2)
        self.assertEqual(POIFeature.objects.count(), 1)

    def test_filtering_by_category_and_feature(self):
        poi_one = self._create_poi("One", self.category_food)
        poi_one.features.add(self.feature_wifi)
        poi_one.save_revision().publish()

        poi_two = self._create_poi("Two", self.category_cafe)
        poi_two.save_revision().publish()

        request = self.factory.get(
            "/places/",
            {"category": str(self.category_food.id), "feature": ["wifi"]},
        )
        request.site = None
        context = self.index.get_context(request)
        pois = list(context["pois"])

        self.assertEqual(len(pois), 1)
        self.assertEqual(pois[0].title, "One")

    def test_category_filter_context(self):
        poi_one = self._create_poi("One", self.category_food)
        poi_one.save_revision().publish()
        poi_two = self._create_poi("Two", self.category_cafe)
        poi_two.save_revision().publish()

        request = self.factory.get("/places/", {"category": str(self.category_food.id)})
        request.site = None
        context = self.index.get_context(request)
        pois = list(context["pois"])

        self.assertEqual(len(pois), 1)
        self.assertEqual(pois[0].title, "One")

    def test_index_category_lock(self):
        self.index.category = self.category_food
        self.index.save_revision().publish()

        poi_one = self._create_poi("One", self.category_food)
        poi_one.save_revision().publish()

        poi_two = self._create_poi("Two", self.category_cafe)
        poi_two.save_revision().publish()

        request = self.factory.get("/places/")
        request.site = None
        context = self.index.get_context(request)
        pois = list(context["pois"])

        self.assertEqual(len(pois), 1)
        self.assertEqual(pois[0].title, "One")

    def test_category_unique_for_index(self):
        self.index.category = self.category_food
        self.index.full_clean()
        self.index.save_revision().publish()

        other_index = POIIndexPage(title="Other", slug="other")
        self.home.add_child(instance=other_index)
        other_index.category = self.category_food
        with self.assertRaises(ValidationError):
            other_index.full_clean()
    def test_map_data_includes_coordinates_only(self):
        poi_with_coords = self._create_poi(
            "With coords",
            self.category_food,
            latitude=13.7563,
            longitude=100.5018,
        )
        poi_with_coords.save_revision().publish()

        poi_without_coords = self._create_poi("No coords", self.category_food)
        poi_without_coords.save_revision().publish()

        request = self.factory.get("/places/")
        request.site = None
        context = self.index.get_context(request)
        map_pois = context["map_pois"]

        self.assertEqual(len(map_pois), 1)
        self.assertEqual(map_pois[0]["title"], "With coords")
