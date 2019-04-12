import aspecd.tasks
import trepr.io
import aspecd.io

dataset_factory_ = trepr.io.DatasetImporterFactory()
recipe = aspecd.tasks.Recipe()
recipe.dataset_factory = dataset_factory_
importer = aspecd.io.RecipeYamlImporter('/home/jara/Dokumente/python/trepr/trepr/recipe.yaml')
importer.import_into(recipe)
chef = aspecd.tasks.Chef(recipe)
chef.cook()