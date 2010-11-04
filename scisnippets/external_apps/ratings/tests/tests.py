from django.contrib.auth.models import User
from django.template import Template, Context
from django.test import TestCase

from ratings.models import RatedItem
from ratings.tests.models import Food, Beverage, BeverageRating
from ratings.utils import sim_euclidean_distance, sim_pearson_correlation, top_matches, recommendations, calculate_similar_items, recommended_items


class RatingsTestCase(TestCase):
    fixtures = ['ratings_testdata.json']
    
    rated_model = Food
    rating_model = RatedItem
    
    def setUp(self):
        self.item1 = self.rated_model.objects.get(pk=1)
        self.item2 = self.rated_model.objects.get(pk=2)
        
        self.john = User.objects.get(username='john')
        self.jane = User.objects.get(username='jane')
        
        self.related_name = self.rating_model.user.field.related_query_name()

    def _sort_by_pk(self, list_or_qs):
        # decorate, sort, undecorate using the pk of the items
        # in the list or queryset
        annotated = [(item.pk, item) for item in list_or_qs]
        annotated.sort()
        return map(lambda item_tuple: item_tuple[1], annotated)
    
    def assertQuerySetEqual(self, a, b):
        # assert list or queryset a is the same as list or queryset b
        return self.assertEqual(self._sort_by_pk(a), self._sort_by_pk(b))

    def test_add(self):
        rating = self.rating_model(user=self.john, score=1)
        self.item1.ratings.add(rating)
        
        # make sure the item1 rating got added
        self.assertEqual(self.item1.ratings.count(), 1)
        
        # get the rating and check that it saved correctly
        item_rating = self.item1.ratings.all()[0]
        self.assertTrue(unicode(item_rating).endswith(' rated 1.0 by john'))
        
        # get the rating another way and check that it works
        user_manager = getattr(self.john, self.related_name)
        item_rating_alt = user_manager.all()[0]
        self.assertEqual(item_rating, item_rating_alt)

        rating2 = self.rating_model(user=self.john, score=-1)
        self.item2.ratings.add(rating2)
        
        # check that the item2 rating got added and that our apple rating is ok
        self.assertEqual(self.item2.ratings.count(), 1)
        self.assertEqual(self.item1.ratings.count(), 1)

        self.assertEqual(user_manager.count(), 2)
    
    def test_remove(self):
        rating = self.rating_model(user=self.john, score=1)
        self.item1.ratings.add(rating)
        
        rating2 = self.rating_model(user=self.jane, score=-1)
        self.item1.ratings.add(rating2)
        
        rating3 = self.rating_model(user=self.john, score=-1)
        self.item2.ratings.add(rating3)
        
        # check to see that john's item1 rating gets removed
        self.item1.ratings.remove(rating)
        self.assertEqual(self.item1.ratings.count(), 1)
        self.assertEqual(self.item1.ratings.all()[0], rating2)
        
        # make sure the item2's rating is still intact
        self.assertEqual(self.item2.ratings.count(), 1)
        
        # trying to remove the item2 rating from the item1 doesn't work
        self.assertRaises(self.rating_model.DoesNotExist, self.item1.ratings.remove, rating3)
        self.assertEqual(self.item2.ratings.count(), 1)
    
    def test_clear(self):
        rating = self.rating_model(user=self.john, score=1)
        self.item1.ratings.add(rating)
        
        rating2 = self.rating_model(user=self.jane, score=-1)
        self.item1.ratings.add(rating2)
        
        rating3 = self.rating_model(user=self.john, score=-1)
        self.item2.ratings.add(rating3)
        
        # check to see that we can clear item1's ratings
        self.item1.ratings.clear()
        self.assertEqual(self.item1.ratings.count(), 0)
        self.assertEqual(self.item2.ratings.count(), 1)
    
    def test_rate_method(self):
        rating1 = self.item1.ratings.rate(self.john, 1)
        rating2 = self.item1.ratings.rate(self.jane, -1)
        rating3 = self.item2.ratings.rate(self.john, -1)
        
        self.assertQuerySetEqual(self.item1.ratings.all(), [rating1, rating2])
        self.assertQuerySetEqual(self.item2.ratings.all(), [rating3])
        
        self.assertEqual(rating1.content_object, self.item1)
        self.assertEqual(rating2.content_object, self.item1)
        self.assertEqual(rating3.content_object, self.item2)
        
        rating1_alt = self.item1.ratings.rate(self.john, 1000000)
        
        # get_or_create'd the rating based on user, so count stays the same
        self.assertEqual(self.item1.ratings.count(), 2)
        self.assertEqual(rating1.pk, rating1_alt.pk)
        self.assertEqual(rating1_alt.score, 1000000)
    
    def test_scoring(self):
        rating1 = self.item1.ratings.rate(self.john, 1)
        rating2 = self.item1.ratings.rate(self.jane, -1)
        rating3 = self.item2.ratings.rate(self.john, -1)
        
        self.assertEqual(self.item1.ratings.cumulative_score(), 0)
        self.assertEqual(self.item1.ratings.average_score(), 0)
        
        self.item1.ratings.rate(self.john, 10)
        self.assertEqual(self.item1.ratings.cumulative_score(), 9)
        self.assertEqual(self.item1.ratings.average_score(), 4.5)
    
    def test_all(self):
        rating = self.rating_model(user=self.john, score=1)
        self.item1.ratings.add(rating)
        
        rating2 = self.rating_model(user=self.jane, score=-1)
        self.item1.ratings.add(rating2)
        
        rating3 = self.rating_model(user=self.john, score=-1)
        self.item2.ratings.add(rating3)
        
        self.assertQuerySetEqual(self.item1.ratings.all(), [rating, rating2])
        self.assertQuerySetEqual(self.item2.ratings.all(), [rating3])
        self.assertQuerySetEqual(self.rated_model.ratings.all(), [rating, rating2, rating3])
    
    def test_filtering(self):
        john_rating_1 = self.rating_model(user=self.john, score=1)
        self.item1.ratings.add(john_rating_1)
        
        john_rating_2 = self.rating_model(user=self.john, score=2)
        self.item2.ratings.add(john_rating_2)
        
        jane_rating_1 = self.rating_model(user=self.jane, score=2)
        self.item1.ratings.add(jane_rating_1)

        rated_qs = self.rated_model.ratings.filter(user=self.john)
        self.assertQuerySetEqual(rated_qs, [john_rating_2, john_rating_1])

        rated_qs = self.rated_model.ratings.filter(user=self.john).order_by_rating()
        self.assertQuerySetEqual(rated_qs, [self.item2, self.item1])
        self.assertEqual(rated_qs[0].score, 2.0)
        self.assertEqual(rated_qs[1].score, 1.0)
    
    def test_ordering(self):
        rating1 = self.item1.ratings.rate(self.john, 1)
        rating2 = self.item1.ratings.rate(self.jane, -1)
        rating3 = self.item2.ratings.rate(self.john, 1)
        
        rated_qs = self.rated_model.ratings.all().order_by_rating()
        self.assertQuerySetEqual(rated_qs, [self.item2, self.item1])
        self.assertQuerySetEqual(rated_qs,
            self.rated_model.ratings.order_by_rating()
        )
        
        self.assertEqual(rated_qs[0].score, 1)
        self.assertEqual(rated_qs[1].score, 0)
        
        item1_qs = queryset=self.rated_model._default_manager.filter(pk=self.item1.pk)
        rated_qs = self.rated_model.ratings.all().order_by_rating(queryset=item1_qs)
        self.assertQuerySetEqual(rated_qs, [self.item1])
        self.assertQuerySetEqual(rated_qs,
            self.rated_model.ratings.order_by_rating(queryset=item1_qs)
        )
        
        self.assertEqual(rated_qs[0].score, 0)
        
        rated_qs = self.rated_model.ratings.all().order_by_rating(descending=False, alias='sum_score')
        self.assertQuerySetEqual(rated_qs, [self.item1, self.item2])
        self.assertQuerySetEqual(rated_qs,
            self.rated_model.ratings.order_by_rating(descending=False, alias='sum_score')
        )
        
        self.assertEqual(rated_qs[0].sum_score, 0)
        self.assertEqual(rated_qs[1].sum_score, 1)
        
        self.item1.ratings.rate(self.john, 3)
        rated_qs = self.rated_model.ratings.all().order_by_rating()
        self.assertQuerySetEqual(rated_qs, [self.item1, self.item2])
    
        self.assertEqual(rated_qs[0].score, 2)
        self.assertEqual(rated_qs[1].score, 1)
    
    def test_templatetag(self):
        t = Template('{% load ratings_tags %}{{ obj|rating_score:user }}')
        c = Context({'obj': self.item1, 'user': self.john})
        
        self.assertEqual(t.render(c), 'None')
        
        self.item1.ratings.rate(self.john, 10)
        self.assertEqual(t.render(c), '10.0')


