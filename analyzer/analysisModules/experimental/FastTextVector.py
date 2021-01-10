import fasttext.util
fasttext.util.download_model('de', if_exists='ignore')  # English
ft = fasttext.load_model('cc.de.300.bin')

ft.get_word_vector('hello').shape(100,)
ft.get_nearest_neighbors('hello')


"""
ft.get_dimension()
fasttext.util.reduce_model(ft, 100)
ft.get_dimension()
"""
