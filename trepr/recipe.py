import aspecd.tasks
import trepr.io
import aspecd.io
import trepr.dataset

dataset_factory_ = trepr.dataset.DatasetFactory()
recipe = aspecd.tasks.Recipe()
recipe.dataset_factory = dataset_factory_
recipe_importer = aspecd.io.RecipeYamlImporter('/home/jara/Dokumente/python/trepr/trepr/recipe.yaml')
recipe_importer.import_into(recipe)
chef = aspecd.tasks.Chef(recipe)
chef.cook()
