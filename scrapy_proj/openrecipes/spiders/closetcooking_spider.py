from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
from openrecipes.items import RecipeItem, RecipeItemLoader
import re


class ClosetcookingMixin(object):
    source = 'closetcooking'

    def parse_item(self, response):

        hxs = HtmlXPathSelector(response)

        base_path = '//*[@class="hrecipe"]'

        recipes_scopes = hxs.select(base_path)

        name_path = '//*[@class="post-title"]/a/text()'
        image_path = '//*[@class="photo"]/@src'
        recipeYield_path = '//*[@class="serving_size yield"]/text()'
        cookTime_path = '//div[2]/span[@class="cookTime"]/span/@title'
        prepTime_path = '//div[2]/span[@class="prepTime"]/span/@title'
        ingredients_path = '//div[1][@class="ingredient"]/text()'

        recipes = []

        label_regex = re.compile(r'^For ')

        for r_scope in recipes_scopes:
            il = RecipeItemLoader(item=RecipeItem())

            il.add_value('source', self.source)

            il.add_value('name', r_scope.select(name_path).extract())
            il.add_value('image', r_scope.select(image_path).extract())
            il.add_value('url', response.url)

            il.add_value('prepTime', r_scope.select(prepTime_path).extract())
            il.add_value('cookTime', r_scope.select(cookTime_path).extract())
            il.add_value('recipeYield', r_scope.select(recipeYield_path).extract())

            ingredient_scopes = r_scope.select(ingredients_path)
            ingredients = []
            for i_scope in ingredient_scopes:
                ingredient = i_scope.extract().strip()
                if not label_regex.match(ingredient) and not ingredient.endswith(':'):
                    ingredients.append(ingredient)
            il.add_value('ingredients', ingredients)

            recipes.append(il.load_item())

        return recipes


class ClosetcookingcrawlSpider(CrawlSpider, ClosetcookingMixin):

    name = "closetcooking.com"

    allowed_domains = ["closetcooking.com"]

    start_urls = [
        "http://www.closetcooking.com/p/recipe-index.html?label=Recipe",
    ]

    rules = (

        Rule(SgmlLinkExtractor(allow=('\/\d\d\d\d\/\d\d\/[a-zA-Z_]+.html')),
             callback='parse_item'),
    )