class CustomModelRatingsTestCase(RatingsTestCase):
    rated_model = Beverage
    rating_model = BeverageRating


class RecommendationsTestCase(TestCase):
    fixtures = ['ratings_testdata.json']
    
    def setUp(self):
        super(RecommendationsTestCase, self).setUp()
        
        self.food_a = Food.objects.create(name='food_a')
        self.food_b = Food.objects.create(name='food_b')
        self.food_c = Food.objects.create(name='food_c')
        self.food_d = Food.objects.create(name='food_d')
        self.food_e = Food.objects.create(name='food_e')
        self.food_f = Food.objects.create(name='food_f')
        
        self.user_a = User.objects.create_user('user_a', 'user_a')
        self.user_b = User.objects.create_user('user_b', 'user_b')
        self.user_c = User.objects.create_user('user_c', 'user_c')
        self.user_d = User.objects.create_user('user_d', 'user_d')
        self.user_e = User.objects.create_user('user_e', 'user_e')
        self.user_f = User.objects.create_user('user_f', 'user_f')
        self.user_g = User.objects.create_user('user_g', 'user_g')
        
        ratings_matrix = [
            # a    b    c    d    e    f
            [2.5, 3.5, 3.0, 3.5, 2.5, 3.0],
            [3.0, 3.5, 1.5, 5.0, 3.5, 3.0],
            [2.5, 3.0, None, 3.5, None, 4.0],
            [None, 3.5, 3.0, 4.0, 2.5, 4.5],
            [3.0, 4.0, 2.0, 3.0, 2.0, 3.0],
            [3.0, 4.0, None, 5.0, 3.5, 3.0],
            [None, 4.5, None, 4.0, 1.0, None]
        ]
        
        # x-axis
        self.foods = [
            self.food_a, self.food_b, self.food_c,
            self.food_d, self.food_e, self.food_f
        ]
        
        # y-axis
        self.users = [
            self.user_a, self.user_b, self.user_c,
            self.user_d, self.user_e, self.user_f,
            self.user_g
        ]

        for x, food in enumerate(self.foods):
            for y, user in enumerate(self.users):
                if ratings_matrix[y][x]:
                    food.ratings.rate(user, ratings_matrix[y][x])

    def test_simple(self):
        result = sim_euclidean_distance(RatedItem.objects.all(), self.user_a, self.user_b)
        self.assertEqual(str(result)[:5], '0.148')
        
        result = sim_pearson_correlation(RatedItem.objects.all(), self.user_a, self.user_b)
        self.assertEqual(str(result)[:5], '0.396')
    
    def test_matching(self):
        results = top_matches(RatedItem.objects.all(), self.users, self.user_g, 3)
        self.assertEqual(str(results), '[(0.99124070716192991, <User: user_a>), (0.92447345164190486, <User: user_e>), (0.89340514744156474, <User: user_d>)]')
    
    def test_recommending(self):
        results = recommendations(RatedItem.objects.all(), self.users, self.user_g)
        self.assertEqual(str(results), '[(3.3477895267131017, <Food: food_f>), (2.8325499182641614, <Food: food_a>), (2.5309807037655649, <Food: food_c>)]')
        
        results = recommendations(RatedItem.objects.all(), self.users, self.user_c)
        self.assertEqual(str(results), '[(2.8092760065251268, <Food: food_c>), (2.6946367039803629, <Food: food_e>)]')
    
    def test_item_recommendation(self):
        results = top_matches(RatedItem.objects.all(), self.foods, self.food_d)
        self.assertEqual(str(results), '[(0.65795169495976946, <Food: food_e>), (0.48795003647426888, <Food: food_a>), (0.11180339887498941, <Food: food_b>), (-0.17984719479905439, <Food: food_f>), (-0.42289003161103106, <Food: food_c>)]')

    def test_similar_items(self):
        calculate_similar_items(RatedItem.objects.all(), 10)
        top_for_food_a = self.food_a.ratings.similar_items()[0]
        
        self.assertEqual(top_for_food_a.similar_object, self.food_b)
        
        top_for_food_b = self.food_b.ratings.similar_items()[0]
        self.assertEqual(top_for_food_b.similar_object, self.food_a)
        
        self.assertEqual(top_for_food_a.score, top_for_food_b.score)
        
        Food.ratings.update_similar_items()
        
        other_for_food_a = self.food_a.ratings.similar_items()[0]
        self.assertEqual(top_for_food_a, other_for_food_a)
    
    def test_recommended_items(self):
        calculate_similar_items(RatedItem.objects.all())
        # failure
        result = recommended_items(RatedItem.objects.all(), self.user_g)
        r1, r2, r3 = result
        self.assertEqual(str(r1[0])[:5], '3.610')
        self.assertEqual(r1[1], self.food_a)
        
        self.assertEqual(str(r2[0])[:5], '3.531')
        self.assertEqual(r2[1], self.food_f)
        
        self.assertEqual(str(r3[0])[:5], '2.960')
        self.assertEqual(r3[1], self.food_c)
    
        result = recommended_items(RatedItem.objects.all(), self.user_c)
        r1, r2 = result
        
        self.assertEqual(str(r1[0])[:5], '2.287')
        self.assertEqual(r1[1], self.food_c)
        
        self.assertEqual(str(r2[0])[:5], '2.084')
        self.assertEqual(r2[1], self.food_e)
