from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
from openrecipes.items import RecipeItem, RecipeItemLoader


class Leitesculinaria_spiderMixin(object):
    source = 'leitesculinaria_spider'

    def parse_item(self, response):

        hxs = HtmlXPathSelector(response)

        base_path = '//*[@itemtype="http://schema.org/Recipe"]'

        recipes_scopes = hxs.select(base_path)

        name_path = '//*[@class="recipe-title"]/text()'
        #  not sure how to get the description consistently on this one.
        #description_path = 'TODO'
        image_path = '//*[@itemprop="image"]/@src'
        prepTime_path = '//*[@class="prep-time tooltip-element"]/number()'
        cookTime_path = '//*[@class="total-time tooltip-element"]/text()'
        recipeYield_path = '//*[@itemprop="recipeYield"]/text()'
        #may have to make ingredients more generic
        ingredients_path = '//*[@class="ingredients-list"]/ul'
        datePublished = '//*[@class="date published time"]/text()'

        recipes = []

        for r_scope in recipes_scopes:
            il = RecipeItemLoader(item=RecipeItem())

            il.add_value('source', self.source)

            il.add_value('name', r_scope.select(name_path).extract())
            il.add_value('image', r_scope.select(image_path).extract())
            il.add_value('url', response.url)
            #il.add_value('description', r_scope.select(description_path).extract())

            il.add_value('prepTime', r_scope.select(prepTime_path).extract())
            il.add_value('cookTime', r_scope.select(cookTime_path).extract())
            il.add_value('recipeYield', r_scope.select(recipeYield_path).extract())

            ingredient_scopes = r_scope.select(ingredients_path)
            ingredients = []
            for i_scope in ingredient_scopes:
                amount = i_scope.select('//*[@class="ingredient-n"]/text()').extract()
                ingredient_unit = i_scope.select('*//*[@class="ingredient-unit"]/text()').extract()
                name = i_scope.select('//*[@class="ingredient-name"]/text()').extract()
                amount = "".join(amount).strip()
                ingredient_unit = "".join(ingredient_unit).strip()
                name = "".join(name).strip()
                ingredients.append("%s %s" % (amount, ingredient_unit, name))
            il.add_value('ingredients', ingredients)

            il.add_value('datePublished', r_scope.select(datePublished).extract())

            recipes.append(il.load_item())

        return recipes


class Leitesculinaria_spidercrawlSpider(CrawlSpider, Leitesculinaria_spiderMixin):

    name = "www.leitesculinaria.com"

    allowed_domains = ["www.leitesculinaria.com"]

    start_urls = [
        "www.leitesculinaria.com/category/recipes",
    ]

    rules = (
        Rule(SgmlLinkExtractor(allow=('/category/recipes/page\/d+'))),

        Rule(SgmlLinkExtractor(allow=('\/d+\/.+')),
             callback='parse_item'),
    )
